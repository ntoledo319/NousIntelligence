"""
Unit tests for the security_helper module

These tests verify the functionality of security features including:
- CSRF token generation and validation
- Rate limiting
- Input sanitization
- Secure hashing

@module: test_security_helper
@author: NOUS Development Team
"""
import unittest
import time
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to import from utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.security_helper import (
    generate_csrf_token,
    validate_csrf_token,
    sanitize_input,
    secure_hash,
    rate_limit
)

class TestCSRFProtection(unittest.TestCase):
    """Test cases for CSRF protection functionality"""
    
    @patch('utils.security_helper.session', {})
    def test_generate_csrf_token(self):
        """Test that CSRF token generation creates valid tokens and updates session"""
        token = generate_csrf_token()
        
        # Check token is non-empty string
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        
        # Check session was updated
        from utils.security_helper import session
        self.assertIn('csrf_token', session)
        self.assertIn('csrf_token_time', session)
        self.assertEqual(session['csrf_token'], token)
    
    @patch('utils.security_helper.session')
    def test_validate_csrf_token_valid(self, mock_session):
        """Test that a valid CSRF token validates correctly"""
        # Setup
        test_token = "valid_test_token"
        current_time = time.time()
        mock_session.__contains__.side_effect = lambda key: key in {
            'csrf_token', 'csrf_token_time'
        }
        mock_session.get.side_effect = lambda key: {
            'csrf_token': test_token,
            'csrf_token_time': current_time - 60  # 1 minute ago
        }.get(key)
        
        # Test valid token
        with patch('secrets.compare_digest', return_value=True):
            result = validate_csrf_token(test_token)
            self.assertTrue(result)
    
    @patch('utils.security_helper.session')
    def test_validate_csrf_token_invalid(self, mock_session):
        """Test that an invalid CSRF token fails validation"""
        # Setup
        test_token = "valid_test_token"
        invalid_token = "invalid_test_token"
        current_time = time.time()
        mock_session.__contains__.side_effect = lambda key: key in {
            'csrf_token', 'csrf_token_time'
        }
        mock_session.get.side_effect = lambda key: {
            'csrf_token': test_token,
            'csrf_token_time': current_time - 60  # 1 minute ago
        }.get(key)
        
        # Test invalid token
        with patch('secrets.compare_digest', return_value=False):
            result = validate_csrf_token(invalid_token)
            self.assertFalse(result)
    
    @patch('utils.security_helper.session')
    def test_validate_csrf_token_expired(self, mock_session):
        """Test that an expired CSRF token fails validation"""
        # Setup
        test_token = "valid_test_token"
        current_time = time.time()
        mock_session.__contains__.side_effect = lambda key: key in {
            'csrf_token', 'csrf_token_time'
        }
        mock_session.get.side_effect = lambda key: {
            'csrf_token': test_token,
            'csrf_token_time': current_time - 3600  # 1 hour ago (expired)
        }.get(key)
        
        # Test expired token
        result = validate_csrf_token(test_token)
        self.assertFalse(result)
    
    @patch('utils.security_helper.session')
    def test_validate_csrf_token_missing(self, mock_session):
        """Test that validation fails when token is missing from session"""
        # Setup
        mock_session.__contains__.return_value = False
        
        # Test missing token
        result = validate_csrf_token("any_token")
        self.assertFalse(result)

class TestInputSanitization(unittest.TestCase):
    """Test cases for input sanitization functionality"""
    
    def test_sanitize_input_html_tags(self):
        """Test that HTML tags are sanitized"""
        dirty_input = "<script>alert('XSS')</script>Hello"
        clean_output = sanitize_input(dirty_input)
        self.assertNotIn("<script>", clean_output)
        self.assertIn("Hello", clean_output)
    
    def test_sanitize_input_sql_injection(self):
        """Test that SQL injection attempts are sanitized"""
        dirty_input = "' OR 1=1; --"
        clean_output = sanitize_input(dirty_input)
        self.assertNotEqual(dirty_input, clean_output)
    
    def test_sanitize_input_preserves_valid(self):
        """Test that valid input is preserved"""
        valid_input = "Hello, this is a normal string 123!"
        clean_output = sanitize_input(valid_input)
        self.assertEqual(valid_input, clean_output)

class TestSecureHashing(unittest.TestCase):
    """Test cases for secure hashing functionality"""
    
    def test_secure_hash_different_inputs(self):
        """Test that different inputs produce different hashes"""
        hash1 = secure_hash("password1")
        hash2 = secure_hash("password2")
        self.assertNotEqual(hash1, hash2)
    
    def test_secure_hash_same_input(self):
        """Test that same input with same salt produces same hash"""
        salt = os.urandom(16)
        hash1 = secure_hash("password", salt)
        hash2 = secure_hash("password", salt)
        self.assertEqual(hash1, hash2)
    
    def test_secure_hash_with_salt(self):
        """Test that providing a salt works correctly"""
        salt = os.urandom(16)
        hash_with_salt = secure_hash("password", salt)
        self.assertIsNotNone(hash_with_salt)
        self.assertTrue(len(hash_with_salt) > 0)

if __name__ == '__main__':
    unittest.main() 