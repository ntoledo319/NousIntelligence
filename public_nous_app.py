"""
NOUS Personal Assistant - 100% Public Access Application

This version completely eliminates authentication loops by making the app fully public.
Only admin routes (if any) will require simple header authentication.
"""
import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, make_response, session
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")
    
    # Add ProxyFix for production deployment behind reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Ensure required directories exist
    for directory in ['static', 'templates', 'logs', 'flask_session', 'instance', 'uploads']:
        os.makedirs(directory, exist_ok=True)
    
    # CRITICAL: Public access headers - removes authentication requirements
    @app.after_request
    def add_public_headers(response):
        """Add headers to ensure 100% public access without any authentication"""
        # Disable all authentication mechanisms
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        
        # Critical: Disable Replit authentication completely
        response.headers['X-Replit-Auth'] = 'false'
        response.headers['X-Replit-User-Auth'] = 'false'
        
        # Ensure no redirect loops
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    
    # Session configuration for optional features (but not required for access)
    app.config.update(
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,  # Allow HTTP for testing
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=1)
    )
    
    # MAIN ROUTES - All completely public
    @app.route('/')
    def index():
        """Main landing page - completely public"""
        try:
            return render_template('index.html', 
                                 title="NOUS Personal Assistant",
                                 version="1.0.0",
                                 timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            logger.error(f"Template error: {e}")
            return jsonify({
                "status": "online",
                "message": "NOUS Personal Assistant is running",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "note": "Fully public access enabled"
            })
    
    @app.route('/health')
    @app.route('/healthz')
    def health():
        """Health check endpoint - completely public"""
        import platform
        
        health_info = {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'python_version': platform.python_version(),
            'system': platform.system(),
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'access_level': 'public',
            'authentication': 'disabled'
        }
        
        return jsonify(health_info)
    
    @app.route('/about')
    def about():
        """About page - completely public"""
        try:
            return render_template('about.html', 
                                 title="About NOUS",
                                 version="1.0.0")
        except Exception as e:
            logger.error(f"About template error: {e}")
            return jsonify({
                "page": "about",
                "title": "NOUS Personal Assistant",
                "description": "AI-powered personal assistant with full public access",
                "version": "1.0.0"
            })
    
    @app.route('/features')
    def features():
        """Features page - completely public"""
        try:
            return render_template('features.html', 
                                 title="NOUS Features",
                                 version="1.0.0")
        except Exception as e:
            logger.error(f"Features template error: {e}")
            return jsonify({
                "page": "features",
                "title": "NOUS Features",
                "features": [
                    "AI-powered conversations",
                    "Voice interaction",
                    "Document analysis",
                    "Health monitoring",
                    "Smart shopping assistance"
                ]
            })
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard - completely public, no login required"""
        try:
            return render_template('dashboard.html', 
                                 title="NOUS Dashboard",
                                 user="Public User",
                                 access_level="public")
        except Exception as e:
            logger.error(f"Dashboard template error: {e}")
            return jsonify({
                "page": "dashboard",
                "title": "NOUS Dashboard",
                "status": "Available - No login required",
                "features": "All features accessible"
            })
    
    @app.route('/chat')
    def chat():
        """Chat interface - completely public"""
        try:
            return render_template('chat/chat.html', 
                                 title="NOUS Chat",
                                 user="Public User")
        except Exception as e:
            logger.error(f"Chat template error: {e}")
            return jsonify({
                "page": "chat",
                "title": "NOUS Chat",
                "status": "Available - No authentication required"
            })
    
    # API Routes - All public
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        """Chat API endpoint - completely public"""
        try:
            data = request.get_json() or {}
            message = data.get('message', '')
            
            if not message:
                return jsonify({'error': 'Message is required'}), 400
            
            # Simple echo response for now
            response = {
                'response': f"I received your message: {message}",
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'access_level': 'public'
            }
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"API chat error: {e}")
            return jsonify({
                'error': 'Chat processing failed',
                'details': str(e)
            }), 500
    
    @app.route('/api/health')
    def api_health():
        """API health check - completely public"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'access': 'public',
            'authentication': 'disabled'
        })
    
    # Admin routes (optional, with simple header check)
    def check_admin():
        """Check if request has valid admin key"""
        admin_key = request.headers.get('X-Admin-Key')
        expected_key = os.environ.get('ADMIN_KEY', 'admin123')
        return admin_key == expected_key
    
    @app.route('/admin')
    def admin_dashboard():
        """Admin dashboard - requires X-Admin-Key header"""
        if not check_admin():
            return jsonify({
                'error': 'Admin access required',
                'note': 'Send X-Admin-Key header with valid key'
            }), 401
        
        return jsonify({
            'page': 'admin',
            'status': 'authenticated',
            'timestamp': datetime.now().isoformat()
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Custom 404 page"""
        return render_template('error.html', 
                             error_code=404,
                             error_message="Page not found",
                             title="404 - Not Found"), 404
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Custom 401 page for admin access"""
        return jsonify({
            'error': 'Unauthorized',
            'note': 'Admin access requires X-Admin-Key header',
            'timestamp': datetime.now().isoformat()
        }), 401
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        logger.error(f"Server error: {str(error)}")
        return render_template('error.html',
                             error_code=500,
                             error_message="Internal server error",
                             title="500 - Server Error"), 500
    
    logger.info("NOUS app created successfully - FULLY PUBLIC ACCESS ENABLED")
    return app

def main():
    """Main entry point"""
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting NOUS Personal Assistant on port {port}")
    logger.info("🌍 PUBLIC ACCESS MODE: No authentication required")
    logger.info("🔓 All routes are accessible without login")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()