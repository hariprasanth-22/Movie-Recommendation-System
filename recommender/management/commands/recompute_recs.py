from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count
from recommender.models import Profile, CachedRecommendations, Challenge, ChallengeProgress
from recommender.utils import recommender
from datetime import timedelta
import json

class Command(BaseCommand):
    help = 'Recompute cached recommendations for all active profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile_id',
            type=int,
            help='Recompute for specific profile ID only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recompute even if cache is fresh',
        )

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(is_active=True)

        if options['profile_id']:
            profiles = profiles.filter(id=options['profile_id'])

        self.stdout.write(f"Recomputing recommendations for {profiles.count()} profiles...")

        for profile in profiles:
            self.stdout.write(f"Processing profile {profile.id} ({profile.name})")

            # Clear existing cached recommendations
            CachedRecommendations.objects.filter(profile=profile).delete()

            # Recompute For You recommendations
            try:
                recs = recommender.get_personalized_recommendations(profile, num_recs=20)
                CachedRecommendations.objects.create(
                    profile=profile,
                    shelf_key='for_you',
                    payload=recs
                )
                self.stdout.write(f"  - Cached {len(recs)} For You recommendations")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error computing For You: {e}"))

            # Recompute Trending (shared across profiles)
            try:
                trending = recommender.get_trending_movies(20)
                trending_payload = [{'movie': m, 'score': 0.8, 'badges': ['Trending'], 'confidence': 0.7} for m in trending]
                CachedRecommendations.objects.update_or_create(
                    profile=profile,
                    shelf_key='trending',
                    defaults={'payload': trending_payload}
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error computing Trending: {e}"))

            # Recompute genre-based shelves
            try:
                pref_weights = profile.preferenceweights_set.first()
                if pref_weights and pref_weights.genre_weights:
                    top_genres = sorted(pref_weights.genre_weights.items(), key=lambda x: x[1], reverse=True)[:3]
                    for genre, weight in top_genres:
                        genre_recs = recommender.get_movies_by_genre(genre, 10)
                        if genre_recs:
                            genre_payload = [{'movie': m, 'score': 0.6, 'badges': [f'{genre} Movie'], 'confidence': 0.6} for m in genre_recs]
                            CachedRecommendations.objects.update_or_create(
                                profile=profile,
                                shelf_key=f'genre_{genre.lower()}',
                                defaults={'payload': genre_payload}
                            )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error computing genre shelves: {e}"))

            # Clear Django cache for this profile
            cache.delete_pattern(f"recs_{profile.id}_*")

        # Update challenge progress
        self.update_challenges()

        self.stdout.write(self.style.SUCCESS("Recompute completed!"))

    def update_challenges(self):
        """Update progress for active challenges."""
        active_challenges = Challenge.objects.filter(is_active=True)

        for challenge in active_challenges:
            self.stdout.write(f"Updating progress for challenge: {challenge.title}")

            if challenge.challenge_type == 'rate_movies':
                # Count ratings in the challenge period
                start_date = challenge.start_date
                end_date = min(challenge.end_date, timezone.now())

                progress_updates = ChallengeProgress.objects.filter(
                    challenge=challenge,
                    profile__userrating__created_at__gte=start_date,
                    profile__userrating__created_at__lte=end_date
                ).annotate(
                    rating_count=Count('profile__userrating')
                ).values('profile', 'rating_count')

                for update in progress_updates:
                    ChallengeProgress.objects.update_or_create(
                        profile_id=update['profile'],
                        challenge=challenge,
                        defaults={
                            'current_value': update['rating_count'],
                            'completed': update['rating_count'] >= challenge.target_value,
                            'completed_at': timezone.now() if update['rating_count'] >= challenge.target_value else None
                        }
                    )

            # Add more challenge types as needed

        self.stdout.write("Challenge progress updated.")
