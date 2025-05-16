"""
Unit tests for the JWT authentication module

These tests verify the functionality of JWT authentication features including:
- Token generation
- Token validation
- Token blacklisting
- Authentication decorators

@module: test_jwt_auth
@author: NOUS Development Team
"""
import unittest
import time
import sys
import os
import jwt
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, g

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.jwt_auth import (
    generate_jwt_token,
    validate_jwt_token,
    blacklist_token,
    cleanup_blacklist,
    jwt_required,
    refresh_token_required,
    get_token_from_request,
    JWT_BLACKLIST,
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)

class TestJWTGeneration(unittest.TestCase):
    """Test cases for JWT token generation"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any existing tokens from blacklist
        JWT_BLACKLIST.clear()
    
    def test_generate_access_token(self):
        """Test generating an access token"""
        user_id = 123
        token, expires_at = generate_jwt_token(user_id, 'access')
        
        # Verify token is a string and expires_at is a timestamp
        self.assertIsInstance(token, str)
        self.assertIsInstance(expires_at, float)
        
        # Decode token to verify contents
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        self.assertEqual(payload['sub'], user_id)
        self.assertEqual(payload['type'], 'access')
        self.assertIn('exp', payload)
        self.assertIn('iat', payload)
    
    def test_generate_refresh_token(self):
        """Test generating a refresh token"""
        user_id = 123
        token, expires_at = generate_jwt_token(user_id, 'refresh')
        
        # Verify token is a string and expires_at is a timestamp
        self.assertIsInstance(token, str)
        self.assertIsInstance(expires_at, float)
        
        # Decode token to verify contents
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        self.assertEqual(payload['sub'], user_id)
        self.assertEqual(payload['type'], 'refresh')
        self.assertIn('exp', payload)
        self.assertIn('iat', payload)
    
    def test_token_expiry(self):
        """Test that token expiry time is set correctly"""
        user_id = 123
        
        # Generate access token
        token, expires_at = generate_jwt_token(user_id, 'access')
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check expiry time (should be around 15 minutes from now)
        now = datetime.utcnow().timestamp()
        self.assertAlmostEqual(payload['exp'] - now, 15 * 60, delta=10)  # Within 10 seconds
        
        # Generate refresh token
        token, expires_at = generate_jwt_token(user_id, 'refresh')
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check expiry time (should be around 7 days from now)
        now = datetime.utcnow().timestamp()
        self.assertAlmostEqual(payload['exp'] - now, 7 * 24 * 60 * 60, delta=10)  # Within 10 seconds
    
    def test_invalid_token_type(self):
        """Test that an invalid token type raises ValueError"""
        with self.assertRaises(ValueError):
            generate_jwt_token(123, 'invalid')

class TestJWTValidation(unittest.TestCase):
    """Test cases for JWT token validation"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any existing tokens from blacklist
        JWT_BLACKLIST.clear()
    
    def test_validate_valid_token(self):
        """Test validating a valid token"""
        user_id = 123
        token, _ = generate_jwt_token(user_id, 'access')
        
        # Validate token
        payload = validate_jwt_token(token)
        
        self.assertEqual(payload['sub'], user_id)
        self.assertEqual(payload['type'], 'access')
    
    def test_validate_expired_token(self):
        """Test validating an expired token"""
        # Create a token that's already expired
        user_id = 123
        now = datetime.utcnow()
        expired_time = now - timedelta(minutes=5)
        
        payload = {
            'sub': user_id,
            'iat': expired_time.timestamp(),
            'exp': expired_time.timestamp(),
            'type': 'access'
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        # Validate token - should raise ExpiredSignatureError
        with self.assertRaises(jwt.ExpiredSignatureError):
            validate_jwt_token(token)
    
    def test_validate_invalid_token(self):
        """Test validating an invalid token"""
        # Create a token with an invalid signature
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEyMywiaWF0IjoxNjE5NzE2ODAwLCJleHAiOjk5OTk5OTk5OTl9.INVALID_SIGNATURE"
        
        # Validate token - should raise InvalidTokenError
        with self.assertRaises(jwt.InvalidTokenError):
            validate_jwt_token(token)
    
    def test_validate_blacklisted_token(self):
        """Test validating a blacklisted token"""
        user_id = 123
        token, _ = generate_jwt_token(user_id, 'access')
        
        # Blacklist the token
        blacklist_token(token)
        
        # Validate token - should raise InvalidTokenError
        with self.assertRaises(jwt.InvalidTokenError):
            validate_jwt_token(token)

class TestTokenBlacklisting(unittest.TestCase):
    """Test cases for token blacklisting"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any existing tokens from blacklist
        JWT_BLACKLIST.clear()
    
    def test_blacklist_token(self):
        """Test blacklisting a token"""
        user_id = 123
        token, _ = generate_jwt_token(user_id, 'access')
        
        # Blacklist the token
        blacklist_token(token)
        
        # Check token is in blacklist
        self.assertIn(token, JWT_BLACKLIST)
    
    def test_cleanup_blacklist(self):
        """Test cleaning up the blacklist"""
        # Create an expired token
        user_id = 123
        now = datetime.utcnow()
        expired_time = now - timedelta(minutes=5)
        
        payload = {
            'sub': user_id,
            'iat': expired_time.timestamp(),
            'exp': expired_time.timestamp(),
            'type': 'access'
        }
        
        expired_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        # Create a valid token
        valid_token, _ = generate_jwt_token(user_id, 'access')
        
        # Add both to blacklist
        blacklist_token(expired_token)
        blacklist_token(valid_token)
        
        # Run cleanup
        cleanup_blacklist()
        
        # Check that expired token was removed but valid token remains
        self.assertNotIn(expired_token, JWT_BLACKLIST)
        self.assertIn(valid_token, JWT_BLACKLIST)

class TestAuthDecorators(unittest.TestCase):
    """Test cases for authentication decorators"""
    
    def setUp(self):
        """Set up test environment"""
        # Clear any existing tokens from blacklist
        JWT_BLACKLIST.clear()
        
        # Create Flask app for testing
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        
        # Define test routes
        @self.app.route('/protected')
        @jwt_required
        def protected():
            return jsonify({"user_id": g.user_id})
        
        @self.app.route('/refresh')
        @refresh_token_required
        def refresh():
            return jsonify({"user_id": g.user_id})
    
    def test_jwt_required_valid_token(self):
        """Test accessing a protected route with a valid token"""
        with self.app.test_request_context():
            # Generate token
            user_id = 123
            token, _ = generate_jwt_token(user_id, 'access')
            
            # Make request with token
            response = self.client.get('/protected', headers={'Authorization': f'Bearer {token}'})
            
            # Check response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['user_id'], user_id)
    
    def test_jwt_required_missing_token(self):
        """Test accessing a protected route without a token"""
        with self.app.test_request_context():
            # Make request without token
            response = self.client.get('/protected')
            
            # Check response
            self.assertEqual(response.status_code, 401)
            self.assertIn('error', response.json)
            self.assertEqual(response.json['error'], 'Authentication required')
    
    def test_jwt_required_invalid_token(self):
        """Test accessing a protected route with an invalid token"""
        with self.app.test_request_context():
            # Make request with invalid token
            response = self.client.get('/protected', headers={'Authorization': 'Bearer invalid_token'})
            
            # Check response
            self.assertEqual(response.status_code, 401)
            self.assertIn('error', response.json)
            self.assertEqual(response.json['error'], 'Invalid token')
    
    def test_refresh_token_required(self):
        """Test accessing a refresh route with a refresh token"""
        with self.app.test_request_context():
            # Generate token
            user_id = 123
            token, _ = generate_jwt_token(user_id, 'refresh')
            
            # Make request with token
            response = self.client.get('/refresh', headers={'Authorization': f'Bearer {token}'})
            
            # Check response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['user_id'], user_id)
    
    def test_refresh_token_required_with_access_token(self):
        """Test accessing a refresh route with an access token (should fail)"""
        with self.app.test_request_context():
            # Generate access token
            user_id = 123
            token, _ = generate_jwt_token(user_id, 'access')
            
            # Make request with access token
            response = self.client.get('/refresh', headers={'Authorization': f'Bearer {token}'})
            
            # Check response
            self.assertEqual(response.status_code, 401)
            self.assertIn('error', response.json)
            self.assertEqual(response.json['error'], 'Invalid token type')

class TestTokenExtraction(unittest.TestCase):
    """Test cases for token extraction"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a Flask app and context
        self.app = Flask(__name__)
    
    def test_extract_from_header(self):
        """Test extracting token from Authorization header"""
        with self.app.test_request_context(headers={'Authorization': 'Bearer test_token'}):
            token = get_token_from_request()
            self.assertEqual(token, 'test_token')
    
    def test_extract_from_form(self):
        """Test extracting token from form data"""
        with self.app.test_request_context(method='POST', data={'token': 'test_token'}):
            token = get_token_from_request()
            self.assertEqual(token, 'test_token')
    
    def test_extract_from_json(self):
        """Test extracting token from JSON data"""
        with self.app.test_request_context(method='POST', 
                                         json={'token': 'test_token'},
                                         content_type='application/json'):
            token = get_token_from_request()
            self.assertEqual(token, 'test_token')
    
    def test_extract_from_query_params(self):
        """Test extracting token from query parameters"""
        with self.app.test_request_context('/?token=test_token'):
            token = get_token_from_request()
            self.assertEqual(token, 'test_token')
    
    def test_missing_token(self):
        """Test behavior when no token is present"""
        with self.app.test_request_context():
            token = get_token_from_request()
            self.assertIsNone(token)

if __name__ == '__main__':
    unittest.main() 