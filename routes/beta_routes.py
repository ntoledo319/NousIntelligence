"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Beta Routes Routes
Beta Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

beta_routes_bp = Blueprint('beta_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Beta Testing Routes

This module provides routes for managing beta testers and beta feature access.
It includes functionality for registering as a beta tester and managing beta testing.

@module routes.beta_routes
@description Beta testing routes
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app

from sqlalchemy.exc import IntegrityError
from datetime import datetime

from models import db, BetaTester, User
from utils.security_helper import admin_required, csrf_protect, log_security_event
from utils.settings import get_setting

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
beta_bp = Blueprint('beta', __name__, url_prefix='/beta')

@beta_bp.route('/')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def index():
    """Beta testing landing page"""
    # Check if beta mode is enabled
    beta_mode = get_setting('enable_beta_features', False)
    if not beta_mode:
        flash('Beta testing is currently disabled.', 'info')
        return redirect(url_for('index.index'))

    # Check if user is already a beta tester
    is_beta_tester = False
    if ('user' in session and session['user']):
        beta_tester = BetaTester.query.filter_by(user_id=session.get('user', {}).get('id', 'demo_user'), active=True).first()
        is_beta_tester = beta_tester is not None

    return render_template(
        'beta/index.html',
        is_beta_tester=is_beta_tester
    )

@beta_bp.route('/apply', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def apply():
    """Apply for beta testing"""
    # Check if beta mode is enabled
    beta_mode = get_setting('enable_beta_features', False)
    if not beta_mode:
        flash('Beta testing is currently disabled.', 'info')
        return redirect(url_for('index.index'))

    # Check if user is already a beta tester
    existing_tester = BetaTester.query.filter_by(user_id=session.get('user', {}).get('id', 'demo_user')).first()
    if existing_tester and existing_tester.active:
        flash('You are already a beta tester.', 'info')
        return redirect(url_for('beta.dashboard'))

    # Check if we're at max beta testers
    max_testers = int(current_app.config.get('MAX_BETA_TESTERS', 30))
    current_tester_count = BetaTester.query.filter_by(active=True).count()

    if current_tester_count >= max_testers and not existing_tester:
        flash('Maximum number of beta testers has been reached. Please try again later.', 'warning')
        return redirect(url_for('beta.index'))

    if request.method == 'POST':
        # Get access code from form
        access_code = request.form.get('access_code', '').strip()
        correct_code = current_app.config.get('BETA_ACCESS_CODE', 'BETANOUS2025')

        if not access_code:
            flash('Access code is required.', 'danger')
        elif access_code != correct_code:
            flash('Invalid access code.', 'danger')
            log_security_event("BETA_INVALID_CODE", f"Invalid beta access code attempt: {access_code}", severity="WARNING")
        else:
            try:
                # Create or update beta tester
                if existing_tester:
                    existing_tester.active = True
                    existing_tester.access_code = access_code
                    db.session.commit()
                    log_security_event("BETA_REACTIVATED", "User reactivated as beta tester", severity="INFO")
                else:
                    # Create new beta tester
                    beta_tester = BetaTester(
                        user_id=session.get('user', {}).get('id', 'demo_user'),
                        access_code=access_code,
                        active=True,
                        notes=request.form.get('notes', '')
                    )
                    db.session.add(beta_tester)
                    db.session.commit()
                    log_security_event("BETA_ENROLLED", "User enrolled as beta tester", severity="INFO")

                flash('You have been successfully enrolled as a beta tester!', 'success')
                return redirect(url_for('beta.dashboard'))

            except IntegrityError:
                db.session.rollback()
                flash('An error occurred during enrollment.', 'danger')
                logger.error(f"Beta enrollment failed for user {session.get('user', {}).get('id', 'demo_user')}")

            except Exception as e:
                db.session.rollback()
                flash('An unexpected error occurred.', 'danger')
                logger.error(f"Beta enrollment error: {str(e)}")

    return render_template('beta/apply.html')

@beta_bp.route('/dashboard')
def dashboard():
    """Beta tester dashboard"""
    # Check if user is a beta tester
    beta_tester = BetaTester.query.filter_by(user_id=session.get('user', {}).get('id', 'demo_user'), active=True).first()
    if not beta_tester:
        flash('You need to be a beta tester to access this page.', 'warning')
        return redirect(url_for('beta.index'))

    # Get list of available beta features (could be dynamic from database)
    beta_features = [
        {
            'name': 'Voice Emotion Analysis',
            'description': 'Analyze emotions in voice recordings using AI',
            'url': url_for('voice_emotion.index'),
            'status': 'Available',
            'icon': 'fas fa-microphone'
        },
        {
            'name': 'Smart Shopping Lists',
            'description': 'AI-generated shopping lists based on your history',
            'url': url_for('smart_shopping.index'),
            'status': 'Available',
            'icon': 'fas fa-shopping-cart'
        },
        {
            'name': 'Mindfulness Voice Assistant',
            'description': 'Voice-guided mindfulness sessions',
            'url': url_for('voice_mindfulness.index'),
            'status': 'Coming Soon',
            'icon': 'fas fa-brain'
        }
    ]

    return render_template(
        'beta/dashboard.html',
        beta_tester=beta_tester,
        beta_features=beta_features
    )

@beta_bp.route('/leave', methods=['POST'])
@csrf_protect
def leave_beta():
    """Leave the beta testing program"""
    beta_tester = BetaTester.query.filter_by(user_id=session.get('user', {}).get('id', 'demo_user')).first()

    if beta_tester:
        beta_tester.active = False
        db.session.commit()
        log_security_event("BETA_LEFT", "User left beta testing program", severity="INFO")
        flash('You have successfully left the beta testing program.', 'success')
    else:
        flash('You are not currently enrolled in the beta testing program.', 'info')

    return redirect(url_for('beta.index'))

@beta_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for managing beta testers"""
    # Get all beta testers
    beta_testers = (
        BetaTester.query
        .join(User)
        .add_columns(
            User.email,
            User.first_name,
            User.last_name,
            User.created_at
        )
        .order_by(BetaTester.active.desc(), BetaTester.created_at.desc())
        .all()
    )

    # Max testers config
    max_testers = int(current_app.config.get('MAX_BETA_TESTERS', 30))
    current_active = BetaTester.query.filter_by(active=True).count()

    return render_template(
        'beta/admin.html',
        beta_testers=beta_testers,
        max_testers=max_testers,
        current_active=current_active
    )

@beta_bp.route('/admin/toggle/<user_id>', methods=['POST'])
@admin_required
@csrf_protect
def toggle_tester(user_id):
    """Toggle a beta tester's active status"""
    beta_tester = BetaTester.query.filter_by(user_id=user_id).first()

    if not beta_tester:
        flash('Beta tester not found.', 'danger')
    else:
        # Toggle status
        beta_tester.active = not beta_tester.active
        db.session.commit()

        status = "activated" if beta_tester.active else "deactivated"
        user_email = User.query.filter_by(id=user_id).first().email

        log_security_event(
            "BETA_STATUS_CHANGE",
            f"Admin {status} beta tester: {user_email}",
            severity="INFO"
        )

        flash(f'Beta tester {status} successfully.', 'success')

    return redirect(url_for('beta.admin_dashboard'))