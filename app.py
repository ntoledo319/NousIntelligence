import os
import json
import datetime
import logging
from flask import Flask, request, redirect, session, url_for, render_template, jsonify, flash
from dotenv import load_dotenv

# Import custom utility modules
from utils.google_helper import get_google_flow, build_google_services
from utils.spotify_helper import get_spotify_client
from utils.scraper import scrape_aa_reflection
from utils.command_parser import parse_command
from utils.logger import log_workout, log_mood

# Load environment variables
load_dotenv()

# Flask config
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET") or "change_this_in_production!"

# OAuth config
GOOGLE_CLIENT_SECRETS = os.environ.get("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")
GOOGLE_REDIRECT = os.environ.get("GOOGLE_REDIRECT_URI", "https://toledonick981.repl.co/callback/google")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.environ.get("SPOTIFY_REDIRECT_URI", "https://toledonick981.repl.co/callback/spotify")

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    """Main entry point and command UI"""
    if request.method == "GET":
        return render_template("index.html", log=session.get("log", []))
    
    # Handle POST command
    cmd = request.form.get("cmd", "").lower().strip()
    if not cmd:
        flash("Please enter a command", "warning")
        return redirect(url_for("index"))
        
    log = session.setdefault("log", [])
    log.append(f">>> {cmd}")
    
    # Check for auth
    if "google_creds" not in session and not cmd.startswith("help"):
        session["log"] = log  # Save log before redirect
        flash("Please authorize Google services first", "info")
        return redirect(url_for("authorize_google"))

    # Handle commands
    try:
        if "google_creds" in session:
            cal, tasks, keep = build_google_services(session)
        else:
            cal, tasks, keep = None, None, None
            
        if "spotify_user" in session:
            sp, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT)
        else:
            sp = None
            
        result = parse_command(cmd, cal, tasks, keep, sp, log)
        if result.get("redirect"):
            return redirect(result.get("redirect"))
            
    except Exception as e:
        logging.error(f"Error processing command: {str(e)}")
        log.append(f"❌ Error: {str(e)}")
    
    session.modified = True
    return redirect(url_for("index"))

@app.route("/authorize/google")
def authorize_google():
    """Start Google OAuth flow"""
    flow = get_google_flow(GOOGLE_CLIENT_SECRETS, GOOGLE_REDIRECT)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route("/callback/google")
def callback_google():
    """Handle Google OAuth callback"""
    try:
        flow = get_google_flow(GOOGLE_CLIENT_SECRETS, GOOGLE_REDIRECT)
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        # Store the credentials in session
        creds_dict = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        
        # For token_uri we'll use the default from Google OAuth
        creds_dict['token_uri'] = "https://oauth2.googleapis.com/token"
        
        session['google_creds'] = creds_dict
        flash("Google services connected successfully!", "success")
    except Exception as e:
        logging.error(f"Google auth error: {str(e)}")
        flash(f"Error connecting Google services: {str(e)}", "danger")
    
    return redirect(url_for("index"))

@app.route("/authorize/spotify")
def authorize_spotify():
    """Start Spotify OAuth flow"""
    _, auth = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT)
    if not auth:
        flash("Error: Missing Spotify credentials", "danger")
        return redirect(url_for("index"))
        
    authorization_url = auth.get_authorize_url()
    return redirect(authorization_url)

@app.route("/callback/spotify")
def callback_spotify():
    """Handle Spotify OAuth callback"""
    try:
        _, auth = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT)
        if not auth:
            flash("Error: Missing Spotify credentials", "danger")
            return redirect(url_for("index"))
            
        code = request.args.get("code")
        token_info = auth.get_access_token(code)
        if token_info and 'scope' in token_info:
            session['spotify_user'] = token_info['scope']
            flash("Spotify connected successfully!", "success")
        else:
            flash("Error: Could not retrieve Spotify token", "danger")
    except Exception as e:
        logging.error(f"Spotify auth error: {str(e)}")
        flash(f"Error connecting Spotify: {str(e)}", "danger")
    
    return redirect(url_for("index"))

@app.route("/help")
def help_page():
    """Show available commands and help"""
    commands = [
        {"command": "add [event] at [time]", "description": "Create a calendar event"},
        {"command": "what's my day", "description": "Show today's calendar events"},
        {"command": "log workout: [details]", "description": "Log workout details"},
        {"command": "log mood: [mood] [details]", "description": "Log your mood"},
        {"command": "show aa reflection", "description": "Display AA daily reflection"},
        {"command": "play [song/artist]", "description": "Play music on Spotify"},
        {"command": "add task: [task]", "description": "Add a task to Google Tasks"},
        {"command": "add note: [note]", "description": "Add a note to Google Keep"},
        {"command": "help", "description": "Show this help menu"}
    ]
    return render_template("index.html", commands=commands)

@app.route("/clear")
def clear_log():
    """Clear the command log"""
    if "log" in session:
        session.pop("log")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    """Clear all session data"""
    session.clear()
    flash("You've been logged out. All credentials have been removed.", "info")
    return redirect(url_for("index"))
