from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Profile(models.Model):
    PROFILE_TYPES = [
        ('adult', 'Adult'),
        ('kids', 'Kids'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    profile_type = models.CharField(max_length=10, choices=PROFILE_TYPES, default='adult')
    avatar = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.profile_type})"

class PreferenceWeights(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    genre_weights = models.JSONField(default=dict)  # {'Action': 0.8, 'Comedy': 0.6}
    runtime_weights = models.JSONField(default=dict)  # {'short': 0.7, 'medium': 0.8, 'long': 0.5}
    language_weights = models.JSONField(default=dict)  # {'en': 0.9, 'es': 0.4}
    sensitivity_weights = models.JSONField(default=dict)  # {'mild': 0.8, 'moderate': 0.6, 'intense': 0.2}
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Weights for {self.profile}"

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField()
    genres = models.JSONField()  # List of genres
    release_year = models.IntegerField()
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    cast = models.JSONField(blank=True, null=True)  # List of cast members
    director = models.CharField(max_length=255, blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)  # in minutes
    language = models.CharField(max_length=10, blank=True, null=True)  # ISO language code
    maturity_rating = models.CharField(max_length=10, blank=True, null=True)  # PG, PG-13, R, etc.

    def __str__(self):
        return self.title

class UserRating(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie')

    def __str__(self):
        return f"{self.profile} - {self.movie.title}: {self.rating}"

class WatchEvent(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watch_duration = models.IntegerField(default=0)  # seconds watched
    total_duration = models.IntegerField(blank=True, null=True)  # total movie duration
    completed = models.BooleanField(default=False)
    last_watched = models.DateTimeField(auto_now=True)
    added_to_list = models.BooleanField(default=False)

    class Meta:
        unique_together = ('profile', 'movie')

    def __str__(self):
        return f"{self.profile} watched {self.movie.title}"

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('not_interested', 'Not Interested'),
        ('seen_it', 'Seen It'),
        ('show_fewer', 'Show Fewer Like This'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie', 'feedback_type')

    def __str__(self):
        return f"{self.profile} {self.feedback_type} {self.movie.title}"

class SavedList(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    list_type = models.CharField(max_length=20, default='watchlist')  # watchlist, favorites, etc.
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'movie', 'list_type')

    def __str__(self):
        return f"{self.profile}'s {self.list_type}: {self.movie.title}"

class Badge(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    badge_type = models.CharField(max_length=50)  # Critic, Explorer, Sci-Fi Buff, etc.
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'badge_type')

    def __str__(self):
        return f"{self.profile} earned {self.badge_type}"

class Challenge(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    challenge_type = models.CharField(max_length=50)  # rate_movies, watch_genre, etc.
    target_value = models.IntegerField()
    reward_badge = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class ChallengeProgress(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    current_value = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('profile', 'challenge')

    def __str__(self):
        return f"{self.profile} progress on {self.challenge}"

class Leaderboard(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    period = models.CharField(max_length=20)  # weekly, monthly, all_time
    score = models.IntegerField(default=0)  # points from ratings, completions, etc.
    rank = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('profile', 'period')

    def __str__(self):
        return f"{self.profile} rank {self.rank} in {self.period}"

class CachedRecommendations(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    shelf_key = models.CharField(max_length=100)  # trending, for_you, genre_action, etc.
    payload = models.JSONField()  # list of movie dicts with scores, badges, etc.
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'shelf_key')
        indexes = [
            models.Index(fields=['profile', 'shelf_key']),
            models.Index(fields=['generated_at']),
        ]

    def __str__(self):
        return f"Cached recs for {self.profile}: {self.shelf_key}"

# Legacy model for backward compatibility
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_genres = models.JSONField(default=list)  # List of genre IDs
    preferred_actors = models.JSONField(default=list)  # List of actor names
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"
