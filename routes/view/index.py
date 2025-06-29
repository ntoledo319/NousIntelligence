"""

from utils.auth_compat import get_demo_user
def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user(), is_authenticated
    
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

Index View Routes

This module contains view routes for the main index/home page.

@module routes.view.index
@author NOUS Development Team
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session

# Create blueprint
index_bp = Blueprint('index', __name__)

@index_bp.route('/', methods=['GET', 'POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def index():
    """Main entry point and command UI"""
    # Check if user is authenticated
    if not ('user' in session and session['user']):
        # Show a welcome page for non-authenticated users
        return render_template("simple_welcome.html")

    if request.method == "GET":
        # Check if there's a command in the query parameters (from dashboard links)
        cmd_from_query = request.args.get("cmd")
        if cmd_from_query:
            session.setdefault("log", []).append(f">>> {cmd_from_query}")
            # Process the command
            return process_command(cmd_from_query)

        return render_template("index.html", log=session.get("log", []))

    # Handle POST command
    cmd = request.form.get("cmd", "").lower().strip()
    if not cmd:
        flash("Please enter a command", "warning")
        return redirect(url_for("index.index"))

    log = session.setdefault("log", [])
    log.append(f">>> {cmd}")

    # Process the command
    return process_command(cmd)

def process_command(cmd):
    """
    Process a command and return the appropriate response

    Args:
        cmd: Command string to process

    Returns:
        Flask response object
    """
    log = session.get("log", [])

    # Check for authentication
    if not ('user' in session and session['user']):
        session["log"] = log  # Save log before redirect
        flash("Demo mode active", "info")
        return redirect(url_for("main.demo"))

    # Get services (try both session and database)
    try:
        user_id = session.get('user', {}).get('id', 'demo_user')

        # Google services
        try:
            from utils.google_helper import build_google_services
            cal, tasks, keep = build_google_services(session, user_id)
        except Exception as e:
            if not cmd.startswith("help"):
                session["log"] = log  # Save log before redirect
                flash("Please connect your Google account to use most commands", "info")
                return redirect(url_for("auth.authorize_google"))
            cal, tasks, keep = None, None, None

        # Spotify
        try:
            from utils.spotify_helper import get_spotify_client

            # Get Spotify credentials from config
            from flask import current_app
            spotify_client_id = current_app.config.get('SPOTIFY_CLIENT_ID')
            spotify_client_secret = current_app.config.get('SPOTIFY_CLIENT_SECRET')
            spotify_redirect = current_app.config.get('SPOTIFY_REDIRECT_URI')

            sp, _ = get_spotify_client(session, spotify_client_id, spotify_client_secret, spotify_redirect, user_id)
        except Exception:
            sp = None

        from utils.command_parser import parse_command
        result = parse_command(cmd, cal, tasks, keep, sp, log, session)
        if result.get("redirect"):
            return redirect(result.get("redirect"))

    except Exception as e:
        logging.error(f"Error processing command: {str(e)}")
        log.append(f"❌ Error: {str(e)}")

    session.modified = True
    return redirect(url_for("index.index"))

@index_bp.route('/clear', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def clear_log():
    """Clear the command log"""
    session["log"] = []
    return redirect(url_for("index.index"))

@index_bp.route('/help', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def help_page():
    """Show help page"""
    return render_template("help.html")