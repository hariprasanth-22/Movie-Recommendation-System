import pickle
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
import os

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

# Global recommender instance
recommender = MovieRecommender()
