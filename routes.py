from flask import session, redirect, url_for, flash
from app import app, db
from flask_login import current_user, login_required

# Import Google auth blueprint
from google_auth import google_auth as google_auth_bp

# Register the Google auth blueprint
app.register_blueprint(google_auth_bp, url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Add protection to routes that require login
@app.route('/dashboard')
@login_required
def protected_dashboard():
    from app import dashboard
    return dashboard()

@app.route('/api/doctors', methods=["GET"])
@login_required
def protected_api_get_doctors():
    from app import api_get_doctors
    return api_get_doctors()

@app.route('/api/doctors', methods=["POST"])
@login_required
def protected_api_add_doctor():
    from app import api_add_doctor
    return api_add_doctor()

@app.route('/api/doctors/<int:doctor_id>', methods=["GET"])
@login_required
def protected_api_get_doctor(doctor_id):
    from app import api_get_doctor
    return api_get_doctor(doctor_id)

@app.route('/api/doctors/<int:doctor_id>', methods=["PUT"])
@login_required
def protected_api_update_doctor(doctor_id):
    from app import api_update_doctor
    return api_update_doctor(doctor_id)

@app.route('/api/doctors/<int:doctor_id>', methods=["DELETE"])
@login_required
def protected_api_delete_doctor(doctor_id):
    from app import api_delete_doctor
    return api_delete_doctor(doctor_id)

# We'll add protection to just a few of the API routes for demonstration
# In a real application, you would protect all API routes

# Create a welcome page
@app.route('/welcome')
@login_required
def welcome():
    return f"""
    <h1>Welcome, {current_user.first_name if current_user.first_name else 'User'}!</h1>
    <p>You have successfully logged in via Replit Auth.</p>
    <p>Your email: {current_user.email if current_user.email else 'Not provided'}</p>
    <p><a href="{url_for('index')}">Go to Command Interface</a></p>
    <p><a href="{url_for('protected_dashboard')}">Go to Dashboard</a></p>
    <p><a href="{url_for('google_auth.logout')}">Logout</a></p>
    """