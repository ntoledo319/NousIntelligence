"""
Unit tests for the API key management module

These tests verify the functionality of API key features including:
- Key generation and validation
- Rotation and revocation
- Rate limiting and scopes

@module: test_api_key_manager
@author: NOUS Development Team
"""
import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, request

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.api_key_manager import (
    generate_api_key,
    hash_api_key,
    check_api_key_scope,
    APIKeyInvalidError,
    APIKeyExpiredError,
    APIKeyRateLimitError,
    API_KEY_PREFIX_LENGTH,
    api_key_required
)

# Mock models we'll need
class MockUser:
    def __init__(self, id, is_admin=False):
        self.id = id
        self.admin = is_admin
    
    def is_administrator(self):
        return self.admin

class MockAPIKey:
    def __init__(self, user_id, key_prefix, key_hash, scopes="[\"read\"]", status="active"):
        self.id = 1
        self.user_id = user_id
        self.key_prefix = key_prefix
        self.key_hash = key_hash
        self.scopes = scopes
        self.status = status
        self.expires_at = None
        self.hourly_usage = 0
        self.daily_usage = 0
        self.hourly_reset_at = time.time()
        self.daily_reset_at = time.time()
        self.use_count = 0
    
    def record_usage(self):
        self.use_count += 1
        self.hourly_usage += 1
        self.daily_usage += 1
    
    def has_scope(self, scope):
        import json
        scopes = json.loads(self.scopes)
        return '*' in scopes or scope in scopes

class TestAPIKeyGeneration(unittest.TestCase):
    """Test cases for API key generation and hashing"""
    
    def test_generate_api_key(self):
        """Test API key generation"""
        full_key, prefix, secret = generate_api_key()
        
        # Check key format
        self.assertEqual(len(prefix), API_KEY_PREFIX_LENGTH)
        self.assertIn('.', full_key)
        self.assertEqual(full_key, f"{prefix}.{secret}")
        
        # Check that prefix is part of the full key
        self.assertTrue(full_key.startswith(prefix))
    
    def test_hash_api_key(self):
        """Test API key hashing"""
        key = "abcd1234.mysecretkey"
        hashed = hash_api_key(key)
        
        # Check hash properties
        self.assertTrue(isinstance(hashed, str))
        self.assertGreater(len(hashed), 32)  # SHA-256 is at least 32 chars
        
        # Same key should produce same hash
        self.assertEqual(hashed, hash_api_key(key))
        
        # Different keys should produce different hashes
        other_key = "abcd1234.othersecretkey"
        self.assertNotEqual(hashed, hash_api_key(other_key))

class TestScopeValidation(unittest.TestCase):
    """Test cases for API key scope validation"""
    
    def test_check_api_key_scope(self):
        """Test API key scope checking"""
        # Key with only read scope
        read_key = MockAPIKey(user_id=1, key_prefix="read1234", key_hash="hash", scopes='["read"]')
        self.assertTrue(check_api_key_scope(read_key, "read"))
        self.assertFalse(check_api_key_scope(read_key, "write"))
        
        # Key with multiple scopes
        multi_key = MockAPIKey(user_id=1, key_prefix="multi123", key_hash="hash", scopes='["read", "write"]')
        self.assertTrue(check_api_key_scope(multi_key, "read"))
        self.assertTrue(check_api_key_scope(multi_key, "write"))
        self.assertFalse(check_api_key_scope(multi_key, "admin"))
        
        # Key with wildcard scope
        admin_key = MockAPIKey(user_id=1, key_prefix="admin123", key_hash="hash", scopes='["*"]')
        self.assertTrue(check_api_key_scope(admin_key, "read"))
        self.assertTrue(check_api_key_scope(admin_key, "write"))
        self.assertTrue(check_api_key_scope(admin_key, "admin"))
        self.assertTrue(check_api_key_scope(admin_key, "any_scope"))
        
        # Inactive key
        inactive_key = MockAPIKey(user_id=1, key_prefix="inac1234", key_hash="hash", status="revoked", scopes='["read"]')
        inactive_key.is_active = lambda: False
        self.assertFalse(check_api_key_scope(inactive_key, "read"))

