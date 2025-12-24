#!/usr/bin/env python3
"""
OAuth Callback Routes - Root level callback handling
Handles Google OAuth callbacks at the root level to match Google Cloud Console configuration
"""

import logging
import os
from flask import Blueprint, redirect, request, session, flash
from flask_login import login_user
from utils.google_oauth import oauth_service
from utils.rate_limiter import oauth_rate_limit

logger = logging.getLogger(__name__)

# Create callback blueprint for root-level callbacks
callback_bp = Blueprint('callback', __name__)

# Production Render deployment URL (hardcoded fallback)
RENDER_PRODUCTION_URL = "https://nousintelligence.onrender.com"

def get_deployment_callback_uri():
    """Get the correct callback URI for Render/Replit/local deployment"""
    # Check for Render deployment first
    if os.environ.get('RENDER'):
        render_url = os.environ.get('RENDER_EXTERNAL_URL')
        if render_url:
            return f"{render_url}/callback/google"
        hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        if hostname:
            return f"https://{hostname}/callback/google"
        # Fallback to hardcoded production URL for Render
        return f"{RENDER_PRODUCTION_URL}/callback/google"

    # Check for Replit deployment
    for env_var in ['REPL_URL', 'REPLIT_DOMAIN']:
        env_value = os.environ.get(env_var)
        if env_value:
            if not env_value.startswith('http'):
                return f"https://{env_value}/callback/google"
            return f"{env_value}/callback/google"

    # Fall back to request context with proper proxy detection
    scheme = 'https' if (request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https') else 'http'
    host = request.host
    return f"{scheme}://{host}/callback/google"


@callback_bp.route('/callback/google')
@oauth_rate_limit
def google_callback():
    """Handle Google OAuth callback at root level (/callback/google)"""
    try:
        logger.info("Google OAuth callback received at /callback/google")

        # Check if OAuth is configured
        if not oauth_service.is_configured():
            logger.error("Google OAuth is not configured")
            flash('Google OAuth is not configured.', 'error')
            return redirect('/')

        # Get the correct callback URI for token exchange (deployment-aware)
        callback_uri = get_deployment_callback_uri()

        logger.info(f"Processing OAuth callback with URI: {callback_uri}")
        
        # Handle OAuth callback
        user = oauth_service.handle_callback(callback_uri)
        
        if user:
            login_user(user, remember=True)
            logger.info(f"User {user.email} logged in successfully via Google OAuth")
            flash('Successfully logged in with Google!', 'success')
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                # Try to redirect to dashboard, fallback to home
                try:
                    from flask import url_for
                    return redirect(url_for('main.dashboard'))
                except Exception as e:
                    logger.error(f"Failed to update user settings: {e}")
                    return redirect('/')
        else:
            logger.error("OAuth callback failed - no user returned")
            flash('Authentication failed. Please try again.', 'error')
            return redirect('/')
            
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect('/')

# Export the blueprint
__all__ = ['callback_bp']