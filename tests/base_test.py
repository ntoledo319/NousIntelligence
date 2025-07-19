import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from src.app_factory import create_app
import json

class BaseTestCase:
    """Base test class with common setup"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        # Create test app with test config
        self.app = create_app('testing')
        
        # Set up application context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test client
        self.client = self.app.test_client()
        
        # Debug: Print registered routes
        print("\n=== Registered Routes ===")
        for rule in self.app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule} {list(rule.methods)}")
        print("=======================\n")
        
        yield
        
        # Clean up
        self.app_context.pop()
    
    def json_post(self, url, data=None, headers=None):
        """Helper for JSON POST requests"""
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        return self.client.post(url, data=json.dumps(data), headers=headers)
    
    def json_put(self, url, data=None, headers=None):
        """Helper for JSON PUT requests"""
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        return self.client.put(url, data=json.dumps(data), headers=headers)
    
    def auth_headers(self, token):
        """Get authentication headers"""
        return {'Authorization': f'Bearer {token}'}
    
    def create_mock_user(self, user_id='test_user', name='Test User'):
        """Create mock user"""
        return {
            'id': user_id,
            'name': name,
            'email': f'{user_id}@example.com',
            'is_demo': True
        }
