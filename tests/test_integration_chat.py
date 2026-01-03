"""
Integration Tests for Chat Functionality - Phase 4.2 Testing
Tests the complete chat flow from frontend to EmotionAwareTherapeuticAssistant
"""
import pytest
from flask import Flask
from unittest.mock import Mock, patch

@pytest.fixture
def app():
    """Create test Flask app"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_session(client):
    """Create authenticated session"""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_123'
        sess['username'] = 'Test User'
    return client

class TestChatIntegration:
    """Integration tests for chat endpoints"""
    
    def test_chat_endpoint_requires_auth(self, client):
        """Test that chat endpoint requires authentication"""
        response = client.post('/api/chat', json={'message': 'Hello'})
        # Should either redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_chat_endpoint_with_demo_mode(self, client):
        """Test chat endpoint in demo mode"""
        with client.session_transaction() as sess:
            sess['user_id'] = 'demo'
        
        response = client.post('/api/chat', json={'message': 'Hello'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data
    
    @patch('services.emotion_aware_therapeutic_assistant.EmotionAwareTherapeuticAssistant')
    def test_chat_calls_therapeutic_assistant(self, mock_assistant_class, auth_session):
        """Test that chat endpoint calls EmotionAwareTherapeuticAssistant"""
        mock_assistant = Mock()
        mock_assistant.get_therapeutic_response.return_value = {
            'response': 'I understand how you feel.',
            'emotion': 'neutral',
            'skill_recommendations': []
        }
        mock_assistant_class.return_value = mock_assistant
        
        response = auth_session.post('/api/chat', json={
            'message': 'I am feeling anxious today'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['response'] == 'I understand how you feel.'
        assert data['emotion'] == 'neutral'
        
        # Verify the assistant was called
        mock_assistant.get_therapeutic_response.assert_called_once()
    
    def test_chat_validates_input(self, auth_session):
        """Test input validation"""
        # Empty message
        response = auth_session.post('/api/chat', json={'message': ''})
        assert response.status_code == 400
        
        # Missing message
        response = auth_session.post('/api/chat', json={})
        assert response.status_code == 400
        
        # Non-JSON request
        response = auth_session.post('/api/chat', data='not json')
        assert response.status_code == 400
    
    def test_chat_message_length_limit(self, auth_session):
        """Test message length validation"""
        long_message = 'a' * 10001  # Over 10000 char limit
        response = auth_session.post('/api/chat', json={'message': long_message})
        assert response.status_code == 413
    
    def test_chat_stores_conversation(self, auth_session):
        """Test that chat messages are stored"""
        # This would require database setup
        # For now, just verify the endpoint works
        response = auth_session.post('/api/chat', json={
            'message': 'Test message for storage'
        })
        assert response.status_code == 200

class TestTherapeuticEndpoints:
    """Integration tests for therapeutic endpoints"""
    
    def test_mood_entry_creation(self, auth_session):
        """Test creating a mood entry"""
        response = auth_session.post('/api/v1/therapeutic/mood', json={
            'mood': 7,
            'note': 'Feeling good today'
        })
        assert response.status_code in [200, 201]
    
    def test_thought_record_creation(self, auth_session):
        """Test creating a CBT thought record"""
        response = auth_session.post('/api/v1/therapeutic/cbt/thoughts', json={
            'situation': 'Meeting went poorly',
            'automaticThought': 'I am terrible at presentations',
            'emotion': 'anxious',
            'evidence': 'One person looked bored',
            'alternativeThought': 'Most people seemed engaged',
            'outcome': 'Feeling slightly better'
        })
        assert response.status_code in [200, 201]
    
    def test_dbt_skill_logging(self, auth_session):
        """Test logging a DBT skill"""
        response = auth_session.post('/api/v1/therapeutic/dbt/skills/log', json={
            'skill_name': 'TIPP',
            'category': 'Distress Tolerance',
            'situation': 'Feeling overwhelmed',
            'effectiveness': 8
        })
        assert response.status_code in [200, 201]

class TestConsolidatedAPI:
    """Tests for consolidated API routes"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_user_endpoint_authenticated(self, auth_session):
        """Test user endpoint with authentication"""
        response = auth_session.get('/api/v1/user')
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['id'] == 'test_user_123'
    
    def test_user_endpoint_guest(self, client):
        """Test user endpoint without authentication"""
        response = client.get('/api/v1/user')
        # Should return guest user or redirect
        assert response.status_code in [200, 302]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
