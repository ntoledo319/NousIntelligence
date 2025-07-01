"""
OAuth Error Handler
Fixes Issues 21-23: Generic errors, missing recovery, no user feedback
"""

import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from flask import flash, session, request
import traceback

logger = logging.getLogger(__name__)

class OAuthErrorType(Enum):
    """OAuth error types for specific handling"""
    INVALID_REQUEST = "invalid_request"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    ACCESS_DENIED = "access_denied"
    UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"
    INVALID_SCOPE = "invalid_scope"
    SERVER_ERROR = "server_error"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    STATE_MISMATCH = "state_mismatch"
    TOKEN_EXPIRED = "token_expired"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    USER_CANCELLED = "user_cancelled"

class OAuthErrorHandler:
    """Enhanced OAuth error handling with user feedback and recovery"""
    
    def __init__(self):
        self.error_messages = self._initialize_error_messages()
        self.recovery_actions = self._initialize_recovery_actions()
    
    def _initialize_error_messages(self) -> Dict[OAuthErrorType, Dict[str, str]]:
        """Initialize user-friendly error messages"""
        return {
            OAuthErrorType.INVALID_REQUEST: {
                'user': "Something went wrong with the login request. Please try again.",
                'technical': "OAuth request contains invalid parameters",
                'action': "Retry login"
            },
            OAuthErrorType.UNAUTHORIZED_CLIENT: {
                'user': "The login service is not properly configured. Please contact support.",
                'technical': "OAuth client not authorized for this request",
                'action': "Contact administrator"
            },
            OAuthErrorType.ACCESS_DENIED: {
                'user': "You cancelled the login process. Click 'Sign in with Google' to try again.",
                'technical': "User denied OAuth authorization",
                'action': "Retry login"
            },
            OAuthErrorType.UNSUPPORTED_RESPONSE_TYPE: {
                'user': "Login configuration error. Please contact support.",
                'technical': "OAuth response type not supported",
                'action': "Contact administrator"
            },
            OAuthErrorType.INVALID_SCOPE: {
                'user': "The requested permissions are not available. Please contact support.",
                'technical': "OAuth scope invalid or not permitted",
                'action': "Contact administrator"
            },
            OAuthErrorType.SERVER_ERROR: {
                'user': "Google's login service is temporarily unavailable. Please try again in a few minutes.",
                'technical': "OAuth server returned an error",
                'action': "Retry after delay"
            },
            OAuthErrorType.TEMPORARILY_UNAVAILABLE: {
                'user': "Login service is temporarily busy. Please try again in a moment.",
                'technical': "OAuth server temporarily unavailable",
                'action': "Retry after delay"
            },
            OAuthErrorType.STATE_MISMATCH: {
                'user': "Security check failed. Please try logging in again.",
                'technical': "OAuth state parameter mismatch (CSRF protection)",
                'action': "Retry login"
            },
            OAuthErrorType.TOKEN_EXPIRED: {
                'user': "Your session has expired. Please sign in again.",
                'technical': "OAuth token has expired",
                'action': "Re-authenticate"
            },
            OAuthErrorType.NETWORK_ERROR: {
                'user': "Network connection issue. Please check your internet and try again.",
                'technical': "Network error during OAuth request",
                'action': "Check connection and retry"
            },
            OAuthErrorType.CONFIGURATION_ERROR: {
                'user': "Login service configuration issue. Please contact support.",
                'technical': "OAuth client configuration error",
                'action': "Contact administrator"
            },
            OAuthErrorType.USER_CANCELLED: {
                'user': "Login was cancelled. Click 'Sign in with Google' when you're ready to continue.",
                'technical': "User cancelled OAuth flow",
                'action': "User action required"
            }
        }
    
    def _initialize_recovery_actions(self) -> Dict[OAuthErrorType, callable]:
        """Initialize automated recovery actions"""
        return {
            OAuthErrorType.STATE_MISMATCH: self._clear_oauth_session,
            OAuthErrorType.TOKEN_EXPIRED: self._clear_oauth_session,
            OAuthErrorType.NETWORK_ERROR: self._log_network_issue,
            OAuthErrorType.CONFIGURATION_ERROR: self._log_config_issue,
            OAuthErrorType.SERVER_ERROR: self._log_server_issue
        }
    
    def handle_oauth_error(self, error: Exception, context: Dict[str, Any] = None) -> Tuple[str, str, bool]:
        """
        Handle OAuth error with user feedback and recovery
        
        Returns:
            Tuple of (redirect_url, error_message, recoverable)
        """
        try:
            # Classify the error
            error_type = self._classify_error(error, context)
            
            # Get error details
            error_info = self.error_messages.get(error_type, self.error_messages[OAuthErrorType.SERVER_ERROR])
            
            # Log technical details
            self._log_error(error_type, error, context, error_info['technical'])
            
            # Attempt recovery
            recovery_attempted = self._attempt_recovery(error_type, context)
            
            # Provide user feedback
            user_message = self._format_user_message(error_info, recovery_attempted)
            flash(user_message, 'error')
            
            # Store recovery information in session
            self._store_recovery_info(error_type, error_info, recovery_attempted)
            
            # Determine redirect
            redirect_url = self._determine_redirect(error_type, recovery_attempted)
            
            # Check if error is recoverable
            recoverable = self._is_recoverable(error_type)
            
            return redirect_url, user_message, recoverable
            
        except Exception as handler_error:
            logger.error(f"Error in OAuth error handler: {handler_error}")
            return "/", "An unexpected error occurred. Please try again.", True
    
    def _classify_error(self, error: Exception, context: Dict[str, Any] = None) -> OAuthErrorType:
        """Classify error into specific OAuth error type"""
        error_str = str(error).lower()
        context = context or {}
        
        # Check for specific OAuth error codes
        if 'access_denied' in error_str:
            return OAuthErrorType.ACCESS_DENIED
        elif 'invalid_request' in error_str:
            return OAuthErrorType.INVALID_REQUEST
        elif 'unauthorized_client' in error_str:
            return OAuthErrorType.UNAUTHORIZED_CLIENT
        elif 'unsupported_response_type' in error_str:
            return OAuthErrorType.UNSUPPORTED_RESPONSE_TYPE
        elif 'invalid_scope' in error_str:
            return OAuthErrorType.INVALID_SCOPE
        elif 'server_error' in error_str:
            return OAuthErrorType.SERVER_ERROR
        elif 'temporarily_unavailable' in error_str:
            return OAuthErrorType.TEMPORARILY_UNAVAILABLE
        
        # Check for state mismatch
        if 'state' in error_str and ('mismatch' in error_str or 'invalid' in error_str):
            return OAuthErrorType.STATE_MISMATCH
        
        # Check for token expiry
        if 'token' in error_str and ('expired' in error_str or 'invalid' in error_str):
            return OAuthErrorType.TOKEN_EXPIRED
        
        # Check for network errors
        if any(keyword in error_str for keyword in ['network', 'connection', 'timeout', 'dns']):
            return OAuthErrorType.NETWORK_ERROR
        
        # Check for configuration errors
        if any(keyword in error_str for keyword in ['config', 'client_id', 'client_secret', 'redirect_uri']):
            return OAuthErrorType.CONFIGURATION_ERROR
        
        # Check if user cancelled (common pattern)
        if context.get('error') == 'access_denied' and context.get('error_description'):
            if 'user' in context['error_description'].lower():
                return OAuthErrorType.USER_CANCELLED
        
        # Default to server error
        return OAuthErrorType.SERVER_ERROR
    
    def _log_error(self, error_type: OAuthErrorType, error: Exception, context: Dict[str, Any], technical_msg: str) -> None:
        """Log error with appropriate level and details"""
        log_data = {
            'error_type': error_type.value,
            'error_message': str(error),
            'technical_message': technical_msg,
            'context': context,
            'user_agent': request.headers.get('User-Agent', 'Unknown') if request else 'Unknown',
            'ip_address': request.remote_addr if request else 'Unknown',
            'traceback': traceback.format_exc()
        }
        
        # Log at appropriate level
        if error_type in [OAuthErrorType.ACCESS_DENIED, OAuthErrorType.USER_CANCELLED]:
            logger.info(f"OAuth user action: {error_type.value}", extra=log_data)
        elif error_type in [OAuthErrorType.CONFIGURATION_ERROR, OAuthErrorType.UNAUTHORIZED_CLIENT]:
            logger.error(f"OAuth configuration error: {error_type.value}", extra=log_data)
        else:
            logger.warning(f"OAuth error: {error_type.value}", extra=log_data)
    
    def _attempt_recovery(self, error_type: OAuthErrorType, context: Dict[str, Any]) -> bool:
        """Attempt automated recovery for the error"""
        recovery_action = self.recovery_actions.get(error_type)
        
        if recovery_action:
            try:
                recovery_action(context)
                logger.info(f"Recovery action completed for {error_type.value}")
                return True
            except Exception as e:
                logger.error(f"Recovery action failed for {error_type.value}: {e}")
        
        return False
    
    def _clear_oauth_session(self, context: Dict[str, Any]) -> None:
        """Clear OAuth-related session data"""
        oauth_keys = ['oauth_state', 'oauth_token', 'oauth_user_info']
        for key in oauth_keys:
            session.pop(key, None)
        logger.info("OAuth session data cleared")
    
    def _log_network_issue(self, context: Dict[str, Any]) -> None:
        """Log network connectivity issue"""
        logger.warning("Network connectivity issue detected during OAuth", extra={
            'context': context,
            'recommendation': 'Check internet connection and Google service status'
        })
    
    def _log_config_issue(self, context: Dict[str, Any]) -> None:
        """Log configuration issue"""
        logger.error("OAuth configuration issue detected", extra={
            'context': context,
            'recommendation': 'Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables'
        })
    
    def _log_server_issue(self, context: Dict[str, Any]) -> None:
        """Log server-side issue"""
        logger.error("OAuth server issue detected", extra={
            'context': context,
            'recommendation': 'Check Google OAuth service status'
        })
    
    def _format_user_message(self, error_info: Dict[str, str], recovery_attempted: bool) -> str:
        """Format user-friendly error message"""
        message = error_info['user']
        
        if recovery_attempted:
            message += " We've attempted to fix the issue automatically."
        
        # Add helpful action
        if error_info['action'] != 'Contact administrator':
            message += f" {error_info['action']}."
        
        return message
    
    def _store_recovery_info(self, error_type: OAuthErrorType, error_info: Dict[str, str], recovery_attempted: bool) -> None:
        """Store recovery information in session for potential retry"""
        session['oauth_error_recovery'] = {
            'error_type': error_type.value,
            'technical_message': error_info['technical'],
            'recovery_attempted': recovery_attempted,
            'timestamp': str(request.environ.get('timestamp', 'unknown')) if request else 'unknown'
        }
    
    def _determine_redirect(self, error_type: OAuthErrorType, recovery_attempted: bool) -> str:
        """Determine appropriate redirect URL after error"""
        # For user-cancelled actions, stay on current page
        if error_type in [OAuthErrorType.ACCESS_DENIED, OAuthErrorType.USER_CANCELLED]:
            return request.referrer or "/"
        
        # For configuration errors, redirect to error page
        if error_type in [OAuthErrorType.CONFIGURATION_ERROR, OAuthErrorType.UNAUTHORIZED_CLIENT]:
            return "/error/oauth-config"
        
        # For recoverable errors, redirect to login
        if self._is_recoverable(error_type):
            return "/auth/login"
        
        # Default to home
        return "/"
    
    def _is_recoverable(self, error_type: OAuthErrorType) -> bool:
        """Check if error type is recoverable by user action"""
        recoverable_errors = [
            OAuthErrorType.ACCESS_DENIED,
            OAuthErrorType.USER_CANCELLED,
            OAuthErrorType.STATE_MISMATCH,
            OAuthErrorType.TOKEN_EXPIRED,
            OAuthErrorType.NETWORK_ERROR,
            OAuthErrorType.SERVER_ERROR,
            OAuthErrorType.TEMPORARILY_UNAVAILABLE
        ]
        return error_type in recoverable_errors
    
    def get_recovery_suggestions(self, error_type: OAuthErrorType) -> Dict[str, Any]:
        """Get recovery suggestions for the user"""
        error_info = self.error_messages.get(error_type, self.error_messages[OAuthErrorType.SERVER_ERROR])
        
        suggestions = {
            'user_message': error_info['user'],
            'technical_message': error_info['technical'],
            'action_required': error_info['action'],
            'recoverable': self._is_recoverable(error_type),
            'retry_safe': error_type in [
                OAuthErrorType.ACCESS_DENIED,
                OAuthErrorType.USER_CANCELLED,
                OAuthErrorType.NETWORK_ERROR,
                OAuthErrorType.SERVER_ERROR
            ]
        }
        
        return suggestions

# Global error handler instance
oauth_error_handler = OAuthErrorHandler()