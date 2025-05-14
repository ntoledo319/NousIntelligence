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
from utils.doctor_appointment_helper import (
    get_doctors, get_doctor_by_id, get_doctor_by_name, 
    add_doctor, update_doctor, delete_doctor,
    get_upcoming_appointments, get_appointments_by_doctor,
    add_appointment, update_appointment_status, set_appointment_reminder,
    get_due_appointment_reminders
)
from models import db, Doctor, Appointment, AppointmentReminder

# Load environment variables
load_dotenv()

# Flask config
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET") or "change_this_in_production!"

# Configure database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    print(f"Using database URL: {database_url}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        logging.info("Database tables created (if they didn't exist already)")
else:
    print("No DATABASE_URL found in environment variables")

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
            
        result = parse_command(cmd, cal, tasks, keep, sp, log, session)
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

# Doctor and appointment routes
@app.route("/api/doctors", methods=["GET"])
def api_get_doctors():
    """Get all doctors for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    doctors = get_doctors(session)
    return jsonify([doctor.to_dict() for doctor in doctors])

@app.route("/api/doctors", methods=["POST"])
def api_add_doctor():
    """Add a new doctor"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Doctor name is required"}), 400
    
    doctor = add_doctor(
        name=data.get("name"),
        specialty=data.get("specialty"),
        phone=data.get("phone"),
        address=data.get("address"),
        notes=data.get("notes"),
        session=session
    )
    
    if doctor:
        return jsonify(doctor.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add doctor"}), 500

@app.route("/api/doctors/<int:doctor_id>", methods=["GET"])
def api_get_doctor(doctor_id):
    """Get a specific doctor"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    doctor = get_doctor_by_id(doctor_id, session)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404
    
    return jsonify(doctor.to_dict())

@app.route("/api/doctors/<int:doctor_id>", methods=["PUT"])
def api_update_doctor(doctor_id):
    """Update a doctor"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    doctor = update_doctor(
        doctor_id=doctor_id,
        name=data.get("name"),
        specialty=data.get("specialty"),
        phone=data.get("phone"),
        address=data.get("address"),
        notes=data.get("notes"),
        session=session
    )
    
    if doctor:
        return jsonify(doctor.to_dict())
    else:
        return jsonify({"error": "Failed to update doctor or doctor not found"}), 404

@app.route("/api/doctors/<int:doctor_id>", methods=["DELETE"])
def api_delete_doctor(doctor_id):
    """Delete a doctor"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    success = delete_doctor(doctor_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete doctor or doctor not found"}), 404

@app.route("/api/appointments", methods=["GET"])
def api_get_appointments():
    """Get all upcoming appointments"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    appointments = get_upcoming_appointments(session)
    return jsonify([appointment.to_dict() for appointment in appointments])

@app.route("/api/doctors/<int:doctor_id>/appointments", methods=["GET"])
def api_get_doctor_appointments(doctor_id):
    """Get all appointments for a specific doctor"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    appointments = get_appointments_by_doctor(doctor_id, session)
    return jsonify([appointment.to_dict() for appointment in appointments])

@app.route("/api/appointments", methods=["POST"])
def api_add_appointment():
    """Add a new appointment"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    if not data or not data.get("doctor_id") or not data.get("date"):
        return jsonify({"error": "Doctor ID and date are required"}), 400
    
    try:
        date = datetime.datetime.fromisoformat(data.get("date"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    
    appointment = add_appointment(
        doctor_id=data.get("doctor_id"),
        date=date,
        reason=data.get("reason"),
        status=data.get("status", "scheduled"),
        notes=data.get("notes"),
        session=session
    )
    
    if appointment:
        return jsonify(appointment.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add appointment"}), 500

@app.route("/api/appointments/<int:appointment_id>/status", methods=["PUT"])
def api_update_appointment_status(appointment_id):
    """Update an appointment status"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    if not data or not data.get("status"):
        return jsonify({"error": "Status is required"}), 400
    
    appointment = update_appointment_status(
        appointment_id=appointment_id,
        new_status=data.get("status"),
        session=session
    )
    
    if appointment:
        return jsonify(appointment.to_dict())
    else:
        return jsonify({"error": "Failed to update appointment or appointment not found"}), 404

@app.route("/api/reminders/due", methods=["GET"])
def api_get_due_reminders():
    """Get all due appointment reminders"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    reminders = get_due_appointment_reminders(session)
    result = []
    for reminder in reminders:
        doctor = Doctor.query.get(reminder.doctor_id)
        doctor_name = doctor.name if doctor else "Unknown"
        result.append({
            "doctor_id": reminder.doctor_id,
            "doctor_name": doctor_name,
            "frequency_months": reminder.frequency_months,
            "last_appointment": reminder.last_appointment.isoformat() if reminder.last_appointment else None,
            "next_reminder": reminder.next_reminder.isoformat() if reminder.next_reminder else None
        })
    return jsonify(result)
