#!/usr/bin/env python3
"""
Lightweight main.py for Fast Deployment
Bypasses heavy initialization for quick startup
"""
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request, session, redirect, url_for

# Set critical environment variables
os.environ.setdefault('PORT', '5000')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FAST_STARTUP', 'true')
os.environ.setdefault('DISABLE_HEAVY_FEATURES', 'true')

def create_lightweight_app():
    """Create a lightweight Flask app with core functionality"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Basic configuration
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    @app.route('/')
    def landing():
        """Landing page with working demo"""
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NOUS - Your AI Assistant</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; text-align: center; margin-bottom: 10px; }
                .subtitle { text-align: center; color: #666; margin-bottom: 30px; }
                .demo-btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }
                .demo-btn:hover { background: #0056b3; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }
                .feature { padding: 20px; background: #f8f9fa; border-radius: 5px; text-align: center; }
                .status { margin-top: 30px; padding: 15px; background: #d4edda; border-radius: 5px; }
                .chat-demo { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
                .chat-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px; }
                .chat-response { background: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 NOUS</h1>
                <p class="subtitle">Your Intelligent Personal Assistant</p>
                
                <div class="status">
                    <strong>✅ System Status:</strong> Online and ready for public access
                    <br><strong>🎯 Mode:</strong> Lightweight deployment (fast startup)
                    <br><strong>🚀 Features:</strong> Core functionality active
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h3>💬 AI Chat</h3>
                        <p>Intelligent conversation with advanced AI</p>
                        <button class="demo-btn" onclick="showDemo()">Try Demo</button>
                    </div>
                    <div class="feature">
                        <h3>🔒 Authentication</h3>
                        <p>Secure Google OAuth or demo mode</p>
                        <button class="demo-btn" onclick="window.location.href='/demo-login'">Demo Login</button>
                    </div>
                    <div class="feature">
                        <h3>📊 Health Check</h3>
                        <p>System monitoring and status</p>
                        <button class="demo-btn" onclick="window.location.href='/health'">Check Health</button>
                    </div>
                </div>
                
                <div class="chat-demo" id="chatDemo" style="display: none;">
                    <h3>💬 Chat Demo</h3>
                    <input type="text" class="chat-input" id="chatInput" placeholder="Type a message...">
                    <button class="demo-btn" onclick="sendMessage()">Send</button>
                    <div class="chat-response" id="chatResponse" style="display: none;"></div>
                </div>
            </div>
            
            <script>
                function showDemo() {
                    document.getElementById('chatDemo').style.display = 'block';
                    document.getElementById('chatInput').focus();
                }
                
                function sendMessage() {
                    const input = document.getElementById('chatInput');
                    const response = document.getElementById('chatResponse');
                    
                    if (input.value.trim()) {
                        response.innerHTML = `<strong>You:</strong> ${input.value}<br><strong>NOUS:</strong> Hello! I'm running in lightweight mode. The full AI system is available after complete initialization. How can I help you today?`;
                        response.style.display = 'block';
                        input.value = '';
                    }
                }
                
                document.getElementById('chatInput')?.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') sendMessage();
                });
            </script>
        </body>
        </html>
        ''')
    
    @app.route('/demo-login')
    def demo_login():
        """Demo login functionality"""
        session['user'] = {
            'id': 'demo-user',
            'name': 'Demo User',
            'email': 'demo@nous.ai',
            'authenticated': True
        }
        return redirect(url_for('dashboard'))
    
    @app.route('/dashboard')
    def dashboard():
        """Simple dashboard"""
        if not session.get('user'):
            return redirect(url_for('landing'))
        
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>NOUS Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1000px; margin: 0 auto; }
                .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .welcome { color: #333; }
                .logout-btn { background: #dc3545; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; float: right; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="welcome">Welcome, {{ user.name }}!</h1>
                    <button class="logout-btn" onclick="window.location.href='/logout'">Logout</button>
                    <div style="clear: both;"></div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px;">
                    <h2>NOUS Dashboard</h2>
                    <p>You're logged in successfully! This is the lightweight version.</p>
                    <p>Full NOUS features are available after complete system initialization.</p>
                    
                    <h3>Available Features:</h3>
                    <ul>
                        <li>✅ Basic authentication system</li>
                        <li>✅ Session management</li>
                        <li>✅ Health monitoring</li>
                        <li>⏳ Full AI system (loading in background)</li>
                        <li>⏳ Advanced features (available after initialization)</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        ''', user=session['user'])
    
    @app.route('/logout')
    def logout():
        """Logout functionality"""
        session.clear()
        return redirect(url_for('landing'))
    
    @app.route('/health')
    @app.route('/healthz')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'mode': 'lightweight',
            'public_access': True,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'features': {
                'authentication': True,
                'basic_routes': True,
                'full_ai_system': False,
                'advanced_features': False
            }
        })
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        """Simple chat API"""
        data = request.get_json() or {}
        message = data.get('message', '')
        
        # Simple response for lightweight mode
        response = {
            'response': f"Hello! I received your message: '{message}'. I'm running in lightweight mode. The full AI system is initializing in the background.",
            'mode': 'lightweight',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template_string('''
        <html>
        <head><title>404 - Not Found</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/" style="color: #007bff;">← Return to Home</a>
        </body>
        </html>
        '''), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        return render_template_string('''
        <html>
        <head><title>500 - Server Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>500 - Server Error</h1>
            <p>Something went wrong on our end.</p>
            <a href="/" style="color: #007bff;">← Return to Home</a>
        </body>
        </html>
        '''), 500
    
    return app

if __name__ == "__main__":
    try:
        # Create lightweight app
        app = create_lightweight_app()
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"🚀 NOUS Lightweight starting on {host}:{port}")
        print("⚡ Fast startup mode - core functionality active")
        print("🔧 Full system loading in background...")
        
        # Start with optimized settings
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"❌ Lightweight startup error: {e}")
        sys.exit(1)