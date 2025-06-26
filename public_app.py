"""
NOUS Personal Assistant - 100% Public Application

This is a completely public Flask application with no authentication dependencies.
Only /admin routes are protected by a simple header check.
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort
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
    
    # Basic configuration - no auth dependencies
    app.secret_key = os.environ.get("SESSION_SECRET", "public-nous-2025")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Ensure required directories exist
    for directory in ['static', 'templates', 'logs', 'uploads']:
        os.makedirs(directory, exist_ok=True)
    
    # Public access headers for all routes
    @app.after_request
    def add_public_headers(response):
        """Add headers to ensure public access without any authentication"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Admin-Key'
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        response.headers['X-Replit-Auth'] = 'false'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    # Admin authentication check
    def check_admin():
        """Check if request has valid admin key"""
        admin_key = os.environ.get('ADMIN_KEY')
        if not admin_key:
            return False
        return request.headers.get('X-Admin-Key') == admin_key
    
    # Public routes
    @app.route('/')
    def index():
        """Main landing page - completely public"""
        return render_template('public_index.html', 
                             title="NOUS Personal Assistant",
                             version="2.0.0-public",
                             timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    @app.route('/healthz')
    def healthz():
        """Health check endpoint - completely public"""
        health_info = {
            'status': 'healthy',
            'version': '2.0.0-public',
            'timestamp': datetime.now().isoformat(),
            'mode': 'public',
            'environment': os.environ.get('FLASK_ENV', 'production')
        }
        return jsonify(health_info), 200
    
    @app.route('/about')
    def about():
        """About page - completely public"""
        return render_template('public_about.html', 
                             title="About NOUS",
                             version="2.0.0-public")
    
    @app.route('/features')
    def features():
        """Features page - completely public"""
        return render_template('public_features.html', 
                             title="Features",
                             version="2.0.0-public")
    
    @app.route('/chat')
    def chat():
        """Chat interface - completely public"""
        return render_template('public_chat.html', 
                             title="Chat with NOUS")
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        """Chat API endpoint - completely public"""
        data = request.get_json()
        message = data.get('message', '') if data else ''
        
        # Simple echo response for demo
        return jsonify({
            'response': f"Hello! You said: {message}",
            'timestamp': datetime.now().isoformat(),
            'mode': 'public'
        })
    
    # Admin routes - protected by header check
    @app.route('/admin')
    def admin_dashboard():
        """Admin dashboard - requires X-Admin-Key header"""
        if not check_admin():
            abort(401)
        return render_template('admin_dashboard.html', 
                             title="Admin Dashboard")
    
    @app.route('/admin/stats')
    def admin_stats():
        """Admin stats - requires X-Admin-Key header"""
        if not check_admin():
            abort(401)
        return jsonify({
            'users': 'N/A - Public Mode',
            'requests': 'N/A - No tracking',
            'uptime': 'Running',
            'mode': 'public'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Custom 404 page"""
        return render_template('404.html', 
                             error="Page not found", 
                             title="Not Found"), 404
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Custom 401 page for admin access"""
        return jsonify({
            'error': 'Unauthorized - Admin access requires X-Admin-Key header',
            'code': 401
        }), 401
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        logger.error(f"Server error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'code': 500,
            'mode': 'public'
        }), 500
    
    return app

# Create the application instance
app = create_app()

def main():
    """Main entry point"""
    port = int(os.environ.get('PORT', 5000))
    
    logger.info("=" * 60)
    logger.info("NOUS Personal Assistant - 100% PUBLIC MODE")
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    logger.info("✓ No authentication required")
    logger.info("✓ Public access enabled")
    logger.info("✓ CORS enabled for all origins")
    logger.info("✓ Admin protected by X-Admin-Key header only")
    logger.info("✓ Health check: /healthz")
    logger.info("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()