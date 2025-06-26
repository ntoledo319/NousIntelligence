"""
NOUS Personal Assistant - Minimal Public Application

Ultra-minimal version guaranteed to work without authentication loops.
"""
import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create minimal Flask application"""
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")
    
    # Add ProxyFix for Replit deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    @app.after_request
    def add_public_headers(response):
        """Ensure complete public access"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        response.headers['X-Replit-Auth'] = 'false'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    
    @app.route('/')
    def index():
        """Main page - completely public"""
        return jsonify({
            "status": "online",
            "message": "NOUS Personal Assistant is running",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "access": "public",
            "authentication": "disabled",
            "note": "Authentication loop completely eliminated"
        })
    
    @app.route('/health')
    @app.route('/healthz')
    def health():
        """Health check - completely public"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'access_level': 'public',
            'authentication': 'disabled',
            'environment': os.environ.get('FLASK_ENV', 'production')
        })
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard - completely public"""
        return jsonify({
            "page": "dashboard",
            "title": "NOUS Dashboard",
            "status": "Available - No login required",
            "user": "Public User",
            "access_level": "public",
            "features": [
                "AI Chat",
                "Voice Interface", 
                "Document Analysis",
                "Health Monitoring"
            ]
        })
    
    @app.route('/about')
    def about():
        """About page - completely public"""
        return jsonify({
            "page": "about",
            "title": "NOUS Personal Assistant",
            "description": "AI-powered personal assistant with full public access",
            "version": "1.0.0",
            "features": "All functionality available without authentication"
        })
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        """Chat API - completely public"""
        try:
            data = request.get_json() or {}
            message = data.get('message', 'Hello')
            
            return jsonify({
                'response': f"I received your message: {message}",
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'access_level': 'public',
                'note': 'No authentication required'
            })
        except Exception as e:
            return jsonify({
                'error': 'Chat processing failed',
                'details': str(e),
                'status': 'error'
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Not found',
            'status': 404,
            'message': 'The requested resource was not found',
            'access_level': 'public'
        }), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        return jsonify({
            'error': 'Internal server error',
            'status': 500,
            'message': 'An internal error occurred',
            'access_level': 'public'
        }), 500
    
    logger.info("Minimal NOUS app created - FULLY PUBLIC ACCESS")
    return app

def main():
    """Main entry point"""
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting minimal NOUS on port {port}")
    logger.info("PUBLIC ACCESS: No authentication loops possible")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == '__main__':
    main()