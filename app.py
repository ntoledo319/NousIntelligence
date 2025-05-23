import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-secure-key-2025")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize extensions
db.init_app(app)

# Routes
@app.route('/')
def index():
    """Homepage with welcome message"""
    return render_template('index.html', title='NOUS Personal Assistant')

@app.route('/dashboard')
def dashboard():
    """Dashboard view"""
    return render_template('dashboard.html', title='Dashboard')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', title='Page Not Found', 
                           error_code=404, message="The page you requested was not found."), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', title='Server Error', 
                           error_code=500, message="An internal server error occurred."), 500

# Create database tables within application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Use 0.0.0.0 to make the app accessible externally
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)