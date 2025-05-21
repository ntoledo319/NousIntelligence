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
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET")

    # Allow loading a secret key from a file *only* if the env vars are not set.
    # This supports container-secret mounts while preventing an insecure default.
    if not SECRET_KEY and os.path.exists('.secret_key'):
        with open('.secret_key', 'r') as f:
            file_key = f.read().strip()
            if file_key:
                SECRET_KEY = file_key

    # Fail fast if no secure secret key is configured.
    if not SECRET_KEY or len(SECRET_KEY) < 16:
        # A 128-bit key (16 raw bytes / 32 hex chars) is a reasonable minimum.
        raise RuntimeError(
            "SECRET_KEY is not configured. Set the SECRET_KEY environment "
            "variable or mount a .secret_key file containing a strong random value."
        )

    # Cookie security – make SameSite default to Lax for all environments.
    SESSION_COOKIE_SAMESITE = "Lax"

    # Toggle automatic table creation (dangerous in prod) via env variable.
    AUTO_CREATE_TABLES = os.environ.get("AUTO_CREATE_TABLES", "false").lower() == "true"
    
    # Improve session persistence
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)  # Extend session lifetime
    SESSION_TYPE = "filesystem"
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = "nous_session:"
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')
    SESSION_REFRESH_EACH_REQUEST = True  # Refresh session on each request
    SESSION_FILE_THRESHOLD = 500  # Max number of sessions stored (decreased from default)

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
    # Update the Google redirect URI to use the correct path structure
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
    
    # Mobile settings
    MOBILE_REDIRECT_AFTER_LOGIN = 'dashboard.dashboard'


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
    # Don't refresh session on every request in production to reduce load
    SESSION_REFRESH_EACH_REQUEST = False


# Dictionary to map environment names to config classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}

# Get config by environment name, defaulting to production
def get_config():
    """Return the configuration class based on FLASK_ENV (production default)."""
    env = os.environ.get('FLASK_ENV', 'production')
    return config_by_name.get(env, config_by_name['default']) 