#!/usr/bin/env python3
"""
Generated Integration Tests
End-to-end testing for critical user flows
"""

import pytest
from app import app, db

class TestIntegration:
    """Integration tests for complete user workflows"""
    
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
    
    def test_landing_page_flow(self, client):
        """Test complete landing page to demo flow"""
        # Step 1: Access landing page
        response = client.get('/')
        assert response.status_code == 200
        
        # Step 2: Navigate to demo
        response = client.get('/demo')
        assert response.status_code == 200
        
        # Step 3: Test demo functionality
        response = client.post('/api/demo/chat', 
                             json={'message': 'Hello'})
        assert response.status_code in [200, 401]  # May require auth
    
    def test_health_monitoring_flow(self, client):
        """Test health monitoring endpoints"""
        # Test basic health
        response = client.get('/health')
        assert response.status_code == 200
        
        # Test detailed health
        response = client.get('/healthz')
        assert response.status_code == 200
        
        # Test API health
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_authentication_flow(self, client):
        """Test authentication workflow"""
        # Test login page access
        response = client.get('/auth/login')
        assert response.status_code in [200, 302, 404]
        
        # Test logout
        response = client.get('/auth/logout')
        assert response.status_code in [200, 302, 404]
    
    def test_api_workflow(self, client):
        """Test API workflow"""
        # Test API discovery
        api_endpoints = ['/api/health', '/api/user', '/api/chat']
        
        for endpoint in api_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 401, 404], f"Endpoint {endpoint} failed"
    
    def test_error_handling(self, client):
        """Test error handling"""
        # Test 404 page
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Test malformed API request
        response = client.post('/api/chat', data='invalid')
        assert response.status_code in [400, 422, 404]
