"""
Enhanced OAuth Callback Handler
Fixes Issues 24-26: State validation, token expiry, user creation errors
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from flask import session, request, jsonify
import jwt
import secrets

logger = logging.getLogger(__name__)

class OAuthCallbackHandler:
    """Enhanced OAuth callback handling with comprehensive validation"""
    
    def __init__(self):
        self.max_callback_age = 600  # 10 minutes
    
    def handle_callback(self, authorization_code: str, state: str, error: str = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle OAuth callback with comprehensive validation
        
        Returns:
            Tuple of (success, result_data)
        """
        try:
            # Step 1: Handle OAuth errors first
            if error:
                return self._handle_oauth_error(error)
            
            # Step 2: Validate state parameter (CSRF protection)
            state_valid, state_error = self._validate_callback_state(state)
            if not state_valid:
                return False, {
                    'error': 'state_validation_failed',
                    'message': 'Security validation failed',
                    'details': state_error,
                    'recoverable': True
                }
            
            # Step 3: Exchange authorization code for tokens
            token_result = self._exchange_authorization_code(authorization_code)
            if not token_result['success']:
                return False, {
                    'error': 'token_exchange_failed',
                    'message': 'Failed to obtain access token',
                    'details': token_result.get('error', 'Unknown error'),
                    'recoverable': True
                }
            
            # Step 4: Validate token expiry
            token_data = token_result['data']
            if not self._validate_token_expiry(token_data):
                return False, {
                    'error': 'token_expired',
                    'message': 'Access token expired',
                    'details': 'Token expired before callback completion',
                    'recoverable': True
                }
            
            # Step 5: Get user information
            user_info_result = self._get_user_information(token_data['access_token'])
            if not user_info_result['success']:
                return False, {
                    'error': 'user_info_failed',
                    'message': 'Failed to retrieve user information',
                    'details': user_info_result.get('error', 'Unknown error'),
                    'recoverable': True
                }
            
            # Step 6: Create or update user with error handling
            user_result = self._handle_user_creation(user_info_result['data'], token_data)
            if not user_result['success']:
                return False, {
                    'error': 'user_creation_failed',
                    'message': 'Failed to create or update user account',
                    'details': user_result.get('error', 'Unknown error'),
                    'recoverable': False,  # May need admin intervention
                    'user_data': user_info_result['data']  # For debugging
                }
            
            # Step 7: Set up secure session
            session_result = self._setup_secure_session(user_result['user'], token_data)
            if not session_result['success']:
                return False, {
                    'error': 'session_setup_failed',
                    'message': 'Failed to establish secure session',
                    'details': session_result.get('error', 'Unknown error'),
                    'recoverable': True
                }
            
            # Success!
            return True, {
                'user': user_result['user'],
                'session_id': session_result['session_id'],
                'message': 'Authentication successful',
                'redirect_url': self._get_post_login_redirect()
            }
            
        except Exception as e:
            logger.error(f"OAuth callback handling failed: {e}", exc_info=True)
            return False, {
                'error': 'callback_exception',
                'message': 'An unexpected error occurred during authentication',
                'details': str(e),
                'recoverable': True
            }
    
    def _handle_oauth_error(self, error: str) -> Tuple[bool, Dict[str, Any]]:
        """Handle OAuth provider errors"""
        error_descriptions = {
            'access_denied': 'You cancelled the login process',
            'invalid_request': 'Invalid login request',
            'unauthorized_client': 'Login service not authorized',
            'unsupported_response_type': 'Login method not supported',
            'invalid_scope': 'Requested permissions not available',
            'server_error': 'Google login service error',
            'temporarily_unavailable': 'Login service temporarily unavailable'
        }
        
        message = error_descriptions.get(error, f'Unknown OAuth error: {error}')
        
        logger.warning(f"OAuth provider error: {error}")
        
        return False, {
            'error': f'oauth_{error}',
            'message': message,
            'details': f'OAuth provider returned error: {error}',
            'recoverable': error in ['access_denied', 'server_error', 'temporarily_unavailable']
        }
    
    def _validate_callback_state(self, state: str) -> Tuple[bool, Optional[str]]:
        """Validate OAuth state parameter with comprehensive checks"""
        try:
            # Check if state parameter exists
            if not state:
                return False, "Missing state parameter"
            
            # Get stored state from session
            stored_state = session.get('oauth_state')
            if not stored_state:
                return False, "No stored state found in session"
            
            # Validate state format (should be JWT or similar)
            if len(state) < 32:  # Minimum security requirement
                return False, "State parameter too short"
            
            # Compare states
            if not secrets.compare_digest(state, stored_state):
                return False, "State parameter mismatch"
            
            # Check state age (prevent replay attacks)
            state_timestamp = session.get('oauth_state_timestamp')
            if state_timestamp:
                state_age = datetime.utcnow().timestamp() - state_timestamp
                if state_age > self.max_callback_age:
                    return False, f"State parameter expired (age: {state_age}s)"
            
            # Clear used state
            session.pop('oauth_state', None)
            session.pop('oauth_state_timestamp', None)
            
            logger.info("OAuth state validation successful")
            return True, None
            
        except Exception as e:
            logger.error(f"State validation error: {e}")
            return False, f"State validation failed: {str(e)}"
    
    def _exchange_authorization_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        try:
            from utils.google_oauth import oauth_service
            
            if not oauth_service or not hasattr(oauth_service, 'exchange_code'):
                return {
                    'success': False,
                    'error': 'OAuth service not available'
                }
            
            # Exchange code for tokens
            token_data = oauth_service.exchange_code(code)
            
            if not token_data or 'access_token' not in token_data:
                return {
                    'success': False,
                    'error': 'No access token received'
                }
            
            # Validate required token fields
            required_fields = ['access_token', 'token_type']
            missing_fields = [field for field in required_fields if field not in token_data]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing token fields: {", ".join(missing_fields)}'
                }
            
            logger.info("Authorization code exchange successful")
            return {
                'success': True,
                'data': token_data
            }
            
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return {
                'success': False,
                'error': f'Token exchange error: {str(e)}'
            }
    
    def _validate_token_expiry(self, token_data: Dict[str, Any]) -> bool:
        """Validate token hasn't expired"""
        try:
            # Check if expires_in is provided
            expires_in = token_data.get('expires_in')
            if not expires_in:
                # No expiry info, assume valid for now
                logger.warning("No token expiry information provided")
                return True
            
            # Calculate expiry time
            issued_at = datetime.utcnow()
            expires_at = issued_at + timedelta(seconds=int(expires_in))
            
            # Check if already expired (with 30-second buffer)
            buffer_time = 30
            if expires_at <= datetime.utcnow() + timedelta(seconds=buffer_time):
                logger.warning(f"Token expires soon or already expired: {expires_at}")
                return False
            
            # Store expiry information
            session['token_expires_at'] = expires_at.isoformat()
            
            logger.info(f"Token valid until: {expires_at}")
            return True
            
        except Exception as e:
            logger.error(f"Token expiry validation failed: {e}")
            return False
    
    def _get_user_information(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        try:
            from utils.google_oauth import oauth_service
            
            if not oauth_service or not hasattr(oauth_service, 'get_user_info'):
                return {
                    'success': False,
                    'error': 'OAuth service not available'
                }
            
            # Get user info
            user_info = oauth_service.get_user_info(access_token)
            
            if not user_info:
                return {
                    'success': False,
                    'error': 'No user information received'
                }
            
            # Validate required user fields
            required_fields = ['id', 'email']
            missing_fields = [field for field in required_fields if field not in user_info]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing user fields: {", ".join(missing_fields)}'
                }
            
            logger.info(f"User information retrieved for: {user_info.get('email', 'unknown')}")
            return {
                'success': True,
                'data': user_info
            }
            
        except Exception as e:
            logger.error(f"User information retrieval failed: {e}")
            return {
                'success': False,
                'error': f'User info error: {str(e)}'
            }
    
    def _handle_user_creation(self, user_info: Dict[str, Any], token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user creation or update with comprehensive error handling"""
        try:
            from models import User
            from app import db
            
            # Extract user data
            google_id = user_info.get('id')
            email = user_info.get('email')
            name = user_info.get('name', '')
            picture = user_info.get('picture', '')
            
            if not google_id or not email:
                return {
                    'success': False,
                    'error': 'Missing required user data (ID or email)'
                }
            
            # Check if user already exists
            existing_user = User.query.filter(
                (User.google_id == google_id) | (User.email == email)
            ).first()
            
            if existing_user:
                # Update existing user
                try:
                    existing_user.name = name
                    existing_user.picture = picture
                    existing_user.google_id = google_id
                    existing_user.last_login = datetime.utcnow()
                    
                    # Update token if refresh token provided
                    if 'refresh_token' in token_data:
                        existing_user.refresh_token = token_data['refresh_token']
                    
                    db.session.commit()
                    
                    logger.info(f"Updated existing user: {email}")
                    return {
                        'success': True,
                        'user': existing_user,
                        'action': 'updated'
                    }
                    
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Failed to update user {email}: {e}")
                    return {
                        'success': False,
                        'error': f'User update failed: {str(e)}'
                    }
            
            else:
                # Create new user
                try:
                    new_user = User(
                        google_id=google_id,
                        email=email,
                        name=name,
                        picture=picture,
                        refresh_token=token_data.get('refresh_token'),
                        created_at=datetime.utcnow(),
                        last_login=datetime.utcnow()
                    )
                    
                    db.session.add(new_user)
                    db.session.commit()
                    
                    logger.info(f"Created new user: {email}")
                    return {
                        'success': True,
                        'user': new_user,
                        'action': 'created'
                    }
                    
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Failed to create user {email}: {e}")
                    return {
                        'success': False,
                        'error': f'User creation failed: {str(e)}'
                    }
            
        except Exception as e:
            logger.error(f"User handling failed: {e}")
            return {
                'success': False,
                'error': f'User handling error: {str(e)}'
            }
    
    def _setup_secure_session(self, user, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup secure session with comprehensive data"""
        try:
            # Generate unique session ID
            session_id = secrets.token_urlsafe(32)
            
            # Clear any existing session data
            session.clear()
            
            # Set user session data
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['google_id'] = user.google_id
            session['session_id'] = session_id
            session['login_timestamp'] = datetime.utcnow().isoformat()
            
            # Set token expiry if available
            if 'expires_in' in token_data:
                expires_at = datetime.utcnow() + timedelta(seconds=int(token_data['expires_in']))
                session['token_expires_at'] = expires_at.isoformat()
            
            # Set session security
            session.permanent = True
            
            logger.info(f"Secure session established for user: {user.email}")
            return {
                'success': True,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Session setup failed: {e}")
            return {
                'success': False,
                'error': f'Session setup error: {str(e)}'
            }
    
    def _get_post_login_redirect(self) -> str:
        """Get appropriate redirect URL after successful login"""
        # Check for intended destination
        next_url = session.get('next_url')
        if next_url and self._is_safe_redirect(next_url):
            session.pop('next_url', None)
            return next_url
        
        # Default redirect
        return '/dashboard'
    
    def _is_safe_redirect(self, url: str) -> bool:
        """Check if redirect URL is safe (no open redirects)"""
        if not url:
            return False
        
        # Only allow relative URLs or same-origin URLs
        if url.startswith('/') and not url.startswith('//'):
            return True
        
        # Could add more sophisticated same-origin checking here
        return False

# Global callback handler instance
oauth_callback_handler = OAuthCallbackHandler()