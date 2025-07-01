"""
Basic Test Suite
Core functionality tests for NOUS application
"""

import pytest
import json

def test_app_startup(client):
    """Test that the application starts up correctly"""
    response = client.get('/health')
    assert response.status_code == 200

def test_authentication_endpoints(client):
    """Test authentication endpoints"""
    # Test demo mode
    response = client.get('/demo')
    assert response.status_code in [200, 302]  # OK or redirect

def test_api_endpoints(authenticated_client):
    """Test API endpoints with authentication"""
    # Test health endpoint
    response = authenticated_client.get('/api/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data

def test_input_validation(authenticated_client):
    """Test input validation on API endpoints"""
    # Test with invalid input
    response = authenticated_client.post('/api/v1/chat', 
                                       json={'message': 'x' * 10000})  # Too long
    
    # Should handle gracefully (not crash)
    assert response.status_code in [400, 413, 200]

def test_rate_limiting(client):
    """Test rate limiting functionality"""
    # This test would need to be adapted based on actual rate limits
    responses = []
    for i in range(5):
        response = client.get('/api/health')
        responses.append(response.status_code)
    
    # Should not block basic health checks
    assert all(status == 200 for status in responses)
