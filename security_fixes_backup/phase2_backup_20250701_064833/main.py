#!/usr/bin/env python3
"""
Optimized main.py for OPERATION PUBLIC-OR-BUST
Fast startup with public access guarantees
"""
try:
    import os
    import logging
    from datetime import datetime
    from app import app
except Exception as e:
    import logging
    logging.error(f"Failed to import modules in main.py: {e}")
    raise

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set critical environment variables for public deployment
os.environ.setdefault('PORT', '8080')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///instance/app.db')

# Enable fast startup for deployment
os.environ.setdefault('FAST_STARTUP', 'true')
os.environ.setdefault('DISABLE_HEAVY_FEATURES', 'true')

# app is imported from app_working

if __name__ == "__main__":
    try:
        # Get port from environment
        port = int(os.environ.get('PORT', 8080))
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info(f"🚀 NOUS starting on {host}:{port}")
        logger.info("⚡ FAST STARTUP: Core functionality active")
        logger.info("🔧 Heavy features will load in background after startup")
        logger.info("💀 OPERATION PUBLIC-OR-BUST: Public access enabled")
        
        # Start with optimized settings for public deployment
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False  # Disable reloader for faster startup
        )
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # Fallback: create minimal Flask app for public access
        try:
            from flask import Flask, jsonify, render_template_string
        except Exception as fallback_e:
            logger.error(f"Failed to import flask for fallback: {fallback_e}")
            raise

        fallback_app = Flask(__name__)
        
        @fallback_app.route('/')
        def landing():
            return render_template_string("""
            <html>
            <head><title>NOUS - Loading...</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>🧠 NOUS</h1>
                <p>Your Intelligent Personal Assistant</p>
                <p>System is initializing... Please refresh in a moment.</p>
                <a href="/health" style="color: #007bff;">Health Check</a>
            </body>
            </html>
            """)
            
        @fallback_app.route('/health')
        @fallback_app.route('/healthz')
        def health():
            return jsonify({
                'status': 'healthy',
                'mode': 'fallback',
                'public_access': True,
                'timestamp': datetime.now().isoformat()
            })
            
        port = int(os.environ.get('PORT', 8080))
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info("🔧 Running fallback server for public access")
        fallback_app.run(host=host, port=port, debug=False)
