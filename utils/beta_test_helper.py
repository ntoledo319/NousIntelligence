"""
Beta test helper module for managing beta testers and their access
"""

from datetime import datetime
from flask import flash, redirect, url_for, session, current_app
from flask_login import current_user
from functools import wraps
import logging
import os

from models import db, User, BetaTester

# Maximum number of beta testers allowed
MAX_BETA_TESTERS = 30

def configure_beta_mode(app):
    """Configure the application for beta mode"""
    # Set beta mode flag in app config
    app.config['BETA_MODE'] = True
    app.config['MAX_BETA_TESTERS'] = MAX_BETA_TESTERS
    
    # Load beta tester access codes from environment variable if available
    beta_access_code = os.environ.get('BETA_ACCESS_CODE', 'BETANOUS2025')
    app.config['BETA_ACCESS_CODE'] = beta_access_code
    
    logging.info(f"Application configured for beta testing mode (max {MAX_BETA_TESTERS} testers)")
    
def is_beta_tester(user_id=None):
    """Check if a user is a beta tester"""
    if not user_id and current_user.is_authenticated:
        user_id = current_user.id
    
    if not user_id:
        return False
        
    # Check if user is an admin (admins are always beta testers)
    user = User.query.get(user_id)
    if user and user.is_admin:
        return True
        
    # Check beta tester status
    tester = BetaTester.query.filter_by(user_id=user_id, status='active').first()
    return tester is not None
    
def requires_beta_access(f):
    """Decorator to require beta tester status for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Always allow admins
        if current_user.is_authenticated and current_user.is_administrator():
            return f(*args, **kwargs)
            
        # Check if user is a beta tester
        if current_user.is_authenticated and is_beta_tester(current_user.id):
            return f(*args, **kwargs)
            
        # If not authenticated or not a beta tester, redirect
        flash("This feature is only available to beta testers", "warning")
        if current_user.is_authenticated:
            return redirect(url_for('beta.request_access'))
        else:
            return redirect(url_for('google_auth.login'))
            
    return decorated_function
    
def register_beta_tester(user_id, access_code=None, notes=None):
    """Register a user as a beta tester"""
    # If no access code provided, check if we're at max capacity
    current_count = BetaTester.query.filter_by(status='active').count()
    
    # Check if we're at max capacity
    if current_count >= MAX_BETA_TESTERS:
        return {
            'success': False,
            'error': f"Maximum number of beta testers ({MAX_BETA_TESTERS}) reached"
        }
        
    # Check if user is already a beta tester
    existing = BetaTester.query.filter_by(user_id=user_id).first()
    if existing:
        if existing.status == 'active':
            return {
                'success': False,
                'error': "User is already a beta tester"
            }
        else:
            # Reactivate the user
            existing.status = 'active'
            existing.activated_at = datetime.utcnow()
            existing.notes = notes
            db.session.commit()
            return {
                'success': True,
                'message': "Beta tester access reactivated"
            }
    
    # Create new beta tester record
    tester = BetaTester(
        user_id=user_id,
        status='active',
        notes=notes,
        activated_at=datetime.utcnow()
    )
    db.session.add(tester)
    db.session.commit()
    
    return {
        'success': True,
        'message': "Beta tester registered successfully"
    }
    
def deactivate_beta_tester(user_id, reason=None):
    """Deactivate a beta tester"""
    tester = BetaTester.query.filter_by(user_id=user_id).first()
    if not tester:
        return {
            'success': False,
            'error': "User is not a beta tester"
        }
        
    tester.status = 'inactive'
    tester.deactivated_at = datetime.utcnow()
    tester.notes = reason or tester.notes
    db.session.commit()
    
    return {
        'success': True,
        'message': "Beta tester deactivated"
    }
    
def get_beta_testers(include_inactive=False):
    """Get all beta testers"""
    query = BetaTester.query
    if not include_inactive:
        query = query.filter_by(status='active')
        
    return query.all()
    
def get_beta_tester_stats():
    """Get beta tester statistics"""
    active_count = BetaTester.query.filter_by(status='active').count()
    inactive_count = BetaTester.query.filter_by(status='inactive').count()
    total_count = active_count + inactive_count
    
    return {
        'active': active_count,
        'inactive': inactive_count,
        'total': total_count,
        'max': MAX_BETA_TESTERS,
        'available_slots': max(0, MAX_BETA_TESTERS - active_count)
    }
    
def validate_beta_access_code(access_code):
    """Validate a beta access code"""
    expected_code = current_app.config.get('BETA_ACCESS_CODE')
    return access_code and expected_code and access_code.strip() == expected_code.strip()