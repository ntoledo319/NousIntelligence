"""
Environment Loader

This module loads environment variables from a local `.env` file (when present)
and applies sane defaults for test environments.

## Concept: Test-Safe Defaults
Some parts of the codebase (notably `src/app_factory.py`) expect `SECRET_KEY`
and `DATABASE_URL` to exist. In production we enforce that requirement, but in
pytest we auto-fill safe defaults to keep the app importable and testable.
"""

import os
import sys
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Backwards/compat: many modules use SESSION_SECRET, while some older code
    # expects SECRET_KEY.
    if not os.getenv('SECRET_KEY') and os.getenv('SESSION_SECRET'):
        os.environ['SECRET_KEY'] = os.environ['SESSION_SECRET']

    # Detect test runs (even if TESTING env var isn't set).
    pytest_running = (
        "PYTEST_CURRENT_TEST" in os.environ
        or "pytest" in sys.modules
        or any(k.startswith("PYTEST_") for k in os.environ.keys())
    )

    # In tests, default to an in-memory DB if none provided.
    if pytest_running and not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    # In tests, default to a deterministic secret so Flask sessions work.
    if pytest_running and not os.getenv('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'test-secret-key'
    if pytest_running and not os.getenv('SESSION_SECRET'):
        os.environ['SESSION_SECRET'] = os.environ['SECRET_KEY']

    # Validate required variables
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        # Only enforce strictly outside tests.
        if not pytest_running:
            raise ValueError(f"Missing required environment variables: {missing}")

def get_config():
    """Get configuration from environment"""
    return {
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    }
