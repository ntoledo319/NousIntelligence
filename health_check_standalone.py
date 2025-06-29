#!/usr/bin/env python3
"""
Lightweight health check for OPERATION PUBLIC-OR-BUST
Ensures deployment health monitoring works
"""
from flask import Flask, jsonify
import os
from datetime import datetime

def create_health_app():
    """Create minimal health check app"""
    app = Flask(__name__)
    
    @app.route('/health')
    @app.route('/healthz')
    @app.route('/ready')
    def health():
        return jsonify({
            'status': 'healthy',
            'public_access': True,
            'deployment_ready': True,
            'timestamp': datetime.now().isoformat(),
            'version': 'public-or-bust',
            'port': os.environ.get('PORT', '5000')
        })
        
    @app.route('/')
    def root():
        return jsonify({
            'message': 'NOUS Health Check Service',
            'status': 'operational',
            'public_access': True
        })
        
    return app

if __name__ == "__main__":
    app = create_health_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
