#!/usr/bin/env python3
"""
OAuth Callback Routes - Root level callback handling
Handles Google OAuth callbacks at the root level to match Google Cloud Console configuration

This route handler consolidates OAuth callbacks to a single endpoint: /callback/google
Configure this exact URL in your Google Cloud Console OAuth settings.
"""

import logging
from flask import Blueprint, redirect, request, session, flash, url_for
from flask_login import login_user
from utils.google_oauth import oauth_service

logger = logging.getLogger(__name__)

# Safe import of rate limiter
try:
    from utils.rate_limiter import oauth_rate_limit
except ImportError:
    # Fallback if rate limiter not available
    def oauth_rate_limit(f):
        return f

# Create callback blueprint for root-level callbacks
callback_bp = Blueprint('callback', __name__)


@callback_bp.route('/callback/google')
@oauth_rate_limit
def google_callback():
    """
    Handle Google OAuth callback at root level (/callback/google).

    This is the PRIMARY OAuth callback endpoint. Configure this exact URL
    in Google Cloud Console: https://your-domain.com/callback/google

    Flow:
    1. Validate OAuth state (CSRF protection)
    2. Exchange authorization code for access token
    3. Fetch user info from Google
    4. Create/update user in database
    5. Log user in and redirect to dashboard

    Returns:
        Redirect to dashboard on success, login page on failure
    """
    try:
        logger.info("Google OAuth callback received at /callback/google")

        # Check for OAuth errors from Google
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            logger.warning(f"OAuth error from Google: {error} - {error_description}")
            flash(f'Authentication failed: {error_description}', 'error')
            return redirect(url_for('auth.login'))

        # Check if OAuth is configured
        if not oauth_service or not oauth_service.is_configured():
            logger.error("Google OAuth is not configured - missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
            flash('Google OAuth is not configured. Please contact support.', 'error')
            return redirect('/')

        # Handle OAuth callback (auto-detects redirect URI)
        user = oauth_service.handle_callback()

        if user:
            login_user(user, remember=True)
            logger.info(f"User {user.email} logged in successfully via Google OAuth")
            flash('Successfully logged in with Google!', 'success')

            # Redirect to intended page or dashboard
            next_page = session.pop('oauth_next', None) or request.args.get('next')
            if next_page and next_page.startswith('/'):  # Security: only allow relative URLs
                return redirect(next_page)

            # Try dashboard, fallback to home
            try:
                return redirect(url_for('main.dashboard'))
            except Exception:
                return redirect('/')
        else:
            logger.error("OAuth callback succeeded but no user was created/returned")
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('auth.login'))

    except ValueError as e:
        # State validation or credential errors
        logger.error(f"OAuth validation error: {str(e)}")
        flash('Security validation failed. Please try logging in again.', 'error')
        return redirect(url_for('auth.login'))

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('auth.login'))

# Export the blueprint
__all__ = ['callback_bp']