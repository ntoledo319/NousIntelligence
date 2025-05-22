"""
Application Configuration

This module contains different configuration classes for various environments.
It uses environment variables for sensitive information and configuration settings.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration with common settings"""
    # Flask settings
    SECRET_KEY = os.environ.get("SESSION_SECRET", os.environ.get("SECRET_KEY", "nous-secure-key-2025"))
    DEBUG = False
    TESTING = False
    
    # Session settings
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    SESSION_TYPE = "filesystem"
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "nous_session:"
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_FILE_THRESHOLD = 500
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 20,
        'echo_pool': False,
        'pool_use_lifo': True,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'NOUS',
        },
    }
    
    # Upload settings
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

class DevelopmentConfig(Config):
    """Configuration for development environment"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Configuration for testing environment"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuration for production environment"""
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_REFRESH_EACH_REQUEST = False

def get_config():
    """Return the configuration class based on environment (defaults to production)
    
    Returns:
        Configuration class
    """
    env = os.environ.get("FLASK_ENV", "production").lower()
    
    if env == "development":
        return DevelopmentConfig
    elif env == "testing":
        return TestingConfig
    else:
        return ProductionConfig