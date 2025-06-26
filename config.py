"""
Application Configuration

Simple streamlined configuration for NOUS deployment.
"""
import os
from datetime import timedelta

class Config:
    """Base configuration with common settings"""
    # Flask Configuration
    SECRET_KEY = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")
    DEBUG = False
    TESTING = False

    # Session Configuration
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    SESSION_TYPE = "filesystem"
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///instance/nous.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Upload Configuration
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

class DevelopmentConfig(Config):
    """Configuration for development environment"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration for production environment"""
    # Fixed for Replit deployment - secure cookies only work with HTTPS
    SESSION_COOKIE_SECURE = False  # Allow HTTP for Replit Cloud Run
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  # Prevent CSRF while allowing cross-site

def get_config():
    """Return the configuration class based on environment"""
    env = os.environ.get('FLASK_ENV', 'production')
    if env == 'development':
        return DevelopmentConfig
    else:
        return ProductionConfig