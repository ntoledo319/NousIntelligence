"""
Main Routes - Landing Page and Core Application Routes
Handles the main application landing page and core routing
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify

# Import rate limiting
try:
    from utils.rate_limiter import rate_limit
except ImportError:
    # Fallback if rate limiter not available
    def rate_limit(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

logger = logging.getLogger(__name__)

# Create main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@rate_limit(limit=30, window=60)  # 30 requests per minute
def index():
    """Landing page for NOUS application"""
    try:
        # Check if user is authenticated
        user_authenticated = 'user' in session and session['user'] is not None
        
        # Check OAuth availability by checking if service is configured
        oauth_available = False
        try:
            from utils.google_oauth import oauth_service
            oauth_available = oauth_service and oauth_service.is_configured()
        except Exception as e:
            logger.warning(f"OAuth availability check failed: {e}")
            oauth_available = False
        
        # Enhanced error logging with request context
        logger.info(f"Landing page accessed - User authenticated: {user_authenticated}, OAuth available: {oauth_available}")
        
        return render_template('landing.html', 
                             user_authenticated=user_authenticated,
                             oauth_available=oauth_available)
    except Exception as e:
        logger.error(f"Landing page error: {e}", exc_info=True)
        # Provide fallback context for error cases
        return render_template('landing.html', 
                             user_authenticated=False,
                             oauth_available=False,
                             error_occurred=True)

@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard - redirects to chat for demo"""
    # Set demo user in session
    session['user'] = {
        'id': 'demo_user_123',
        'name': 'Demo User',
        'email': 'demo@nous.app',
        'demo_mode': True
    }
    return redirect('/chat')

@main_bp.route('/seed-dashboard')
def seed_dashboard():
    """SEED Optimization Dashboard"""
    try:
        # Check if user is authenticated
        user_authenticated = 'user' in session and session['user'] is not None
        
        return render_template('seed_dashboard.html', 
                             user_authenticated=user_authenticated)
    except Exception as e:
        logger.error(f"SEED dashboard error: {e}")
        return render_template('seed_dashboard.html', 
                             user_authenticated=False)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@main_bp.route('/demo')
def demo():
    """Demo page for NOUS"""
    try:
        # Create demo user session
        demo_user = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True,
            'is_guest': True,
            'login_time': datetime.now().isoformat()
        }
        session['user'] = demo_user
        
        # Check if app.html template exists, fallback to chat.html
        try:
            return render_template('app.html', user=demo_user, demo_mode=True)
        except Exception as template_error:
            logger.warning(f"app.html template error: {template_error}, trying chat.html")
            try:
                return render_template('chat.html', user=demo_user, demo_mode=True)
            except Exception as chat_error:
                logger.warning(f"chat.html template error: {chat_error}, using simple demo")
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>NOUS Demo</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                    <h1>🧠 NOUS Demo Mode</h1>
                    <p>Welcome, {demo_user['name']}! You're now in demo mode.</p>
                    <div id="chat-container" style="border: 1px solid #ccc; padding: 20px; margin: 20px 0; height: 400px; overflow-y: auto;"></div>
                    <form id="chat-form" style="display: flex; gap: 10px;">
                        <input type="text" id="message-input" placeholder="Type your message..." style="flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">
                        <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px;">Send</button>
                    </form>
                    <script>
                        document.getElementById('chat-form').addEventListener('submit', function(e) {{
                            e.preventDefault();
                            const message = document.getElementById('message-input').value;
                            if (message.trim()) {{
                                fetch('/api/chat', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{message: message, demo_mode: true}})
                                }})
                                .then(response => response.json())
                                .then(data => {{
                                    const container = document.getElementById('chat-container');
                                    container.innerHTML += '<div><strong>You:</strong> ' + message + '</div>';
                                    container.innerHTML += '<div><strong>NOUS:</strong> ' + data.response + '</div>';
                                    container.scrollTop = container.scrollHeight;
                                    document.getElementById('message-input').value = '';
                                }})
                                .catch(error => console.error('Error:', error));
                            }}
                        }});
                    </script>
                </body>
                </html>
                """
    except Exception as e:
        logger.error(f"Demo page error: {e}")
        return f"Demo mode error: {str(e)}", 500

# Export the blueprint
__all__ = ['main_bp']