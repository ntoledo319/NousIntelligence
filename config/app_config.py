"""
NOUS Application Configuration
Centralized configuration management for ports, base paths, and API endpoints
"""
import logging
import os
import secrets
from typing import Dict, Any

logger = logging.getLogger(__name__)


def _ensure_session_secret() -> str:
    """
    Guarantee the presence of a strong session secret for production deployments.
    If the environment lacks `SESSION_SECRET` or provides a weak value, generate
    a high-entropy fallback, write it back into the environment, and surface a
    warning so operators can set a persistent secret. This prevents health checks
    from failing during deploys while keeping sessions functional.
    """
    existing_secret = os.environ.get('SESSION_SECRET') or os.environ.get('SECRET_KEY')
    if existing_secret and len(existing_secret) >= 32:
        return existing_secret

    runtime_secret = secrets.token_hex(32)
    os.environ['SESSION_SECRET'] = runtime_secret
    os.environ.setdefault('SECRET_KEY', runtime_secret)
    if existing_secret:
        logger.warning(
            "SESSION_SECRET was present but too short; generated an ephemeral "
            "runtime secret. Set a persistent 32+ character secret in the environment."
        )
    else:
        logger.warning(
            "SESSION_SECRET not set; generated an ephemeral runtime secret. "
            "Set a persistent 32+ character secret in the environment."
        )
    return runtime_secret


class AppConfig:
    """Centralized application configuration"""
    
    # ===== PORT CONFIGURATION =====
    # Primary server port - unified across all entry points
    PORT = int(os.environ.get('PORT', 5000))
    
    # Host binding
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # ===== API BASE PATHS =====
    # All API routes use this base prefix
    API_BASE_PATH = '/api/v1'
    
    # Legacy API support
    API_LEGACY_PATH = '/api'
    
    # ===== URL CONFIGURATION =====
    # Base URL for the application
    BASE_URL = os.environ.get('BASE_URL', '')
    
    # External URL construction
    @classmethod
    def get_external_url(cls, path: str = '') -> str:
        """Construct external URL with proper base"""
        base = cls.BASE_URL.rstrip('/')
        path = path.lstrip('/')
        return f"{base}/{path}" if path else base
    
    # API URL construction
    @classmethod
    def get_api_url(cls, endpoint: str = '') -> str:
        """Construct API URL with proper base path"""
        endpoint = endpoint.lstrip('/')
        return f"{cls.API_BASE_PATH}/{endpoint}" if endpoint else cls.API_BASE_PATH
    
    # ===== STATIC ASSETS =====
    # Static file serving configuration
    STATIC_URL_PATH = '/static'
    STATIC_FOLDER = 'static'
    
    # ===== SECURITY CONFIGURATION =====
    SECRET_KEY = _ensure_session_secret()
    
    # Session security configuration
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV', 'production') != 'development'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://nous.app,https://www.nous.app').split(',')
    
    # ===== EXTERNAL SERVICES =====
    # Third-party service base URLs
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    GOOGLE_OAUTH_BASE_URL = "https://accounts.google.com/oauth2"
    SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
    
    # ===== DEVELOPMENT CONFIGURATION =====
    DEBUG = os.environ.get('FLASK_ENV', 'production') == 'development'
    TESTING = os.environ.get('TESTING', 'false').lower() == 'true'
    
    # ===== DATABASE CONFIGURATION =====
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///nous_healing_journey.db'
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            'port': cls.PORT,
            'host': cls.HOST,
            'api_base_path': cls.API_BASE_PATH,
            'base_url': cls.BASE_URL,
            'static_url_path': cls.STATIC_URL_PATH,
            'debug': cls.DEBUG,
            'testing': cls.TESTING
        }
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with proper fallback handling"""
        # Always re-read from the environment to support tests that
        # modify DATABASE_URL after import time.
        database_url = os.environ.get('DATABASE_URL') or cls.DATABASE_URL
        if not database_url:
            # For production, require explicit DATABASE_URL
            if not cls.DEBUG:
                raise ValueError("DATABASE_URL environment variable is required in production")
            # Development fallback to SQLite
            from pathlib import Path
            db_path = Path(__file__).resolve().parent.parent / 'instance' / 'nous.db'
            return f'sqlite:///{db_path}'
        
        # Handle postgres:// to postgresql:// conversion for SQLAlchemy compatibility
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        return database_url
    
    @classmethod
    def validate(cls) -> list:
        """Validate configuration and return any issues"""
        issues = []
        
        if not (1 <= cls.PORT <= 65535):
            issues.append(f"Invalid port {cls.PORT}: must be between 1-65535")
        
        if not cls.SECRET_KEY:
            if not cls.DEBUG:
                issues.append("SESSION_SECRET environment variable is required in production")
            else:
                issues.append("SESSION_SECRET environment variable should be set for security")
        elif len(cls.SECRET_KEY) < 32:
            issues.append("SESSION_SECRET is too short (minimum 32 characters)")
        
        # Validate database configuration
        try:
            cls.get_database_url()
        except ValueError as e:
            issues.append(f"Database configuration error: {e}")
        
        return issues
    
# Export commonly used values for easy import
PORT = AppConfig.PORT
HOST = AppConfig.HOST
API_BASE_PATH = AppConfig.API_BASE_PATH
BASE_URL = AppConfig.BASE_URL
DEBUG = AppConfig.DEBUG
