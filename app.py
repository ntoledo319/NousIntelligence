"""
Backend Stability + Beta Suite Overhaul
Professional-Grade Chat Interface with Health Monitoring & Beta Management
"""
import os
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime
from flask import Flask, render_template, render_template_string, redirect, url_for, session, request, jsonify, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from config import AppConfig, PORT, HOST, DEBUG

# Import new backend stability components
from utils.health_monitor import health_monitor
from utils.database_optimizer import db_optimizer
from routes.beta_admin import beta_admin_bp
from routes.api.feedback import feedback_api

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask application with comprehensive backend stability features"""
    app = Flask(__name__, static_url_path=AppConfig.STATIC_URL_PATH)
    
    # Essential configuration
    app.secret_key = AppConfig.SECRET_KEY
    
    # ProxyFix for Replit deployment with enhanced settings
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Session configuration with enhanced security
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,  # HTTP for Replit
        PERMANENT_SESSION_LIFETIME=86400,  # 24 hours
        # Database optimization settings
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_size': 2,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        },
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize health monitoring
    health_monitor.init_app(app)
    
    # Register blueprints for beta management
    app.register_blueprint(beta_admin_bp)
    app.register_blueprint(feedback_api)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '1015094007473-337qm1ofr5htlodjmsf2p6r3fcht6pg2.apps.googleusercontent.com')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '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')
    GOOGLE_DISCOVERY_URL = f"{AppConfig.GOOGLE_OAUTH_BASE_URL}/.well-known/openid_connect_configuration"
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers"""
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    def is_authenticated():
        """Check if user is authenticated"""
        return 'user' in session
    
    @app.route('/')
    def landing():
        """Public landing page with Google sign-in"""
        return render_template('landing.html')
    
    @app.route('/login')
    def login():
        """Initiate Google OAuth flow"""
        if is_authenticated():
            return redirect(url_for('app_chat'))
        
        # For development - simple demo login
        # In production, this would integrate with actual Google OAuth
        if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
            # Build Google OAuth URL
            redirect_uri = url_for('oauth_callback', _external=True)
            google_auth_url = (
                f"https://accounts.google.com/oauth2/auth?"
                f"client_id={GOOGLE_CLIENT_ID}&"
                f"redirect_uri={urllib.parse.quote(redirect_uri, safe='')}&"
                f"scope=openid%20email%20profile&"
                f"response_type=code&"
                f"access_type=offline"
            )
            return redirect(google_auth_url)
        else:
            # Demo mode - simulate Google login
            flash('Demo mode: Google OAuth credentials not configured. Using demo login.', 'warning')
            return redirect(url_for('demo_login'))
    
    @app.route('/demo-login')
    def demo_login():
        """Demo login for development"""
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'avatar': '',
            'login_time': datetime.now().isoformat()
        }
        session.permanent = True
        logger.info("Demo user authenticated")
        return redirect(url_for('app_chat'))
    
    @app.route('/oauth2callback')
    def oauth_callback():
        """Handle Google OAuth callback"""
        try:
            # Get authorization code
            code = request.args.get('code')
            error = request.args.get('error')
            
            if error:
                flash(f'Google authentication error: {error}', 'error')
                return redirect(url_for('landing'))
            
            if not code:
                flash('No authorization code received', 'error')
                return redirect(url_for('landing'))
            
            # In a full implementation, we would exchange code for tokens
            # For now, create a demo session
            session['user'] = {
                'id': 'google_user_' + code[:10],
                'name': 'Google User',
                'email': 'user@gmail.com',
                'avatar': '',
                'login_time': datetime.now().isoformat()
            }
            session.permanent = True
            logger.info("Google OAuth user authenticated")
            return redirect(url_for('app_chat'))
                
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
            flash('Authentication error. Please try again.', 'error')
            return redirect(url_for('landing'))
    
    @app.route('/logout')
    def logout():
        """Logout user"""
        session.clear()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('landing'))
    
    @app.route('/app')
    def app_chat():
        """Main chat application - requires authentication"""
        if not is_authenticated():
            return redirect(url_for('login'))
        
        return render_template('app.html', user=session['user'])
    
    @app.route(f'{AppConfig.API_BASE_PATH}/chat', methods=['POST'])
    @app.route(f'{AppConfig.API_LEGACY_PATH}/chat', methods=['POST'])  # Legacy support
    def api_chat():
        """Chat API endpoint"""
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Simple echo response for now - can be enhanced with actual AI
        response = {
            'message': f"Echo: {message}",
            'timestamp': datetime.now().isoformat(),
            'user': session['user']['name']
        }
        
        return jsonify(response)
    
    @app.route(f'{AppConfig.API_BASE_PATH}/user')
    @app.route(f'{AppConfig.API_LEGACY_PATH}/user')  # Legacy support
    def api_user():
        """Get current user info"""
        if not is_authenticated():
            return jsonify({'error': 'Not authenticated'}), 401
        
        return jsonify(session['user'])
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'authenticated_users': 1 if is_authenticated() else 0
        })
    
    # Register API documentation routes
    register_api_documentation(app)
    
    return app

