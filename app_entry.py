#!/usr/bin/env python3
"""
Alternative entry point for NOUS application
Compatible with older .replit configuration that expects app.py
"""
import os

# Set optimized environment variables
os.environ.setdefault('PORT', '8080')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FAST_STARTUP', 'true')
os.environ.setdefault('DISABLE_HEAVY_FEATURES', 'true')

if __name__ == "__main__":
    # Import and run the main application
    from main import *
    
    print("🔄 Starting NOUS via app.py compatibility layer...")
    try:
        from app import create_app
        app = create_app()
        
        port = int(os.environ.get('PORT', 8080))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🚀 NOUS starting on {host}:{port}")
        print("⚡ Fast startup mode enabled")
        print("🔧 Heavy features will load on-demand")
        
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()