import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    
    # Validate required variables
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
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
