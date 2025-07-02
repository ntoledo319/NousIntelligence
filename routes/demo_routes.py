#!/usr/bin/env python3
"""
Demo Routes - Demo Mode Access
Provides immediate demo access without authentication barriers
"""

import logging
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, redirect, request, session, jsonify, flash

logger = logging.getLogger(__name__)

# Create demo blueprint
demo_bp = Blueprint('demo', __name__)

@demo_bp.route('/demo', methods=['GET', 'POST'])
def activate_demo():
    """Activate demo mode - provides immediate access without authentication"""
    try:
        # Generate unique demo session ID to prevent session fixation
        demo_session_id = f"demo_{secrets.token_hex(8)}"
        
        # Create demo user session with expiration
        session['user'] = {
            'id': demo_session_id,
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True,
            'login_time': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
        # Set additional session flags
        session['demo_mode'] = True
        session['authenticated'] = True
        session.permanent = False  # Session expires when browser closes
        
        logger.info(f"Demo mode activated: {demo_session_id}")
        
        # Return success response for API calls or redirect for browser
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'user': session['user'],
                'message': 'Demo mode activated successfully',
                'redirect': '/demo'
            })
        else:
            return redirect('/demo')
        
    except Exception as e:
        logger.error(f"Demo activation error: {e}")
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': False,
                'error': 'Failed to activate demo mode'
            }), 500
        else:
            flash('Failed to activate demo mode. Please try again.', 'error')
            return redirect('/')

@demo_bp.route('/demo/status')
def demo_status():
    """Check demo mode status"""
    demo_active = session.get('demo_mode', False)
    user = session.get('user')
    
    return jsonify({
        'demo_active': demo_active,
        'authenticated': session.get('authenticated', False),
        'user': user,
        'expires_at': user.get('expires_at') if user else None
    })

@demo_bp.route('/demo/extend', methods=['POST'])
def extend_demo():
    """Extend demo session by 2 hours"""
    if not session.get('demo_mode'):
        return jsonify({'error': 'Not in demo mode'}), 400
    
    try:
        # Extend expiration by 2 hours
        new_expiry = datetime.now() + timedelta(hours=2)
        session['user']['expires_at'] = new_expiry.isoformat()
        
        return jsonify({
            'success': True,
            'expires_at': new_expiry.isoformat(),
            'message': 'Demo session extended for 2 hours'
        })
    except Exception as e:
        logger.error(f"Demo extension error: {e}")
        return jsonify({'error': 'Failed to extend demo session'}), 500