from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return self.title

class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.rating}"

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_genres = models.JSONField(default=list)  # List of genre IDs
    preferred_actors = models.JSONField(default=list)  # List of actor names
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"
