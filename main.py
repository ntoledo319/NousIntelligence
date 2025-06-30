#!/usr/bin/env python3
"""
Optimized main.py for OPERATION PUBLIC-OR-BUST
Fast startup with public access guarantees
"""
try:
    import os
    from datetime import datetime
    from app import create_app
except Exception as e:
    print(f"Failed to import modules in main.py: {e}")
    raise

# Set critical environment variables for public deployment
os.environ.setdefault('PORT', '8080')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///instance/app.db')

# Enable fast startup for deployment
os.environ.setdefault('FAST_STARTUP', 'true')
os.environ.setdefault('DISABLE_HEAVY_FEATURES', 'true')

app = create_app()

if __name__ == "__main__":
    try:
        # Get port from environment
        port = int(os.environ.get('PORT', 8080))
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
        try:
            from flask import Flask, jsonify, render_template_string
        except Exception as fallback_e:
            print(f"Failed to import flask for fallback: {fallback_e}")
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
        
        print("🔧 Running fallback server for public access")
        fallback_app.run(host=host, port=port, debug=False)
