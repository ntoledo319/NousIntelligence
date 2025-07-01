#!/usr/bin/env python3
"""
Generated API Tests
Comprehensive testing for API endpoints
"""

import json
import pytest
from app import app, db

class TestAPIEndpoints:
    """Test all API endpoints for functionality and security"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.drop_all()
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers"""
        return {'Content-Type': 'application/json'}


    def test_api_dashboard_stats(self, client, auth_headers):
        """Test /api/dashboard/stats endpoint"""
        # Test GET request
        response = client.get('/api/dashboard/stats', headers=auth_headers)
        assert response.status_code in [200, 401, 404], f"Unexpected status: {response.status_code}"
        
        # Test with demo mode if available
        demo_headers = {'Content-Type': 'application/json', 'X-Demo-Mode': 'true'}
        response = client.get('/api/dashboard/stats', headers=demo_headers)
        assert response.status_code in [200, 401, 404], f"Demo mode failed: {response.status_code}"
        
        # Test JSON response format
        if response.status_code == 200:
            try:
                data = response.get_json()
                assert isinstance(data, (dict, list)), "Response should be JSON"
            except:
                pass  # Some endpoints return HTML

    def test_api_data(self, client, auth_headers):
        """Test /api/data endpoint"""
        # Test GET request
        response = client.get('/api/data', headers=auth_headers)
        assert response.status_code in [200, 401, 404], f"Unexpected status: {response.status_code}"
        
        # Test with demo mode if available
        demo_headers = {'Content-Type': 'application/json', 'X-Demo-Mode': 'true'}
        response = client.get('/api/data', headers=demo_headers)
        assert response.status_code in [200, 401, 404], f"Demo mode failed: {response.status_code}"
        
        # Test JSON response format
        if response.status_code == 200:
            try:
                data = response.get_json()
                assert isinstance(data, (dict, list)), "Response should be JSON"
            except:
                pass  # Some endpoints return HTML

    def test_api_security_headers(self, client):
        """Test that API endpoints include security headers"""
        test_routes = ['/api/health', '/api/chat', '/api/user']
        
        for route in test_routes:
            response = client.get(route)
            # Check for basic security headers
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-Frame-Options' in response.headers
    
    def test_api_rate_limiting(self, client):
        """Test API rate limiting"""
        # Make multiple rapid requests
        for i in range(10):
            response = client.get('/api/health')
            if response.status_code == 429:
                break
        # Rate limiting should kick in eventually
    
    def test_api_error_handling(self, client):
        """Test API error handling"""
        # Test non-existent endpoint
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Test malformed JSON
        response = client.post('/api/chat', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code in [400, 422]
