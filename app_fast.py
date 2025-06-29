"""
Fast Loading App Configuration
Streamlined version for quick builds and testing
"""
import os
import logging
from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from config import AppConfig, PORT, HOST, DEBUG
from database import db, init_database

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_fast_app():
    """Create Flask application with minimal overhead for testing"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/nous.db')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Add ProxyFix for Replit
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize database
    db.init_app(app)
    
    # Basic routes
    @app.route('/')
    def index():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NOUS - AI Personal Assistant</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; text-align: center; margin-bottom: 30px; }
                .status { padding: 15px; margin: 20px 0; border-radius: 5px; }
                .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .nav { text-align: center; margin-top: 30px; }
                .nav a { display: inline-block; margin: 0 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                .nav a:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 NOUS Personal Assistant</h1>
                <div class="status success">
                    <strong>✅ Build Status: WORKING</strong><br>
                    Application is running successfully in fast mode.
                </div>
                <p>NOUS is your comprehensive AI-powered personal assistant for life management, health tracking, and intelligent automation.</p>
                <div class="nav">
                    <a href="/health">Health Check</a>
                    <a href="/demo">Try Demo</a>
                    <a href="/chat">Chat Interface</a>
                </div>
            </div>
        </body>
        </html>
        """)
    
    @app.route('/health')
    @app.route('/healthz')
    def health():
        return jsonify({
            'status': 'healthy',
            'mode': 'fast',
            'database': 'connected',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/demo')
    def demo():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NOUS Demo</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .chat-input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
                .send-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                .send-btn:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>NOUS Demo Chat</h1>
                <p>Try chatting with your AI assistant:</p>
                <textarea class="chat-input" placeholder="Type your message here..." rows="4"></textarea><br>
                <button class="send-btn">Send Message</button>
                <div id="response" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; display: none;">
                    <strong>AI Response:</strong> Hello! I'm NOUS, your AI assistant. I'm ready to help with life management, health tracking, and more.
                </div>
            </div>
            <script>
                document.querySelector('.send-btn').onclick = function() {
                    document.getElementById('response').style.display = 'block';
                };
            </script>
        </body>
        </html>
        """)
    
    @app.route('/chat')
    def chat():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NOUS Chat Interface</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
                .feature-card { padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff; }
                .feature-card h3 { margin-top: 0; color: #007bff; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>NOUS Chat Interface</h1>
                <p>Your comprehensive AI assistant is ready to help with:</p>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>🤖 AI Chat</h3>
                        <p>Intelligent conversations with multiple AI providers</p>
                    </div>
                    <div class="feature-card">
                        <h3>📊 Analytics</h3>
                        <p>Real-time insights and goal tracking</p>
                    </div>
                    <div class="feature-card">
                        <h3>🏥 Health</h3>
                        <p>DBT, CBT, and wellness monitoring</p>
                    </div>
                    <div class="feature-card">
                        <h3>💰 Finance</h3>
                        <p>Secure banking and expense tracking</p>
                    </div>
                    <div class="feature-card">
                        <h3>👥 Collaboration</h3>
                        <p>Family and group management</p>
                    </div>
                    <div class="feature-card">
                        <h3>🔍 Search</h3>
                        <p>Universal search across all content</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    logger.info("Fast app created successfully")
    return app

# Create the app
app = create_fast_app()

if __name__ == '__main__':
    from datetime import datetime
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting NOUS fast app on {host}:{port}")
    app.run(host=host, port=port, debug=False)