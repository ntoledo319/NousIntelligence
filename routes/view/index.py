"""
Index View Routes

This module contains view routes for the main index/home page.

@module routes.view.index
@author NOUS Development Team
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required

# Create blueprint
index_bp = Blueprint('index', __name__)


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    """Main entry point and command UI"""
    # Check if user is authenticated
    if not current_user.is_authenticated:
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
    if not current_user.is_authenticated:
        session["log"] = log  # Save log before redirect
        flash("Please log in to use the command interface", "info")
        return redirect(url_for("auth.login"))
    
    # Get services (try both session and database)
    try:
        user_id = current_user.id
        
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
def clear_log():
    """Clear the command log"""
    session["log"] = []
    return redirect(url_for("index.index"))


@index_bp.route('/help', methods=['GET'])
def help_page():
    """Show help page"""
    return render_template("help.html") 