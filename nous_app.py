"""
NOUS Personal Assistant - Unified Application

This is the single, authoritative entry point for the NOUS Personal Assistant.
All redundant variants have been consolidated into this clean implementation.
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, make_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create Flask application
def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")
    
    # Ensure required directories exist
    for directory in ['static', 'templates', 'logs', 'flask_session', 'instance', 'uploads']:
        os.makedirs(directory, exist_ok=True)
    
    # Public access headers
    @app.after_request
    def add_public_headers(response):
        """Add headers to ensure public access without Replit login"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        response.headers['X-Replit-Auth'] = 'false'
        return response
    
    # Main routes
    @app.route('/')
    def index():
        """Main landing page"""
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
                "timestamp": datetime.now().isoformat()
            })
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        import platform
        
        health_info = {
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'python_version': platform.python_version(),
            'system': platform.system(),
            'environment': os.environ.get('FLASK_ENV', 'production')
        }
        
        # Return HTML for browser requests, JSON for API calls
        if request.headers.get('Accept', '').find('text/html') >= 0:
            try:
                return render_template('health.html', **health_info, title="Health Check")
            except:
                pass
        
        return jsonify(health_info)
    
    @app.route('/about')
    def about():
        """About page"""
        try:
            return render_template('about.html', 
                                 title="About NOUS",
                                 version="1.0.0")
        except Exception as e:
            logger.error(f"About template error: {e}")
            return jsonify({
                "page": "about",
                "title": "NOUS Personal Assistant",
                "description": "An advanced AI-powered personal assistant",
                "version": "1.0.0"
            })
    
    @app.route('/features')
    def features():
        """Features page"""
        try:
            return render_template('features.html', 
                                 title="Features",
                                 version="1.0.0")
        except Exception as e:
            logger.error(f"Features template error: {e}")
            return jsonify({
                "page": "features",
                "title": "NOUS Features",
                "features": [
                    "AI-powered conversations",
                    "Task management",
                    "Health monitoring",
                    "Weather updates",
                    "Smart scheduling"
                ]
            })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        try:
            return render_template('error.html', 
                                 error="Page not found", 
                                 code=404, 
                                 title="Not Found"), 404
        except:
            return jsonify({"error": "Page not found", "code": 404}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        logger.error(f"Server error: {error}")
        try:
            return render_template('error.html', 
                                 error="Internal server error", 
                                 code=500, 
                                 title="Server Error"), 500
        except:
            return jsonify({"error": "Internal server error", "code": 500}), 500
    
    return app

# Create the application instance
app = create_app()

def main():
    """Main entry point"""
    port = int(os.environ.get('PORT', 8080))
    
    logger.info("=" * 60)
    logger.info("NOUS Personal Assistant - Unified Application")
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    logger.info("Public access enabled (no Replit login required)")
    logger.info("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()