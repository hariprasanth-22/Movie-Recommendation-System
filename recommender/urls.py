from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('rate/<int:movie_id>/', views.rate_movie, name='rate_movie'),
    path('search/', views.search, name='search'),
    path('preferences/', views.update_preferences, name='update_preferences'),
]
