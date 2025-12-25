"""
Production Security Configuration
Implements CORS, rate limiting, and enhanced security for Render deployment
"""

import os
import logging
from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)


def init_production_security(app: Flask) -> dict:
    """
    Initialize production security features including CORS and rate limiting.

    Args:
        app: Flask application instance

    Returns:
        dict: Initialized security components
    """
    components = {}

    # Initialize CORS
    components['cors'] = init_cors(app)

    # Initialize rate limiting
    components['limiter'] = init_rate_limiting(app)

    logger.info("✅ Production security initialized successfully")
    return components


def init_cors(app: Flask) -> CORS:
    """
    Initialize CORS (Cross-Origin Resource Sharing) configuration.

    Configures appropriate CORS settings for production deployment on Render,
    allowing requests from the frontend while maintaining security.
    """
    # Get allowed origins from environment or use secure defaults
    allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

    # Default allowed origins for Render deployment
    default_origins = [
        'https://nous-intelligence-web.onrender.com',
        'https://nous-assistant.onrender.com',
    ]

    # Add localhost for development
    if app.debug or os.environ.get('FLASK_ENV') == 'development':
        default_origins.extend([
            'http://localhost:3000',
            'http://localhost:8080',
            'http://localhost:5000',
        ])

    # Combine custom origins with defaults
    origins = [o.strip() for o in allowed_origins if o.strip()] or default_origins

    # Initialize CORS with secure configuration
    cors = CORS(
        app,
        resources={
            r"/api/*": {
                "origins": origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "X-CSRF-Token",
                    "X-Request-ID",
                ],
                "expose_headers": [
                    "X-Request-ID",
                    "X-RateLimit-Limit",
                    "X-RateLimit-Remaining",
                    "X-RateLimit-Reset",
                ],
                "supports_credentials": True,
                "max_age": 3600,  # Cache preflight requests for 1 hour
            },
            r"/auth/*": {
                "origins": origins,
                "methods": ["GET", "POST"],
                "supports_credentials": True,
            },
            r"/callback/*": {
                "origins": origins,
                "methods": ["GET", "POST"],
                "supports_credentials": True,
            }
        }
    )

    logger.info(f"🔒 CORS initialized for origins: {', '.join(origins)}")
    return cors


def init_rate_limiting(app: Flask) -> Limiter:
    """
    Initialize rate limiting to protect against abuse and DDoS attacks.

    Implements different rate limits for different endpoint categories:
    - Authentication: Strict limits to prevent brute force
    - API endpoints: Moderate limits for normal usage
    - Static files: Generous limits
    """
    # Configure storage backend
    # For production with Redis
    storage_uri = os.environ.get('REDIS_URL') or os.environ.get('REDISCLOUD_URL')

    # Fall back to in-memory storage if Redis not available
    if not storage_uri:
        logger.warning("⚠️  Redis not configured, using in-memory rate limiting (not recommended for production)")
        storage_uri = "memory://"

    # Initialize Flask-Limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=["200 per hour", "50 per minute"],
        # Strategy: moving-window for more accurate rate limiting
        strategy="moving-window",
        # Headers to expose rate limit info
        headers_enabled=True,
        # Customize error messages
        on_breach=rate_limit_handler,
    )

    # Apply specific limits to authentication endpoints
    limiter.limit("5 per minute")(app.view_functions.get('auth_routes.google_login', lambda: None))
    limiter.limit("10 per hour")(app.view_functions.get('callback_routes.google_callback', lambda: None))

    # Apply limits to API endpoints
    @limiter.request_filter
    def ignore_health_check():
        """Don't rate limit health check endpoints"""
        return request.endpoint in ['health', 'api_routes.health_check']

    logger.info("🛡️  Rate limiting initialized successfully")
    return limiter


def rate_limit_handler(request_limit):
    """
    Custom handler for rate limit breaches.

    Args:
        request_limit: The limit that was exceeded

    Returns:
        tuple: JSON response and HTTP status code
    """
    from flask import jsonify

    logger.warning(
        f"Rate limit exceeded: {request.remote_addr} - {request.endpoint} - "
        f"Limit: {request_limit.limit}"
    )

    return jsonify({
        "error": "rate_limit_exceeded",
        "message": "Too many requests. Please slow down and try again later.",
        "retry_after": request_limit.reset_at,
    }), 429


def get_security_config() -> dict:
    """
    Get security configuration for the application.

    Returns:
        dict: Security configuration parameters
    """
    return {
        'session_cookie_secure': not (
            os.environ.get('FLASK_ENV') == 'development' or
            os.environ.get('DEBUG') == 'True'
        ),
        'session_cookie_httponly': True,
        'session_cookie_samesite': 'Lax',
        'permanent_session_lifetime': 3600,  # 1 hour
        'max_content_length': 16 * 1024 * 1024,  # 16MB max request size
    }


def apply_security_config(app: Flask) -> None:
    """
    Apply security configuration to Flask app.

    Args:
        app: Flask application instance
    """
    config = get_security_config()

    app.config['SESSION_COOKIE_SECURE'] = config['session_cookie_secure']
    app.config['SESSION_COOKIE_HTTPONLY'] = config['session_cookie_httponly']
    app.config['SESSION_COOKIE_SAMESITE'] = config['session_cookie_samesite']
    app.config['PERMANENT_SESSION_LIFETIME'] = config['permanent_session_lifetime']
    app.config['MAX_CONTENT_LENGTH'] = config['max_content_length']

    logger.info("🔐 Security configuration applied")
