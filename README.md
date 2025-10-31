# Movie Recommendation System

A comprehensive Django-based web application for personalized movie recommendations using machine learning algorithms. The system provides user authentication, movie browsing, rating functionality, and intelligent recommendation engine.

## Features

- **User Management**: Registration, login, and profile management with multiple profiles per user
- **Movie Database**: Extensive movie catalog with details from TMDB API
- **Personalized Recommendations**: ML-powered recommendations based on user ratings and preferences
- **Rating System**: 1-5 star rating system for movies
- **Search Functionality**: Full-text search across movie titles and descriptions
- **Dashboard**: User dashboard with ratings history and personalized recommendations
- **Responsive Design**: Bootstrap-based UI that works on all devices
- **Advanced Features**:
  - Multiple user profiles (adult/kids)
  - Preference weights for genres, runtime, language, and content sensitivity
  - Watch history and progress tracking
  - Achievement badges and challenges
  - Leaderboards and social features

## Tech Stack

- **Backend**: Django 4.x, Python 3.11+
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **ML Libraries**: Scikit-learn, Pandas, NumPy
- **APIs**: TMDB API for movie data
- **Deployment**: Ready for Heroku, AWS, or DigitalOcean

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hariprasanth-22/Movie-Recommendation-System.git
   cd Movie-Recommendation-System
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   TMDB_API_KEY=your-tmdb-api-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Load initial data** (optional):
   ```bash
   python manage.py loaddata initial_data.json
   ```

7. **Create superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:
   Open http://localhost:8000 in your browser

## Usage

### For Users
1. Register an account or login
2. Create user profiles (adult/kids)
3. Browse trending movies on the homepage
4. Search for movies using the search bar
5. View movie details and similar recommendations
6. Rate movies (1-5 stars) to improve recommendations
7. Access your dashboard for personalized suggestions
8. Update preferences for better recommendations

### For Developers
- **API Endpoints**: RESTful API for movie data and recommendations
- **Management Commands**: Custom Django commands for data processing
- **ML Models**: Pre-trained models in the `models/` directory
- **Admin Panel**: Django admin interface for content management

## Project Structure

```
movie-recommender/
├── movie_recommender/          # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── recommender/                # Main app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # URL patterns
│   ├── forms.py               # Django forms
│   ├── utils.py               # Utility functions and ML logic
│   ├── management/            # Custom management commands
│   ├── migrations/            # Database migrations
│   ├── static/                # Static files (CSS, JS, images)
│   └── templates/             # HTML templates
├── models/                    # Pre-trained ML models
│   ├── count_matrix.npz
│   ├── count_vectorizer.pkl
│   └── processed_movies.pkl
├── db.sqlite3                 # SQLite database
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## API Documentation

### Movie Endpoints
- `GET /` - Homepage with trending movies
- `GET /movie/<id>/` - Movie detail page
- `POST /rate/<id>/` - Rate a movie
- `GET /search/?q=<query>` - Search movies

### User Endpoints
- `GET /dashboard/` - User dashboard
- `POST /register/` - User registration
- `POST /login/` - User login
- `POST /logout/` - User logout
- `POST /preferences/` - Update user preferences

## Machine Learning

The recommendation system uses:
- **Content-based filtering**: TF-IDF vectorization of movie descriptions
- **Collaborative filtering**: User-item rating matrix factorization
- **Hybrid approach**: Combines content and collaborative methods
- **Personalization**: Incorporates user preferences and profile types

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation
- Ensure migrations are created for model changes

## Testing

Run the test suite:
```bash
python manage.py test
```

## Deployment

### Heroku Deployment
1. Create a Heroku app
2. Set environment variables in Heroku dashboard
3. Push to Heroku git repository
4. Run migrations on Heroku

### Docker Deployment
```bash
docker build -t movie-recommender .
docker run -p 8000:8000 movie-recommender
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Movie data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/)
- Icons from [Font Awesome](https://fontawesome.com/)
- UI framework: [Bootstrap](https://getbootstrap.com/)

## Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Note**: This is a development version. For production use, ensure proper security configurations and database setup.