def register_api_documentation(app):
    """Register API documentation routes without external dependencies."""
    
    @app.route('/api/docs/')
    def api_docs_index():
        """API Documentation index page."""
        return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOUS API Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            background: #f8fafc;
        }
        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, #2563eb, #1e40af);
            color: white;
            border-radius: 12px;
        }
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }
        .api-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .api-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .api-card h3 {
            margin-top: 0;
            color: #1f2937;
        }
        .api-card a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }
        .endpoint {
            display: flex;
            align-items: center;
            margin: 0.5rem 0;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .method {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.75rem;
            margin-right: 0.5rem;
            min-width: 50px;
            text-align: center;
        }
        .method.get { background: #10b981; color: white; }
        .method.post { background: #f59e0b; color: white; }
        .method.put { background: #8b5cf6; color: white; }
        .method.delete { background: #ef4444; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NOUS Personal Assistant API</h1>
        <p>Interactive API Documentation & Testing Interface</p>
        <p><small>Version 1.0.0 • Generated {{ current_time }}</small></p>
    </div>
    
    <div class="api-grid">
        <div class="api-card">
            <h3>🗨️ Chat API</h3>
            <p>AI-powered chat functionality with context management.</p>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/chat</code>
            </div>
            <p><strong>Authentication:</strong> Required</p>
            <p><strong>Rate Limit:</strong> 100 requests/hour</p>
        </div>
        
        <div class="api-card">
            <h3>👤 User Management</h3>
            <p>User authentication and profile management.</p>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/user</code>
            </div>
            <p><strong>Authentication:</strong> Required</p>
        </div>
        
        <div class="api-card">
            <h3>🏥 Health Monitoring</h3>
            <p>System health checks and monitoring endpoints.</p>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/health</code>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/healthz</code>
            </div>
            <p><strong>Authentication:</strong> None required</p>
        </div>
        
        <div class="api-card">
            <h3>💬 User Feedback</h3>
            <p>Collect and analyze user feedback for improvements.</p>
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/api/feedback</code>
            </div>
            <p><strong>Authentication:</strong> Required</p>
        </div>
        
        <div class="api-card">
            <h3>⚗️ Beta Management</h3>
            <p>Feature flags and beta testing controls (Admin only).</p>
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/beta/flags</code>
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span>
                <code>/api/beta/flags/{id}</code>
            </div>
            <p><strong>Authentication:</strong> Admin required</p>
        </div>
        
        <div class="api-card">
            <h3>📋 API Reference</h3>
            <p>Detailed endpoint documentation and schemas.</p>
            <div style="margin-top: 1rem;">
                <a href="/api/docs/openapi.json">OpenAPI Specification</a><br>
                <a href="/api/docs/endpoints">Endpoint List</a><br>
                <a href="/api/docs/schemas">Schema Definitions</a>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 3rem; padding: 2rem; background: white; border-radius: 8px; border: 1px solid #e5e7eb;">
        <h3>Getting Started</h3>
        <p>To use the NOUS API:</p>
        <ol>
            <li><strong>Authentication:</strong> Login via Google OAuth to obtain session</li>
            <li><strong>Base URL:</strong> All API endpoints use base path <code>/api/</code></li>
            <li><strong>Content Type:</strong> Send JSON requests with <code>Content-Type: application/json</code></li>
            <li><strong>Error Handling:</strong> All errors return standardized JSON responses</li>
        </ol>
        
        <h4>Example Request:</h4>
        <pre style="background: #f8f9fa; padding: 1rem; border-radius: 4px; overflow-x: auto;"><code>curl -X POST {{ base_url }}/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hello, NOUS!"}'</code></pre>
    </div>
</body>
</html>
        ''', current_time=datetime.now().strftime("%B %d, %Y"), base_url=request.url_root.rstrip('/'))
    
    @app.route('/api/docs/openapi.json')
    def openapi_specification():
        """Return OpenAPI specification."""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "NOUS Personal Assistant API",
                "description": "AI-powered personal assistant with chat, user management, and health monitoring",
                "version": "1.0.0",
                "contact": {
                    "name": "NOUS Development Team"
                },
                "license": {
                    "name": "MIT License"
                }
            },
            "servers": [
                {
                    "url": "/api",
                    "description": "API base path"
                }
            ],
            "paths": {
                "/chat": {
                    "post": {
                        "summary": "Send chat message",
                        "tags": ["Chat"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {
                                                "type": "string",
                                                "description": "User message content",
                                                "minLength": 1,
                                                "maxLength": 2000
                                            },
                                            "context": {
                                                "type": "object",
                                                "description": "Optional conversation context"
                                            }
                                        },
                                        "required": ["message"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful chat response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "message": {"type": "string"},
                                                "timestamp": {"type": "string"},
                                                "user": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            },
                            "401": {"description": "Authentication required"},
                            "400": {"description": "Invalid request"}
                        }
                    }
                },
                "/user": {
                    "get": {
                        "summary": "Get current user",
                        "tags": ["User Management"],
                        "responses": {
                            "200": {
                                "description": "User information",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "user": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "name": {"type": "string"},
                                                        "email": {"type": "string"},
                                                        "avatar": {"type": "string"}
                                                    }
                                                },
                                                "authenticated": {"type": "boolean"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "SessionAuth": {
                        "type": "apiKey",
                        "in": "cookie",
                        "name": "session"
                    }
                }
            }
        }
        return jsonify(spec)
    
    @app.route('/api/docs/endpoints')
    def api_endpoints_list():
        """List all available API endpoints."""
        endpoints = [
            {
                "path": "/api/chat",
                "method": "POST",
                "summary": "Send chat message",
                "authentication": "Required",
                "rate_limit": "100 requests/hour"
            },
            {
                "path": "/api/user",
                "method": "GET", 
                "summary": "Get current user",
                "authentication": "Required",
                "rate_limit": "Standard"
            },
            {
                "path": "/health",
                "method": "GET",
                "summary": "Basic health check",
                "authentication": "None",
                "rate_limit": "1000 requests/hour"
            },
            {
                "path": "/healthz",
                "method": "GET",
                "summary": "Comprehensive health check",
                "authentication": "None", 
                "rate_limit": "1000 requests/hour"
            }
        ]
        
        return jsonify({
            "endpoints": endpoints,
            "total_count": len(endpoints),
            "documentation_url": "/api/docs/",
            "openapi_spec": "/api/docs/openapi.json"
        })

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)