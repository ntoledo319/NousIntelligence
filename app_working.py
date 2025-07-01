"""
NOUS Personal Assistant - Secure Flask Application
Production-ready app with Google OAuth authentication and comprehensive security
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask_login import LoginManager
# CORS not needed for basic setup
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with comprehensive backend stability features"""
    logger.info("🚀 Starting NOUS application creation...")

    # Initialize Flask app
    app = Flask(__name__)

    # Configure app from environment and config
    try:
        from config.app_config import AppConfig
        app.config.from_object(AppConfig)

        # Ensure database URI is set
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

        logger.info("✅ App configuration loaded successfully")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise

    # ProxyFix for deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Database initialization
    try:
        from database import init_database
        init_database(app)
    init_auth(app)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

    # User loader for Flask-Login
    def user_loader(user_id):
        """Load user by ID for Flask-Login"""
        try:
            from models.user import User
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"User loading error: {e}")
            return None

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.user_loader(user_loader)

    # Initialize Google OAuth
    try:
        from utils.google_oauth import init_oauth
        init_oauth(app)
        logger.info("✅ Google OAuth initialized successfully")
    except Exception as e:
        logger.warning(f"Google OAuth initialization failed: {e}")

    # Register all application blueprints
    try:
        from routes import register_all_blueprints
        register_all_blueprints(app)
        logger.info("✅ All blueprints registered successfully")
    except Exception as e:
        logger.error(f"Blueprint registration failed: {e}")
        raise

    # Direct demo route to bypass blueprint conflicts
    @app.route('/demo')
    def demo():
        """Demo route for NOUS application"""
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
            
            # Try to render the main app template
            try:
                return render_template('app.html', user=demo_user, demo_mode=True)
            except Exception as template_error:
                logger.warning(f"Template error: {template_error}")
                # Return simple HTML demo interface
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>NOUS Demo</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{ font-family: 'Inter', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8fafc; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .chat-container {{ border: 1px solid #e2e8f0; padding: 20px; margin: 20px 0; height: 400px; overflow-y: auto; background: white; border-radius: 8px; }}
                        .chat-form {{ display: flex; gap: 10px; }}
                        input {{ flex: 1; padding: 12px; border: 1px solid #cbd5e0; border-radius: 6px; }}
                        button {{ padding: 12px 24px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; }}
                        button:hover {{ background: #1d4ed8; }}
                        .message {{ margin: 10px 0; padding: 8px; border-radius: 4px; }}
                        .user-message {{ background: #eff6ff; border-left: 3px solid #2563eb; }}
                        .bot-message {{ background: #f0fdf4; border-left: 3px solid #10b981; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>🧠 NOUS Demo Mode</h1>
                        <p>Welcome, {demo_user['name']}! You're experiencing NOUS in demo mode.</p>
                    </div>
                    <div id="chat-container" class="chat-container">
                        <div class="message bot-message">
                            <strong>NOUS:</strong> Hello! I'm NOUS, your intelligent personal assistant. Try asking me a question or just start a conversation!
                        </div>
                    </div>
                    <form id="chat-form" class="chat-form">
                        <input type="text" id="message-input" placeholder="Type your message here..." required>
                        <button type="submit">Send</button>
                    </form>
                    <script>
                        document.getElementById('chat-form').addEventListener('submit', function(e) {{
                            e.preventDefault();
                            const messageInput = document.getElementById('message-input');
                            const message = messageInput.value.trim();
                            if (message) {{
                                // Add user message to chat
                                const container = document.getElementById('chat-container');
                                container.innerHTML += '<div class="message user-message"><strong>You:</strong> ' + message + '</div>';
                                container.scrollTop = container.scrollHeight;
                                messageInput.value = '';
                                
                                // Send to API
                                fetch('/api/v1/chat', {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{message: message, demo_mode: true}})
                                }})
                                .then(response => response.json())
                                .then(data => {{
                                    container.innerHTML += '<div class="message bot-message"><strong>NOUS:</strong> ' + data.response + '</div>';
                                    container.scrollTop = container.scrollHeight;
                                }})
                                .catch(error => {{
                                    container.innerHTML += '<div class="message bot-message"><strong>NOUS:</strong> I apologize, but I\'m having trouble connecting right now. Please try again.</div>';
                                    container.scrollTop = container.scrollHeight;
                                }});
                            }}
                        }});
                    </script>
                </body>
                </html>
                """
        except Exception as e:
            logger.error(f"Demo route error: {e}")
            return f"Demo mode error: {str(e)}", 500

    # Security headers for public deployment
    @app.after_request
    def add_security_headers(response):
        """Add security headers for public deployment"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    logger.info("✅ NOUS application created successfully")
    return app

# Global app instance for deployment
try:
    app = create_app()
    logger.info("🎯 NOUS application ready for deployment")
except Exception as e:
    logger.error(f"❌ Application creation failed: {e}")
    raise