from flask import session, render_template, redirect, url_for, flash
from app import app, db
from flask_login import current_user, login_required
from google_auth import google_auth
from utils.beta_test_helper import is_beta_tester, configure_beta_mode

# Register Google Authentication blueprint
app.register_blueprint(google_auth, url_prefix="/auth")

# Configure beta testing mode
configure_beta_mode(app)

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    # Use flask_login.current_user to check if current user is logged in or anonymous.
    user = current_user
    if user.is_authenticated:
        return render_template('dashboard.html', user=user)
    else:
        return render_template('simple_welcome.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    # Check if user is a beta tester
    is_beta = is_beta_tester(user.id)
    return render_template('dashboard.html', user=user, is_beta=is_beta)

@app.route('/settings')
@login_required
def settings_page():
    user = current_user
    return f"Settings for {user.first_name or 'User'}"

@app.route('/user_guide')
def user_guide():
    return "User Guide for NOUS Personal Assistant"

@app.route('/help')
def help_page():
    return "Help for NOUS Personal Assistant"