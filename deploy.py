"""
Deployment helper script for NOUS Personal Assistant
"""
import os
import sys

def setup_deployment():
    """Configure the environment for deployment"""
    print("Setting up NOUS Personal Assistant for deployment...")
    
    # Ensure directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Set environment variables for deployment
    os.environ['FLASK_APP'] = 'main.py'
    os.environ['FLASK_ENV'] = 'production'
    
    print("Deployment setup completed successfully!")
    print("Run 'python main.py' to start the application")

if __name__ == "__main__":
    setup_deployment()
    
    # If argument is passed to run the app after setup
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        from main import app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)