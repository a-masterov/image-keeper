# Image Keeper

A Django-based image sharing site that allows for uploading, downloading, and displaying JPEG images. Images are stored as Large Objects in PostgreSQL database. The site includes user registration and authentication to restrict access to registered users only.

## Features

- User registration and authentication
- Upload JPEG images with title and description
- View images in a gallery
- View image details
- Download images
- Delete your own images
- User profiles

## Technology Stack

- Django 5.1.7
- PostgreSQL (for production, using Large Objects for image storage)
- SQLite (for development)
- Bootstrap 5 (for UI)

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL (for production)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/a-masterov/image-keeper.git
   cd image-keeper
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and configure your environment variables.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the site at http://127.0.0.1:8000/

## Production Deployment

For production deployment, make sure to:

1. Set `DJANGO_DEBUG=False` in your environment variables
2. Configure `DJANGO_ALLOWED_HOSTS` with your domain
3. Use PostgreSQL as your database
4. Set a strong `DJANGO_SECRET_KEY`
5. Configure proper static files serving
