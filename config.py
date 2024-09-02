import os
from pathlib import Path

class Config:
    # General configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_default_secret_key')
    FLASK_APP = os.environ.get('FLASK_APP', 'wsgi:app')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///auctn_ref.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Caching configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')  # Options: 'simple', 'redis', etc.
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')

    # Flask-Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') 
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG', 'False').lower() in ['true', '1', 'yes']
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'your_default_salt')

    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Options: 'Lax', 'Strict', 'None'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # Logging configuration
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO')
    LOGGING_FORMAT = os.environ.get('LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Security headers
    CONTENT_SECURITY_POLICY = {
        'default-src': ['\'self\''],
        'img-src': ['\'self\'', 'data:'],
    }

    @staticmethod
    def init_app(app):
        pass
