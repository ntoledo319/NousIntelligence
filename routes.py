from flask import session
from app import app, db
from replit_auth import make_replit_blueprint, require_login
from flask_login import current_user

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    # Use flask_login.current_user to check if current user is logged in or anonymous.
    user = current_user
    if user.is_authenticated:
        return f"Hello, {user.first_name or 'User'}! Welcome to the NOUS Personal Assistant."
    else:
        return "Welcome to NOUS. Please log in to continue."

@app.route('/dashboard')
@require_login  # protected by Replit Auth
def dashboard():
    user = current_user
    return f"Dashboard for {user.first_name or 'User'}"

@app.route('/settings')
@require_login  # protected by Replit Auth
def settings_page():
    user = current_user
    return f"Settings for {user.first_name or 'User'}"

@app.route('/user_guide')
def user_guide():
    return "User Guide for NOUS Personal Assistant"

@app.route('/help')
def help_page():
    return "Help for NOUS Personal Assistant"