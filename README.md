# Movie Recommendation System

A Django-based web application for movie recommendations using machine learning algorithms.

## Features

- User registration and authentication
- Movie search and browsing
- Personalized movie recommendations
- Dashboard for user interactions
- Responsive web design

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/hariprasanth-22/Movie-Recommendation-System.git
   cd Movie-Recommendation-System
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Load initial data (if available):
   ```
   python manage.py loaddata initial_data.json
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage

- Access the application at `http://localhost:8000`
- Register a new account or login
- Search for movies or get recommendations

## Project Structure

- `movie_recommender/`: Main Django project settings
- `recommender/`: Main app containing models, views, and templates
- `models/`: Pre-trained ML models for recommendations
- `static/`: Static files (CSS, JS, images)
- `templates/`: HTML templates

## Technologies Used

- Django
- Python
- HTML/CSS/JavaScript
- Scikit-learn (for ML models)
- SQLite (database)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