class TestAPIKeyDecorator(unittest.TestCase):
    """Test cases for API key decorator"""
    
    def setUp(self):
        """Set up test Flask app"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Create a test route with the decorator
        @self.app.route('/test')
        @api_key_required(scopes=['read'])
        def test_route():
            return jsonify({"success": True, "user_id": request.user_id})
        
        # Create a multi-scope test route
        @self.app.route('/admin')
        @api_key_required(scopes=['admin'])
        def admin_route():
            return jsonify({"success": True, "admin": True})
    
    @patch('utils.api_key_manager.validate_api_key')
    @patch('utils.api_key_manager.check_rate_limits')
    def test_api_key_required_valid(self, mock_check_rate_limits, mock_validate):
        """Test decorator with valid API key"""
        # Mock a valid API key
        api_key = MockAPIKey(user_id=123, key_prefix="test1234", key_hash="hash", scopes='["read"]')
        mock_validate.return_value = api_key
        mock_check_rate_limits.return_value = True
        
        # Test request with valid key
        with self.app.test_client() as client:
            response = client.get('/test', headers={'Authorization': 'Bearer test1234.secret'})
            
            # Check response
            self.assertEqual(response.status_code, 200)
            mock_validate.assert_called_once()
            mock_check_rate_limits.assert_called_once()
    
    @patch('utils.api_key_manager.validate_api_key')
    def test_api_key_required_missing(self, mock_validate):
        """Test decorator with missing API key"""
        with self.app.test_client() as client:
            response = client.get('/test')
            
            # Check response
            self.assertEqual(response.status_code, 401)
            mock_validate.assert_not_called()
    
    @patch('utils.api_key_manager.validate_api_key')
    def test_api_key_required_invalid(self, mock_validate):
        """Test decorator with invalid API key"""
        mock_validate.side_effect = APIKeyInvalidError("Invalid key")
        
        with self.app.test_client() as client:
            response = client.get('/test', headers={'Authorization': 'Bearer invalid.key'})
            
            # Check response
            self.assertEqual(response.status_code, 401)
            mock_validate.assert_called_once()
    
    @patch('utils.api_key_manager.validate_api_key')
    def test_api_key_required_expired(self, mock_validate):
        """Test decorator with expired API key"""
        mock_validate.side_effect = APIKeyExpiredError("Expired key")
        
        with self.app.test_client() as client:
            response = client.get('/test', headers={'Authorization': 'Bearer expired.key'})
            
            # Check response
            self.assertEqual(response.status_code, 401)
            mock_validate.assert_called_once()
    
    @patch('utils.api_key_manager.validate_api_key')
    @patch('utils.api_key_manager.check_rate_limits')
    def test_api_key_required_rate_limited(self, mock_check_rate_limits, mock_validate):
        """Test decorator with rate-limited API key"""
        # Mock a valid API key but exceed rate limits
        api_key = MockAPIKey(user_id=123, key_prefix="rate1234", key_hash="hash", scopes='["read"]')
        mock_validate.return_value = api_key
        mock_check_rate_limits.side_effect = APIKeyRateLimitError("Rate limit exceeded")
        
        with self.app.test_client() as client:
            response = client.get('/test', headers={'Authorization': 'Bearer rate1234.secret'})
            
            # Check response
            self.assertEqual(response.status_code, 429)
            mock_validate.assert_called_once()
            mock_check_rate_limits.assert_called_once()
    
    @patch('utils.api_key_manager.validate_api_key')
    @patch('utils.api_key_manager.check_rate_limits')
    def test_api_key_required_insufficient_scope(self, mock_check_rate_limits, mock_validate):
        """Test decorator with API key missing required scope"""
        # Mock a valid API key with insufficient scope
        api_key = MockAPIKey(user_id=123, key_prefix="read1234", key_hash="hash", scopes='["read"]')
        mock_validate.return_value = api_key
        mock_check_rate_limits.return_value = True
        
        with self.app.test_client() as client:
            response = client.get('/admin', headers={'Authorization': 'Bearer read1234.secret'})
            
            # Check response
            self.assertEqual(response.status_code, 403)
            mock_validate.assert_called_once()
            mock_check_rate_limits.assert_called_once()

if __name__ == '__main__':
    unittest.main() 