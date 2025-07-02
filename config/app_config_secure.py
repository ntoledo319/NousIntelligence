"""
NOUS Application Configuration (Security Hardened)
Centralized configuration management with production-ready security settings
"""
import os
from typing import Dict, Any

class SecureAppConfig:
    """Security-hardened application configuration"""
    
    # ===== PORT CONFIGURATION =====
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # ===== ENVIRONMENT DETECTION =====
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'production').lower()
    DEBUG = ENVIRONMENT == 'development'
    TESTING = os.environ.get('TESTING', 'false').lower() == 'true'
    
    # ===== API BASE PATHS =====
    API_BASE_PATH = '/api/v1'
    API_LEGACY_PATH = '/api'
    
    # ===== URL CONFIGURATION =====
    BASE_URL = os.environ.get('BASE_URL', '')
    
    @classmethod
    def get_external_url(cls, path: str = '') -> str:
        """Construct external URL with proper base"""
        base = cls.BASE_URL.rstrip('/')
        path = path.lstrip('/')
        return f"{base}/{path}" if path else base
    
    @classmethod
    def get_api_url(cls, endpoint: str = '') -> str:
        """Construct API URL with proper base path"""
        endpoint = endpoint.lstrip('/')
        return f"{cls.API_BASE_PATH}/{endpoint}" if endpoint else cls.API_BASE_PATH
    
    # ===== STATIC ASSETS =====
    STATIC_URL_PATH = '/static'
    STATIC_FOLDER = 'static'
    
    # ===== SECURITY CONFIGURATION =====
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    
    # Validate secret key strength
    @classmethod
    def validate_secret_key(cls):
        """Validate that secret key meets security requirements"""
        if not cls.SECRET_KEY:
            if cls.DEBUG:
                # Generate a warning-level temporary key for development
                import secrets
                cls.SECRET_KEY = secrets.token_hex(32)
                import logging
                logging.warning("Using temporary SECRET_KEY for development. Set SESSION_SECRET in production!")
            else:
                raise ValueError("SESSION_SECRET environment variable is required in production")
        elif len(cls.SECRET_KEY) < 32:
            raise ValueError("SESSION_SECRET must be at least 32 characters for security")
        return cls.SECRET_KEY
    
    # ===== SESSION SECURITY CONFIGURATION =====
    # Always use secure cookies in production, only allow insecure in development
    SESSION_COOKIE_SECURE = not DEBUG  # Force secure cookies in production
    SESSION_COOKIE_HTTPONLY = True     # Always prevent XSS access to cookies
    SESSION_COOKIE_SAMESITE = 'Strict' # Enhanced CSRF protection
    
    # Shorter session lifetime for security
    PERMANENT_SESSION_LIFETIME = 3600 if not DEBUG else 7200  # 1 hour prod, 2 hours dev
    
    # Session cookie name obfuscation
    SESSION_COOKIE_NAME = 'nous_session'
    
    # Enhanced session configuration
    SESSION_REGENERATE_ON_LOGIN = True
    SESSION_COOKIE_DOMAIN = None  # Let Flask auto-detect
    
    # ===== CORS CONFIGURATION =====
    # Strict CORS policy for production
    CORS_ORIGINS = []
    if DEBUG:
        CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', 'http://127.0.0.1:5000']
    else:
        cors_env = os.environ.get('CORS_ORIGINS', 'https://nous.app,https://www.nous.app')
        CORS_ORIGINS = [origin.strip() for origin in cors_env.split(',') if origin.strip()]
    
    # ===== SECURITY HEADERS =====
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }
    
    # Content Security Policy
    if not DEBUG:
        SECURITY_HEADERS['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://apis.google.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openrouter.ai https://accounts.google.com;"
        )
    
    # ===== EXTERNAL SERVICES =====
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    GOOGLE_OAUTH_BASE_URL = "https://accounts.google.com/oauth2"
    SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
    
    # ===== DATABASE CONFIGURATION =====
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Database security settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "echo": DEBUG,  # Only log SQL in development
    }
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with proper fallback handling"""
        database_url = cls.DATABASE_URL
        if not database_url:
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
    
    # ===== CSRF PROTECTION =====
    CSRF_TOKEN_LIFETIME = 1800  # 30 minutes
    CSRF_SECRET_KEY = None  # Will use SECRET_KEY if not set
    
    # ===== RATE LIMITING =====
    RATELIMIT_STORAGE_URL = "memory://" if DEBUG else os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "100 per hour" if not DEBUG else "1000 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # ===== LOGGING CONFIGURATION =====
    LOG_LEVEL = 'INFO' if not DEBUG else 'DEBUG'
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    LOG_TO_STDOUT = not DEBUG
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary (safe values only)"""
        return {
            'port': cls.PORT,
            'host': cls.HOST,
            'api_base_path': cls.API_BASE_PATH,
            'base_url': cls.BASE_URL,
            'static_url_path': cls.STATIC_URL_PATH,
            'debug': cls.DEBUG,
            'testing': cls.TESTING,
            'environment': cls.ENVIRONMENT,
            'session_secure': cls.SESSION_COOKIE_SECURE,
            'csrf_enabled': True,
            'security_headers_enabled': True,
        }
    
    @classmethod
    def validate(cls) -> list:
        """Validate configuration and return any issues"""
        issues = []
        
        # Port validation
        if not (1 <= cls.PORT <= 65535):
            issues.append(f"Invalid port {cls.PORT}: must be between 1-65535")
        
        # Secret key validation
        try:
            cls.validate_secret_key()
        except ValueError as e:
            issues.append(f"Secret key validation failed: {e}")
        
        # Database validation
        try:
            cls.get_database_url()
        except ValueError as e:
            issues.append(f"Database configuration error: {e}")
        
        # Production security checks
        if not cls.DEBUG:
            if not cls.SESSION_COOKIE_SECURE:
                issues.append("SESSION_COOKIE_SECURE must be True in production")
            
            if cls.PERMANENT_SESSION_LIFETIME > 3600:
                issues.append("Session lifetime too long for production (max 1 hour recommended)")
            
            if not cls.CORS_ORIGINS:
                issues.append("CORS_ORIGINS should be configured for production")
        
        return issues
    
    @classmethod
    def apply_to_flask_app(cls, app):
        """Apply configuration to Flask app with security settings"""
        # Validate configuration first
        cls.validate_secret_key()
        
        # Basic Flask config
        app.config['SECRET_KEY'] = cls.SECRET_KEY
        app.config['DEBUG'] = cls.DEBUG
        app.config['TESTING'] = cls.TESTING
        
        # Database configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = cls.get_database_url()
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = cls.SQLALCHEMY_ENGINE_OPTIONS
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Session configuration
        app.config['SESSION_COOKIE_SECURE'] = cls.SESSION_COOKIE_SECURE
        app.config['SESSION_COOKIE_HTTPONLY'] = cls.SESSION_COOKIE_HTTPONLY
        app.config['SESSION_COOKIE_SAMESITE'] = cls.SESSION_COOKIE_SAMESITE
        app.config['SESSION_COOKIE_NAME'] = cls.SESSION_COOKIE_NAME
        app.config['PERMANENT_SESSION_LIFETIME'] = cls.PERMANENT_SESSION_LIFETIME
        
        # Security headers
        @app.after_request
        def add_security_headers(response):
            for header, value in cls.SECURITY_HEADERS.items():
                response.headers[header] = value
            return response
        
        return app


# Export commonly used values for easy import
AppConfig = SecureAppConfig  # Backward compatibility
PORT = SecureAppConfig.PORT
HOST = SecureAppConfig.HOST
API_BASE_PATH = SecureAppConfig.API_BASE_PATH
BASE_URL = SecureAppConfig.BASE_URL
DEBUG = SecureAppConfig.DEBUG