import pickle
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import os
import random
from collections import defaultdict
from .models import Profile, PreferenceWeights, Feedback, CachedRecommendations, WatchEvent, SavedList

class MovieRecommender:
    def __init__(self):
        self.movies_df = None
        self.vectorizer = None
        self.count_matrix = None
        self._load_models()

    def _load_models(self):
        """Load the ML models from the models directory."""
        models_dir = os.path.join(settings.BASE_DIR, 'models')

        # Load processed movies
        with open(os.path.join(models_dir, 'processed_movies.pkl'), 'rb') as f:
            self.movies_df = pickle.load(f)

        # Load vectorizer
        with open(os.path.join(models_dir, 'count_vectorizer.pkl'), 'rb') as f:
            self.vectorizer = pickle.load(f)

        # Load count matrix
        matrix_data = np.load(os.path.join(models_dir, 'count_matrix.npz'))
        self.count_matrix = csr_matrix(
            (matrix_data['data'], matrix_data['indices'], matrix_data['indptr']),
            shape=matrix_data['shape']
        )

    def load_local_artifacts(self):
        """Load all local ML artifacts."""
        return self._load_models()

    def rank_with_hybrid(self, movie_ids, alpha=0.7, popularity_fn=None):
        """
        Rank movies using hybrid scoring: alpha*cosine_similarity + (1-alpha)*popularity_score.

        Args:
            movie_ids: List of movie IDs to rank
            alpha: Weight for similarity (0-1)
            popularity_fn: Function to compute popularity score from vote_avg and vote_count

        Returns:
            List of (movie_id, score) tuples sorted by score descending
        """
        if not movie_ids:
            return []

        if popularity_fn is None:
            popularity_fn = lambda avg, count: (avg * min(count, 1000)) / 1000  # Simple popularity

        scores = []
        for movie_id in movie_ids:
            if movie_id not in self.movies_df['id'].values:
                continue

            movie_idx = self.movies_df[self.movies_df['id'] == movie_id].index[0]
            movie_data = self.movies_df.iloc[movie_idx]

            # Get cosine similarity to query (assuming first movie is query)
            if len(movie_ids) > 1:
                query_idx = self.movies_df[self.movies_df['id'] == movie_ids[0]].index[0]
                cos_sim = cosine_similarity(self.count_matrix[query_idx], self.count_matrix[movie_idx]).flatten()[0]
            else:
                cos_sim = 1.0  # Self-similarity

            pop_score = popularity_fn(movie_data['vote_average'], movie_data['vote_count'])
            hybrid_score = alpha * cos_sim + (1 - alpha) * pop_score

            scores.append((movie_id, hybrid_score))

        return sorted(scores, key=lambda x: x[1], reverse=True)

    def rerank_for_diversity(self, items, lambda_diversity=0.1):
        """
        Apply diversity penalty to reduce near-duplicates.

        Args:
            items: List of (movie_id, score) tuples
            lambda_diversity: Diversity penalty weight

        Returns:
            Reranked list with diversity penalty applied
        """
        if not items:
            return items

        # Simple diversity based on genre overlap
        reranked = []
        used_genres = set()

        for movie_id, score in items:
            movie_data = self.movies_df[self.movies_df['id'] == movie_id].iloc[0]
            genres = set(movie_data['genres']) if isinstance(movie_data['genres'], list) else set()

            # Penalty for genre overlap
            overlap_penalty = len(genres & used_genres) * lambda_diversity
            adjusted_score = score - overlap_penalty

            reranked.append((movie_id, adjusted_score))
            used_genres.update(genres)

        return sorted(reranked, key=lambda x: x[1], reverse=True)

    def session_rerank(self, items, session_signals):
        """
        Re-rank based on session signals (recent clicks, dwell time).

        Args:
            items: List of (movie_id, score) tuples
            session_signals: Dict with 'recent_clicks', 'dwell_times'

        Returns:
            Reranked items
        """
        if not session_signals:
            return items

        recent_clicks = session_signals.get('recent_clicks', [])
        dwell_times = session_signals.get('dwell_times', {})

        boosted = []
        for movie_id, score in items:
            boost = 0

            # Boost recently clicked movies
            if movie_id in recent_clicks:
                boost += 0.2

            # Boost based on dwell time
            dwell = dwell_times.get(movie_id, 0)
            if dwell > 30:  # 30 seconds
                boost += 0.1

            boosted.append((movie_id, score + boost))

        return sorted(boosted, key=lambda x: x[1], reverse=True)

    def explain(self, item_id, profile_id):
        """
        Generate explanation badges and confidence for a recommendation.

        Args:
            item_id: Movie ID
            profile_id: Profile ID

        Returns:
            Dict with 'badges' list and 'confidence' score
        """
        badges = []
        confidence = 0.5  # Base confidence

        try:
            profile = Profile.objects.get(id=profile_id)
            movie = self.movies_df[self.movies_df['id'] == item_id].iloc[0]

            # Check ratings history for "because you liked"
            ratings = profile.userrating_set.filter(rating__gte=4).values_list('movie__tmdb_id', flat=True)
            if ratings:
                # Find similar movies to highly rated ones
                for rated_id in ratings[:5]:  # Check last 5 ratings
                    if rated_id in self.movies_df['id'].values:
                        rated_idx = self.movies_df[self.movies_df['id'] == rated_id].index[0]
                        item_idx = self.movies_df[self.movies_df['id'] == item_id].index[0]
                        sim = cosine_similarity(self.count_matrix[rated_idx], self.count_matrix[item_idx]).flatten()[0]
                        if sim > 0.3:
                            rated_title = self.movies_df.iloc[rated_idx]['title']
                            badges.append(f"Because you liked {rated_title}")
                            confidence += 0.2
                            break

            # Genre matches
            pref_weights = PreferenceWeights.objects.filter(profile=profile).first()
            if pref_weights and pref_weights.genre_weights:
                top_genres = sorted(pref_weights.genre_weights.items(), key=lambda x: x[1], reverse=True)[:2]
                movie_genres = set(movie['genres']) if isinstance(movie['genres'], list) else set()
                matching = [g for g, w in top_genres if g in movie_genres]
                if matching:
                    badges.append(f"Matches: {', '.join(matching)}")
                    confidence += 0.15

            # Popularity badge
            if movie['vote_average'] > 7.5:
                badges.append("Popular with similar profiles")
                confidence += 0.1

        except Exception as e:
            print(f"Error generating explanation: {e}")

        return {
            'badges': badges[:3],  # Max 3 badges
            'confidence': min(confidence, 1.0)
        }

    def get_recommendations(self, movie_id, num_recommendations=10):
        """Get movie recommendations based on content similarity."""
        if movie_id not in self.movies_df['id'].values:
            return []

        # Find the index of the movie
        movie_idx = self.movies_df[self.movies_df['id'] == movie_id].index[0]

        # Calculate cosine similarity
        cosine_sim = cosine_similarity(self.count_matrix[movie_idx], self.count_matrix).flatten()

        # Get similarity scores
        sim_scores = list(enumerate(cosine_sim))

        # Sort by similarity score (descending)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get top recommendations (excluding the movie itself)
        sim_scores = sim_scores[1:num_recommendations+1]

        # Get movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return recommended movies
        return self.movies_df.iloc[movie_indices][['id', 'title', 'overview', 'genres', 'release_year', 'vote_average']].to_dict('records')

    def get_trending_movies(self, num_movies=20):
        """Get trending/popular movies."""
        # Sort by vote_average and vote_count for trending
        trending = self.movies_df.nlargest(num_movies, ['vote_average', 'vote_count'])
        return trending[['id', 'title', 'overview', 'genres', 'release_year', 'vote_average']].to_dict('records')

    def get_movies_by_genre(self, genre, num_movies=10):
        """Get movies by genre."""
        genre_movies = self.movies_df[self.movies_df['genres'].apply(lambda x: genre.lower() in [g.lower() for g in x] if isinstance(x, list) else False)]
        return genre_movies.nlargest(num_movies, 'vote_average')[['id', 'title', 'overview', 'genres', 'release_year', 'vote_average']].to_dict('records')

    def search_movies(self, query, num_results=10):
        """Search movies by title."""
        query_lower = query.lower()
        matches = self.movies_df[self.movies_df['title'].str.lower().str.contains(query_lower)]
        return matches.nlargest(num_results, 'vote_average')[['id', 'title', 'overview', 'genres', 'release_year', 'vote_average']].to_dict('records')

    def get_personalized_recommendations(self, profile, num_recs=20):
        """
        Get personalized recommendations for a profile.

        Args:
            profile: Profile instance
            num_recs: Number of recommendations

        Returns:
            List of movie dicts with scores, badges, confidence
        """
        # Try cached recommendations first
        cache_key = f"recs_{profile.id}_for_you"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Get highly rated movies for content-based recs
        high_ratings = profile.userrating_set.filter(rating__gte=4).values_list('movie__tmdb_id', flat=True)

        candidates = set()
        for movie_id in high_ratings:
            recs = self.get_recommendations(movie_id, 5)
            candidates.update([r['id'] for r in recs])

        # Remove already rated movies
        rated_ids = set(profile.userrating_set.values_list('movie__tmdb_id', flat=True))
        candidates = candidates - rated_ids

        # Apply feedback filters
        feedback_excludes = set(
            Feedback.objects.filter(
                profile=profile,
                feedback_type__in=['not_interested', 'seen_it', 'show_fewer']
            ).values_list('movie__tmdb_id', flat=True)
        )
        candidates = candidates - feedback_excludes

        if not candidates:
            # Fallback to trending
            trending = self.get_trending_movies(num_recs)
            return [{'movie': m, 'score': 0.5, 'badges': ['Trending'], 'confidence': 0.5} for m in trending]

        # Rank with hybrid scoring
        ranked = self.rank_with_hybrid(list(candidates))

        # Apply diversity
        diverse = self.rerank_for_diversity(ranked)

        # Get top recommendations
        top_ids = [mid for mid, score in diverse[:num_recs]]

        recommendations = []
        for movie_id in top_ids:
            movie_data = self.movies_df[self.movies_df['id'] == movie_id].iloc[0].to_dict()
            explanation = self.explain(movie_id, profile.id)
            recommendations.append({
                'movie': movie_data,
                'score': next((score for mid, score in diverse if mid == movie_id), 0.5),
                'badges': explanation['badges'],
                'confidence': explanation['confidence']
            })

        # Cache for 1 hour
        cache.set(cache_key, recommendations, 3600)

        return recommendations

# Global recommender instance
recommender = MovieRecommender()
