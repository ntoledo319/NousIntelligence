"""
Rate Limiting Configuration
Unified rate limiting for authentication and API endpoints
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


def get_limiter(app=None):
    """
    Create and configure Flask-Limiter instance
    """
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL', 'memory://'),
        strategy="fixed-window"
    )
    
    if app:
        limiter.init_app(app)
    
    return limiter


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    'auth_login': "5 per minute",
    'auth_callback': "10 per minute",
    'api_general': "100 per minute",
    'api_heavy': "20 per minute",  # AI operations, image processing
    'password_reset': "3 per hour",
    'account_creation': "5 per hour"
}
