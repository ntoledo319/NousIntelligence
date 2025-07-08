import pytest
import json
from tests.base_test import BaseTestCase

class TestHealthAPI(BaseTestCase):
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test main health check"""
        response = self.client.get('/api/health/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
class TestAuthAPI(BaseTestCase):
    """Test authentication endpoints"""
    
    def test_login_missing_credentials(self):
        """Test login without credentials"""
        response = self.json_post('/api/auth/login', {})
        assert response.status_code == 400
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {'email': 'invalid@example.com', 'password': 'wrong'}
        response = self.json_post('/api/auth/login', data)
        assert response.status_code == 401

class TestTaskAPI(BaseTestCase):
    """Test task management endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        return 'test_token_123'
    
    def test_get_tasks_unauthorized(self):
        """Test getting tasks without auth"""
        response = self.client.get('/api/tasks/tasks')
        assert response.status_code == 401
    
    def test_create_task_missing_data(self, auth_token):
        """Test creating task without required data"""
        headers = self.auth_headers(auth_token)
        response = self.json_post('/api/tasks/tasks', {}, headers)
        assert response.status_code == 400

class TestMentalHealthAPI(BaseTestCase):
    """Test mental health endpoints"""
    
    def test_mood_entry_validation(self):
        """Test mood entry validation"""
        invalid_data = {'mood': 11}  # Invalid rating
        response = self.json_post('/api/mental_health/mood', invalid_data)
        assert response.status_code == 400
    
    def test_thought_record_creation(self):
        """Test thought record creation"""
        valid_data = {
            'situation': 'Test situation',
            'thoughts': 'Test thoughts',
            'emotions': 'anxious',
            'intensity': 7
        }
        response = self.json_post('/api/mental_health/thought-record', valid_data)
        # Should require auth
        assert response.status_code == 401
