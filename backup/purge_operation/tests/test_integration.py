"""
@module test_integration
@description Integration tests for end-to-end workflows
@author AI Assistant
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import pytest
from app import app
from models import User, Conversation, Message, KnowledgeItem

class TestIntegrationFlows(unittest.TestCase):
    """Integration test suite for end-to-end workflows."""
    
    def setUp(self):
        """Set up test client and mocks before each test."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create test database session
        self.patcher = patch('app.db.session')
        self.mock_session = self.patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
    
    @patch('app.get_user_from_session')
    @patch('utils.ai_helper.get_ai_response')
    def test_conversation_workflow(self, mock_ai_response, mock_get_user):
        """Test end-to-end conversation workflow."""
        # Mock authenticated user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_get_user.return_value = mock_user
        
        # Mock AI response
        mock_ai_response.return_value = {
            "response": "This is a test AI response",
            "tokens_used": 10
        }
        
        # Mock database interactions
        mock_conversation = MagicMock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Test Conversation"
        
        # Mock session query results
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        mock_query = self.mock_session.query.return_value
        mock_query.filter.return_value.first.return_value = mock_conversation
        
        # Step 1: Start a new conversation
        test_data = {
            "message": "Hello, this is a test message",
            "conversation_id": None
        }
        response = self.app.post('/api/conversation', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Assertions for first step
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('response', response_data)
        self.assertIn('conversation_id', response_data)
        
        conversation_id = response_data['conversation_id']
        
        # Step 2: Continue the conversation
        test_data = {
            "message": "This is a follow-up message",
            "conversation_id": conversation_id
        }
        response = self.app.post('/api/conversation', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Assertions for second step
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('response', response_data)
        
        # Step 3: Get conversation history
        response = self.app.get(f'/api/conversation/{conversation_id}')
        
        # Assertions for history
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('messages', response_data)
    
    @patch('app.get_user_from_session')
    @patch('utils.knowledge_helper.search_knowledge')
    @patch('utils.knowledge_helper.add_knowledge_item')
    def test_knowledge_workflow(self, mock_add_knowledge, mock_search_knowledge, mock_get_user):
        """Test end-to-end knowledge base workflow."""
        # Mock authenticated user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_get_user.return_value = mock_user
        
        # Mock search response
        mock_search_knowledge.return_value = {
            "results": [
                {"id": 1, "title": "Test Item", "content": "Test content"}
            ]
        }
        
        # Mock add knowledge response
        mock_add_knowledge.return_value = {"id": 2, "success": True}
        
        # Step 1: Add knowledge item
        test_data = {
            "title": "New Knowledge Item",
            "content": "This is test content for knowledge integration",
            "source": "Integration Test"
        }
        response = self.app.post('/api/knowledge/add', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Assertions for first step
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # Step 2: Search knowledge
        test_data = {
            "query": "test knowledge"
        }
        response = self.app.post('/api/knowledge/search', 
                                data=json.dumps(test_data),
                                content_type='application/json')
        
        # Assertions for second step
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('results', response_data)

if __name__ == '__main__':
    unittest.main() 