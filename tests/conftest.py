"""
Test Configuration
Centralized testing configuration and utilities
"""

import os
import pytest
from pathlib import Path

# Test configuration
TEST_DATABASE_URL = "sqlite:///:memory:"
TEST_SECRET_KEY = "test-secret-key-for-testing-only-32chars"

class TestConfig:
    """Test-specific configuration"""
    TESTING = True
    SECRET_KEY = TEST_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    
    # Disable authentication for testing
    TESTING_MODE = True

@pytest.fixture
def client():
    """Create test client"""
    from app import create_app
    
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client"""
    # Create test session
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_123'
        sess['username'] = 'Test User'
        sess['email'] = 'test@example.com'
        sess['is_demo'] = False
    
    return client
