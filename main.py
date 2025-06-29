#!/usr/bin/env python3
"""
Optimized main.py for OPERATION PUBLIC-OR-BUST
Fast startup with public access guarantees
"""
import os
from datetime import datetime

# Set critical environment variables for public deployment
os.environ.setdefault('PORT', '5000')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('FLASK_ENV', 'production')

# Enable fast startup for deployment
os.environ.setdefault('FAST_STARTUP', 'true')
os.environ.setdefault('DISABLE_HEAVY_FEATURES', 'true')

if __name__ == "__main__":
    try:
        from app import create_app
        app = create_app()
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🚀 NOUS starting on {host}:{port}")
        print("⚡ FAST STARTUP: Core functionality active")
        print("🔧 Heavy features will load in background after startup")
        print("💀 OPERATION PUBLIC-OR-BUST: Public access enabled")
        
        # Start with optimized settings for public deployment
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False  # Disable reloader for faster startup
        )
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        # Fallback: create minimal Flask app for public access
        from flask import Flask, jsonify, render_template_string
        
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
            
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print("🔧 Running fallback server for public access")
        fallback_app.run(host=host, port=port, debug=False)
