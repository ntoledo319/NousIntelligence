"""
@module test_api_routes
@description Unit tests for critical API endpoints
@author AI Assistant
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import pytest
from app import app

class TestAPIRoutes(unittest.TestCase):
    """Test suite for critical API endpoints."""
    
    def setUp(self):
        """Set up test client and mocks before each test."""
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('app.get_user_from_session')
    def test_conversation_api(self, mock_get_user):
        """Test the conversation API endpoint."""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_get_user.return_value = mock_user
        
        # Test POST request to conversation endpoint
        test_data = {
            "message": "Hello, test message",
            "conversation_id": None
        }
        response = self.app.post('/api/conversation', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('response', response_data)
        self.assertIn('conversation_id', response_data)
    
    @patch('app.get_user_from_session')
    def test_knowledge_api(self, mock_get_user):
        """Test the knowledge search API endpoint."""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_get_user.return_value = mock_user
        
        # Test POST request to knowledge search endpoint
        test_data = {
            "query": "test knowledge query"
        }
        response = self.app.post('/api/knowledge/search', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('results', response_data)
    
    @patch('app.get_user_from_session')
    def test_user_preferences_api(self, mock_get_user):
        """Test the user preferences API endpoints."""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.preferences = {}
        mock_get_user.return_value = mock_user
        
        # Test GET request to user preferences endpoint
        response = self.app.get('/api/user/preferences')
        
        # Assertions for GET
        self.assertEqual(response.status_code, 200)
        
        # Test PUT request to update user preferences
        test_data = {
            "theme": "dark",
            "notifications_enabled": True
        }
        response = self.app.put('/api/user/preferences',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        # Assertions for PUT
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])

    @patch('app.get_user_from_session')
    def test_unauthorized_access(self, mock_get_user):
        """Test API endpoints with unauthorized access."""
        # Mock unauthenticated user
        mock_get_user.return_value = None
        
        # Test unauthorized access to protected endpoint
        response = self.app.get('/api/user/preferences')
        
        # Assertions
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)

if __name__ == '__main__':
    unittest.main() 