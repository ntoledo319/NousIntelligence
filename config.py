"""
Application Configuration

This module contains different configuration classes for various environments.
It uses environment variables for sensitive information.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration with common settings"""
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET") or "change_this_in_production!"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_TYPE = "filesystem"
    SESSION_USE_SIGNER = True

    # Database settings
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Optimized database connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,          # Test connections before use to prevent stale connections
        'pool_recycle': 300,            # Recycle connections after 5 minutes (reduced from 10)
        'pool_size': 10,                # Default pool size (reduced from 20 for better resource usage)
        'max_overflow': 20,             # Allow more overflow connections when needed (increased from 10)
        'pool_timeout': 20,             # Timeout for getting connection from pool (reduced from 30)
        'echo_pool': False,             # Don't echo pool events (optimization)
        'pool_use_lifo': True,          # Use LIFO to reuse recently used connections (improved performance)
        'connect_args': {               # Connection arguments
            'connect_timeout': 10,      # Connection timeout
            'application_name': 'NOUS', # Application name for monitoring
        },
    }

    # Security settings
    BETA_MODE = os.environ.get('ENABLE_BETA_MODE', 'true').lower() == 'true'
    BETA_ACCESS_CODE = os.environ.get('BETA_ACCESS_CODE', 'BETANOUS2025')
    MAX_BETA_TESTERS = int(os.environ.get('MAX_BETA_TESTERS', '30'))

    # OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "https://mynous.replit.app/auth/google/callback")
    
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "https://mynous.replit.app/callback/spotify")
    
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_DEFAULT = "200 per hour"
    RATELIMIT_HEADERS_ENABLED = True

    # File uploads
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB


class DevelopmentConfig(Config):
    """Configuration for development environment"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    # Override OAuth redirect URIs for local development
    GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/google/callback")
    SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:8080/callback/spotify")


class TestingConfig(Config):
    """Configuration for testing environment"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost"


class ProductionConfig(Config):
    """Configuration for production environment"""
    DEBUG = False
    TESTING = False

    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True


# Dictionary to map environment names to config classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Get config by environment name, defaulting to development
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, config_by_name['default']) 