from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Movie, UserRating, UserPreference
from .utils import recommender
from .forms import UserRegistrationForm, RatingForm
import json

def home(request):
    """Homepage showing trending movies."""
    trending_movies = recommender.get_trending_movies(20)
    context = {
        'trending_movies': trending_movies,
        'user': request.user,
    }
    return render(request, 'recommender/home.html', context)

def movie_detail(request, movie_id):
    """Detailed movie page with recommendations."""
    # Get movie data from the recommender
    movie_data = None
    for movie in recommender.movies_df[recommender.movies_df['id'] == movie_id].to_dict('records'):
        movie_data = movie
        break

    if not movie_data:
        return render(request, '404.html', status=404)

    # Get recommendations
    recommendations = recommender.get_recommendations(movie_id, 6)

    # Check if user has rated this movie
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = UserRating.objects.get(user=request.user, movie__tmdb_id=movie_id)
        except UserRating.DoesNotExist:
            pass

    context = {
        'movie': movie_data,
        'recommendations': recommendations,
        'user_rating': user_rating,
        'rating_form': RatingForm() if request.user.is_authenticated else None,
        'genres_json': json.dumps(movie_data['genres']),
    }
    return render(request, 'recommender/movie_detail.html', context)

@login_required
def dashboard(request):
    """User dashboard with recommendations and profile."""
    # Get user's ratings
    user_ratings = UserRating.objects.filter(user=request.user).select_related('movie')
    rated_movie_ids = [rating.movie.tmdb_id for rating in user_ratings]

    # Get personalized recommendations (for now, just trending movies not rated)
    all_trending = recommender.get_trending_movies(50)
    recommendations = [movie for movie in all_trending if movie['id'] not in rated_movie_ids][:10]

    # Get user's preferences
    try:
        preferences = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        preferences = None

    context = {
        'user_ratings': user_ratings,
        'recommendations': recommendations,
        'preferences': preferences,
    }
    return render(request, 'recommender/dashboard.html', context)

def register(request):
    """User registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'recommender/register.html', {'form': form})

def user_login(request):
    """User login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'recommender/login.html')

def user_logout(request):
    """User logout."""
    logout(request)
    return redirect('home')

@login_required
@require_POST
def rate_movie(request, movie_id):
    """Rate a movie."""
    rating_value = request.POST.get('rating')
    if not rating_value:
        return JsonResponse({'error': 'Rating required'}, status=400)

    try:
        rating_value = float(rating_value)
        if not 1 <= rating_value <= 5:
            raise ValueError
    except ValueError:
        return JsonResponse({'error': 'Invalid rating'}, status=400)

    # Get or create movie
    movie, created = Movie.objects.get_or_create(
        tmdb_id=movie_id,
        defaults={
            'title': request.POST.get('title', 'Unknown'),
            'overview': request.POST.get('overview', ''),
            'genres': json.loads(request.POST.get('genres', '[]')),
            'release_year': int(request.POST.get('release_year', 0)),
            'vote_average': float(request.POST.get('vote_average', 0)),
            'vote_count': 0,
        }
    )

    # Create or update rating
    rating, created = UserRating.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={'rating': rating_value}
    )

    return JsonResponse({'success': True, 'rating': rating_value})

def search(request):
    """Search movies."""
    query = request.GET.get('q', '')
    if not query:
        return render(request, 'recommender/search.html', {'movies': [], 'query': query})

    movies = recommender.search_movies(query, 20)
    return render(request, 'recommender/search.html', {'movies': movies, 'query': query})

@login_required
@require_POST
def update_preferences(request):
    """Update user preferences."""
    favorite_genres = request.POST.getlist('genres')
    preferred_actors = request.POST.get('actors', '').split(',')

    preferences, created = UserPreference.objects.update_or_create(
        user=request.user,
        defaults={
            'favorite_genres': favorite_genres,
            'preferred_actors': [actor.strip() for actor in preferred_actors if actor.strip()],
        }
    )

    messages.success(request, 'Preferences updated!')
    return redirect('dashboard')
