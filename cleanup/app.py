import os
import json
import datetime
import logging
from flask import Flask, request, redirect, session, url_for, render_template, jsonify, flash
from markupsafe import Markup
from dotenv import load_dotenv
from flask_login import LoginManager, current_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix

# Import custom utility modules
from utils.google_helper import get_google_flow, build_google_services
from utils.spotify_helper import get_spotify_client
from utils.scraper import scrape_aa_reflection
from utils.command_parser import parse_command
from utils.logger import log_workout, log_mood
from utils.ai_helper import cfhat  # Add import for cfhat function
from utils.weather_helper import (
    get_current_weather, get_weather_forecast, get_location_coordinates,
    format_weather_output, format_forecast_output, get_pressure_trend,
    calculate_pain_flare_risk, get_storm_severity, format_pain_forecast_output
)
# Import Spotify visualization blueprint
from routes.spotify_visualization import spotify_viz
from utils.doctor_appointment_helper import (
    get_doctors, get_doctor_by_id, get_doctor_by_name,
    add_doctor, update_doctor, delete_doctor,
    get_upcoming_appointments, get_appointments_by_doctor,
    add_appointment, update_appointment_status, set_appointment_reminder,
    get_due_appointment_reminders
)
from utils.shopping_helper import (
    get_shopping_lists, get_shopping_list_by_id, get_shopping_list_by_name,
    create_shopping_list, add_item_to_list, get_items_in_list,
    toggle_item_checked, remove_item_from_list, set_list_as_recurring,
    mark_list_as_ordered, get_due_shopping_lists
)
from utils.medication_helper import (
    get_medications, get_medication_by_id, get_medication_by_name,
    add_medication, update_medication_quantity, refill_medication,
    get_medications_to_refill, get_medications_by_doctor
)
from utils.product_helper import (
    get_products, get_product_by_id, get_product_by_name,
    add_product, set_product_as_recurring, mark_product_as_ordered,
    get_due_product_orders, update_product_price
)
from utils.budget_helper import (
    get_budgets, get_budget_by_id, get_budget_by_name, create_budget, update_budget,
    delete_budget, get_budget_summary, get_expenses, get_expense_by_id, add_expense,
    update_expense, delete_expense, get_recurring_payments, get_upcoming_payments,
    mark_payment_paid
)
from utils.travel_helper import (
    get_trips, get_trip_by_id, get_trip_by_name, create_trip, update_trip,
    delete_trip, get_trip_cost, get_upcoming_trips, get_active_trip,
    get_itinerary, add_itinerary_item, update_itinerary_item, delete_itinerary_item,
    get_accommodations, add_accommodation, update_accommodation, delete_accommodation,
    get_travel_documents, add_travel_document, update_travel_document, delete_travel_document,
    get_packing_list, add_packing_item, toggle_packed_status, delete_packing_item,
    generate_standard_packing_list, get_packing_progress
)
from models import db, Doctor, Appointment, AppointmentReminder, ShoppingList, ShoppingItem, Medication, Product
from models import Budget, Expense, RecurringPayment, Trip, ItineraryItem, Accommodation, TravelDocument, PackingItem, WeatherLocation

# Import the rate limit decorator
from utils.security_helper import rate_limit, log_security_event

# Load environment variables
load_dotenv()

# Flask config
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET") or "change_this_in_production!"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Beta Testing Mode
app.config['ENABLE_BETA_MODE'] = os.environ.get('ENABLE_BETA_MODE', 'true').lower() == 'true'
app.config['BETA_ACCESS_CODE'] = os.environ.get('BETA_ACCESS_CODE', 'BETANOUS2025')
app.config['MAX_BETA_TESTERS'] = int(os.environ.get('MAX_BETA_TESTERS', '30'))

# Configure database
database_url = os.environ.get("DATABASE_URL")
# Make sure DATABASE_URL is in the correct format for SQLAlchemy
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if database_url:
    print(f"Using database URL: {database_url}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,  # Verify connections before using from pool
        'pool_recycle': 600,    # Increase connection recycling to 10 minutes (was 300/5min)
        'pool_size': 20,        # Increase maximum connections in pool (was 10)
        'max_overflow': 10,     # Increase overflow connections (was 5)
        'pool_timeout': 30,     # Timeout for getting a connection from pool (seconds)
        'echo_pool': False,     # Don't log all pool checkouts/checkins
        'pool_use_lifo': True,  # Use last-in-first-out to reduce number of open connections
    }
    db.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            logging.info("Database tables created (if they didn't exist already)")

            # Start the maintenance scheduler
            from utils.maintenance_helper import start_maintenance_scheduler
            start_maintenance_scheduler()
            logging.info("Maintenance scheduler started")
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
else:
    print("No DATABASE_URL found in environment variables")

# Initialize LoginManager with Google Authentication
login_manager = LoginManager(app)
login_manager.login_view = "google_auth.login"  # Route function name in the blueprint
login_manager.login_message = "Please sign in with Google to access this page."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from models import User
    return User.query.get(user_id)

# Google authentication will be handled in routes.py to prevent duplicate registration

# Configure beta testing mode
from utils.beta_test_helper import configure_beta_mode
configure_beta_mode(app)

# Import and register the routes from routes package
from routes import register_blueprints
register_blueprints(app)

# Add custom template filters
import re
import jinja2

@app.template_filter('from_json')
def from_json(value):
    """Template filter to parse JSON strings"""
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

@app.template_filter('nl2br')
def nl2br(value):
    """Template filter to convert newlines to HTML line breaks"""
    if value:
        # Ensure value is a string and escape HTML characters
        value = str(value)
        value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        value = value.replace('\n', Markup('<br>'))
        return Markup(value)
    return ""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# OAuth config
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT = os.environ.get("GOOGLE_REDIRECT_URI", request.url_root.rstrip('/') + "/callback/google" if request else "https://mynous.replit.app/callback/google")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.environ.get("SPOTIFY_REDIRECT_URI", request.url_root.rstrip('/') + "/callback/spotify" if request else "https://mynous.replit.app/callback/spotify")

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

# Routes
@app.route("/settings")
def settings_page():
    """Display user settings page"""
    from models import UserSettings, ConversationDifficulty

    settings = None

    # Get settings for logged-in users from database
    if current_user.is_authenticated:
        settings = current_user.settings
    # For anonymous users, get from session if available
    elif 'conversation_difficulty' in session:
        # Create a simple dict with session values for template
        settings = {
            'conversation_difficulty': session.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value),
            'enable_voice_responses': session.get('enable_voice_responses', False),
            'preferred_language': session.get('preferred_language', 'en-US'),
            'theme': session.get('theme', 'light'),
            'color_theme': session.get('color_theme', 'default')
        }

    return render_template('settings.html', settings=settings)

@app.route("/settings", methods=['POST'])
@rate_limit(max_requests=30, time_window=60)  # 30 requests per minute
def save_settings():
    """Save user settings"""
    from utils.adaptive_conversation import set_difficulty

    # Get form data
    difficulty = request.form.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value)
    enable_voice = 'enable_voice_responses' in request.form
    language = request.form.get('preferred_language', 'en-US')
    theme = request.form.get('theme', 'light')
    color_theme = request.form.get('color_theme', 'default')

    # For logged-in users, save to database
    if current_user.is_authenticated:
        # Create settings if they don't exist
        if not current_user.settings:
            settings = UserSettings()
            settings.user_id = current_user.id
            settings.conversation_difficulty = difficulty
            settings.enable_voice_responses = enable_voice
            settings.preferred_language = language
            settings.theme = theme
            settings.color_theme = color_theme
            db.session.add(settings)
        else:
            # Update existing settings
            current_user.settings.conversation_difficulty = difficulty
            current_user.settings.enable_voice_responses = enable_voice
            current_user.settings.preferred_language = language
            current_user.settings.theme = theme
            current_user.settings.color_theme = color_theme

        db.session.commit()
        flash('Settings saved successfully', 'success')
    else:
        # For anonymous users, save to session
        session['conversation_difficulty'] = difficulty
        session['enable_voice_responses'] = enable_voice
        session['preferred_language'] = language
        session['theme'] = theme
        flash('Settings saved for this session', 'success')

    # Use our utility function to set the difficulty
    set_difficulty(difficulty)

    return redirect(url_for('index'))

@app.route("/", methods=["GET", "POST"])
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
        return redirect(url_for("index"))

    log = session.setdefault("log", [])
    log.append(f">>> {cmd}")

    # Process the command
    return process_command(cmd)

def process_command(cmd):
    """Process a command and return the appropriate response"""
    log = session.get("log", [])

    # Check for authentication
    if not current_user.is_authenticated:
        session["log"] = log  # Save log before redirect
        flash("Please log in to use the command interface", "info")
        return redirect(url_for("google_auth.login"))

    # Get services (try both session and database)
    try:
        user_id = current_user.id

        # Google services
        try:
            cal, tasks, keep = build_google_services(session, user_id)
        except Exception as e:
            if not cmd.startswith("help"):
                session["log"] = log  # Save log before redirect
                flash("Please connect your Google account to use most commands", "info")
                return redirect(url_for("authorize_google"))
            cal, tasks, keep = None, None, None

        # Spotify
        try:
            sp, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT, user_id)
        except Exception:
            sp = None

        result = parse_command(cmd, cal, tasks, keep, sp, log, session)
        if result.get("redirect"):
            return redirect(result.get("redirect"))

    except Exception as e:
        logging.error(f"Error processing command: {str(e)}")
        log.append(f"❌ Error: {str(e)}")

    session.modified = True
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Show dashboard with data visualizations and summaries"""
    # Check for beta access if beta mode is enabled
    if app.config.get('BETA_MODE', False):
        from utils.beta_test_helper import is_beta_tester
        if not is_beta_tester(current_user.id):
            flash("The dashboard is currently available only to beta testers.", "warning")
            return redirect(url_for('beta.request_access'))

    # Check for Google services connection
    if "google_creds" not in session:
        flash("Please connect your Google account to access all dashboard features", "warning")

    # Prepare data for the dashboard
    data = {}

    # Get budget data
    try:
        data['budget_summary'] = get_budget_summary(session)

        # Format budget categories for the chart
        if data['budget_summary'] and 'categories' in data['budget_summary']:
            # Filter out categories with 0 budget
            budget_categories = {
                cat: details['budget']
                for cat, details in data['budget_summary']['categories'].items()
                if details['budget'] > 0
            }
            data['budget_categories'] = budget_categories
    except Exception as e:
        logging.error(f"Error fetching budget data: {str(e)}")

    # Get trip data
    try:
        active_trip = get_active_trip(session)
        if active_trip:
            # Calculate days remaining
            today = datetime.datetime.now()
            days_left = (active_trip.end_date - today).days if active_trip.end_date else 0

            # Check if it has itinerary
            itinerary = get_itinerary(active_trip.id, session)

            trip_data = active_trip.to_dict()
            trip_data['days_left'] = days_left
            trip_data['has_itinerary'] = len(itinerary) > 0
            trip_data['itinerary_count'] = len(itinerary)

            data['active_trip'] = trip_data

        upcoming_trips = get_upcoming_trips(session)
        if upcoming_trips:
            # Format upcoming trips data
            upcoming_data = []
            for trip in upcoming_trips:
                today = datetime.datetime.now()
                days_until = (trip.start_date - today).days if trip.start_date else 0

                trip_dict = trip.to_dict()
                trip_dict['days_until'] = days_until
                upcoming_data.append(trip_dict)

            data['upcoming_trips'] = upcoming_data
    except Exception as e:
        logging.error(f"Error fetching trip data: {str(e)}")

    # Get appointment data
    try:
        from utils.doctor_appointment_helper import get_upcoming_appointments
        appointments = get_upcoming_appointments(session)
        if appointments:
            data['appointments'] = appointments

        # Check medications to refill
        from utils.medication_helper import get_medications_to_refill
        medications_to_refill = get_medications_to_refill(session)
        if medications_to_refill:
            data['medications_to_refill'] = medications_to_refill
    except Exception as e:
        logging.error(f"Error fetching health data: {str(e)}")

    # Get shopping data
    try:
        from utils.shopping_helper import get_shopping_lists, get_due_shopping_lists
        from utils.product_helper import get_due_product_orders

        shopping_lists = get_shopping_lists(session)
        if shopping_lists:
            data['shopping_lists'] = shopping_lists

            # Calculate total items
            total_items = sum(len(lst.items) for lst in shopping_lists if lst.items)
            data['total_items'] = total_items

            # Get due lists
            due_lists = get_due_shopping_lists(session)
            if due_lists:
                data['due_lists'] = due_lists

            # Get products to order
            products_to_order = get_due_product_orders(session)
            if products_to_order:
                data['products_to_order'] = products_to_order
    except Exception as e:
        logging.error(f"Error fetching shopping data: {str(e)}")

    # Get pain forecast data
    try:
        from models import WeatherLocation
        user_id = session.get("user_id")

        # Try to get user's primary location
        primary_location = WeatherLocation.query.filter_by(user_id=user_id, is_primary=True).first()

        if primary_location:
            # Get weather data for pain forecast
            weather_data = get_current_weather(primary_location.name)

            if weather_data:
                # Get pressure trend data
                pressure_trend = get_pressure_trend(primary_location.name, 24)

                if pressure_trend:
                    # Get storm severity data
                    storm_data = get_storm_severity(weather_data)

                    # Calculate pain flare risk
                    pain_risk = calculate_pain_flare_risk(pressure_trend, storm_data)

                    # Prepare data for the dashboard
                    data['pain_forecast'] = {
                        'location': pressure_trend['location'],
                        'current_pressure': pressure_trend['current_pressure'],
                        'trend_direction': pressure_trend['trend_direction'],
                        'pressure_change': pressure_trend['overall_change'],
                        'risk_level': pain_risk['risk_level'],
                        'risk_score': pain_risk['risk_score'],
                        'confidence': pain_risk['confidence'],
                        'factors': pain_risk['factors'],
                        'recommendation': pain_risk['recommendation']
                    }
    except Exception as e:
        logging.error(f"Error generating pain forecast: {str(e)}")

    # Create some recent activity (could be replaced with actual activity log)
    data['recent_activity'] = [
        {
            'action': 'Added budget',
            'description': 'Created monthly budget for groceries',
            'time_ago': '2 hours ago'
        },
        {
            'action': 'Booked flight',
            'description': 'Reserved tickets for Paris trip',
            'time_ago': '1 day ago'
        },
        {
            'action': 'Added expense',
            'description': 'Recorded $45.99 for dinner',
            'time_ago': '2 days ago'
        },
        {
            'action': 'Scheduled appointment',
            'description': 'Doctor visit on June 15',
            'time_ago': '3 days ago'
        },
    ]

    return render_template("dashboard.html", **data)

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
    # Require authentication
    if not current_user.is_authenticated:
        flash("Please log in first to connect your Google account", "warning")
        return redirect(url_for("google_auth.login"))

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
    # Require authentication
    if not current_user.is_authenticated:
        flash("Please log in first to connect your Google account", "warning")
        return redirect(url_for("google_auth.login"))

    try:
        from utils.auth_helper import save_google_credentials

        flow = get_google_flow(GOOGLE_CLIENT_SECRETS, GOOGLE_REDIRECT)
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials

        # Store the credentials in the database for this user
        save_google_credentials(current_user.id, creds)

        # Also store in session for current browser session
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
    # Require authentication
    if not current_user.is_authenticated:
        flash("Please log in first to connect your Spotify account", "warning")
        return redirect(url_for("google_auth.login"))

    _, auth = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT)
    if not auth:
        flash("Error: Missing Spotify credentials", "danger")
        return redirect(url_for("index"))

    authorization_url = auth.get_authorize_url()
    return redirect(authorization_url)

@app.route("/callback/spotify")
def callback_spotify():
    """Handle Spotify OAuth callback"""
    # Require authentication
    if not current_user.is_authenticated:
        flash("Please log in first to connect your Spotify account", "warning")
        return redirect(url_for("google_auth.login"))

    try:
        from utils.auth_helper import save_spotify_token

        _, auth = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT)
        if not auth:
            flash("Error: Missing Spotify credentials", "danger")
            return redirect(url_for("index"))

        code = request.args.get("code")
        token_info = auth.get_access_token(code)

        if token_info and 'scope' in token_info:
            # Save token to database for this user
            save_spotify_token(current_user.id, token_info)

            # Also store in session for current browser session
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
    return render_template("help.html")

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
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
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
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
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

# Shopping List API endpoints
@app.route("/api/shopping-lists", methods=["GET"])
def api_get_shopping_lists():
    """Get all shopping lists for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    shopping_lists = get_shopping_lists(session)
    return jsonify([lst.to_dict() for lst in shopping_lists])

@app.route("/api/shopping-lists", methods=["POST"])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def api_create_shopping_list():
    """Create a new shopping list"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "List name is required"}), 400

    shopping_list = create_shopping_list(
        name=data.get("name"),
        description=data.get("description"),
        store=data.get("store"),
        session=session
    )

    if shopping_list:
        return jsonify(shopping_list.to_dict()), 201
    else:
        return jsonify({"error": "Failed to create shopping list"}), 500

@app.route("/api/shopping-lists/<int:list_id>", methods=["GET"])
def api_get_shopping_list(list_id):
    """Get a specific shopping list"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    shopping_list = get_shopping_list_by_id(list_id, session)
    if not shopping_list:
        return jsonify({"error": "Shopping list not found"}), 404

    return jsonify(shopping_list.to_dict())

@app.route("/api/shopping-lists/<int:list_id>/items", methods=["GET"])
def api_get_list_items(list_id):
    """Get all items in a shopping list"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    items = get_items_in_list(list_id, session)
    return jsonify([item.to_dict() for item in items])

@app.route("/api/shopping-lists/<int:list_id>/items", methods=["POST"])
def api_add_list_item(list_id):
    """Add an item to a shopping list"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Item name is required"}), 400

    item = add_item_to_list(
        list_id=list_id,
        item_name=data.get("name"),
        quantity=data.get("quantity", 1),
        unit=data.get("unit"),
        category=data.get("category"),
        notes=data.get("notes"),
        session=session
    )

    if item:
        return jsonify(item.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add item to list"}), 500

@app.route("/api/shopping-lists/items/<int:item_id>/check", methods=["PUT"])
def api_toggle_item_checked(item_id):
    """Toggle an item as checked/unchecked"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if data is None or "is_checked" not in data:
        return jsonify({"error": "is_checked status is required"}), 400

    item = toggle_item_checked(item_id, data.get("is_checked"), session)
    if item:
        return jsonify(item.to_dict())
    else:
        return jsonify({"error": "Failed to update item or item not found"}), 404

@app.route("/api/shopping-lists/items/<int:item_id>", methods=["DELETE"])
def api_remove_list_item(item_id):
    """Remove an item from a shopping list"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = remove_item_from_list(item_id, session)
    if success:
        return jsonify({"status": "removed"})
    else:
        return jsonify({"error": "Failed to remove item or item not found"}), 404

@app.route("/api/shopping-lists/<int:list_id>/recurring", methods=["PUT"])
def api_set_list_recurring(list_id):
    """Set a shopping list as recurring"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("frequency_days"):
        return jsonify({"error": "frequency_days is required"}), 400

    try:
        frequency_days = int(data.get("frequency_days"))
    except (ValueError, TypeError):
        return jsonify({"error": "frequency_days must be a number"}), 400

    shopping_list = set_list_as_recurring(list_id, frequency_days, session)
    if shopping_list:
        return jsonify(shopping_list.to_dict())
    else:
        return jsonify({"error": "Failed to update list or list not found"}), 404

@app.route("/api/shopping-lists/<int:list_id>/ordered", methods=["PUT"])
def api_mark_list_ordered(list_id):
    """Mark a shopping list as ordered"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    shopping_list = mark_list_as_ordered(list_id, session)
    if shopping_list:
        return jsonify(shopping_list.to_dict())
    else:
        return jsonify({"error": "Failed to update list or list not found"}), 404

@app.route("/api/shopping-lists/due", methods=["GET"])
def api_get_due_lists():
    """Get shopping lists that are due for ordering"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    shopping_lists = get_due_shopping_lists(session)
    return jsonify([lst.to_dict() for lst in shopping_lists])

# Medication API endpoints
@app.route("/api/medications", methods=["GET"])
def api_get_medications():
    """Get all medications for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    medications = get_medications(session)
    return jsonify([med.to_dict() for med in medications])

@app.route("/api/medications", methods=["POST"])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def api_add_medication():
    """Add a new medication"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Medication name is required"}), 400

    medication = add_medication(
        name=data.get("name"),
        dosage=data.get("dosage"),
        instructions=data.get("instructions"),
        doctor_name=data.get("doctor_name"),
        pharmacy=data.get("pharmacy"),
        quantity=data.get("quantity"),
        refills=data.get("refills"),
        session=session
    )

    if medication:
        return jsonify(medication.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add medication"}), 500

@app.route("/api/medications/<int:medication_id>", methods=["GET"])
def api_get_medication(medication_id):
    """Get a specific medication"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    medication = get_medication_by_id(medication_id, session)
    if not medication:
        return jsonify({"error": "Medication not found"}), 404

    return jsonify(medication.to_dict())

@app.route("/api/medications/<int:medication_id>/quantity", methods=["PUT"])
def api_update_medication_quantity(medication_id):
    """Update a medication's remaining quantity"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or "quantity" not in data:
        return jsonify({"error": "Quantity is required"}), 400

    try:
        quantity = int(data.get("quantity"))
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity must be a number"}), 400

    medication = update_medication_quantity(medication_id, quantity, session)
    if medication:
        return jsonify(medication.to_dict())
    else:
        return jsonify({"error": "Failed to update medication or medication not found"}), 404

@app.route("/api/medications/<int:medication_id>/refill", methods=["PUT"])
def api_refill_medication(medication_id):
    """Record a medication refill"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or "quantity_added" not in data:
        return jsonify({"error": "quantity_added is required"}), 400

    try:
        quantity_added = int(data.get("quantity_added"))
        refills_remaining = int(data.get("refills_remaining")) if "refills_remaining" in data else None
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity values must be numbers"}), 400

    medication = refill_medication(medication_id, quantity_added, refills_remaining, session)
    if medication:
        return jsonify(medication.to_dict())
    else:
        return jsonify({"error": "Failed to refill medication or medication not found"}), 404

@app.route("/api/medications/refill-needed", methods=["GET"])
def api_get_medications_to_refill():
    """Get medications that need to be refilled"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    medications = get_medications_to_refill(session)
    return jsonify([med.to_dict() for med in medications])

@app.route("/api/doctors/<int:doctor_id>/medications", methods=["GET"])
def api_get_doctor_medications(doctor_id):
    """Get medications prescribed by a specific doctor"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    medications = get_medications_by_doctor(doctor_id, session)
    return jsonify([med.to_dict() for med in medications])

# Product API endpoints
@app.route("/api/products", methods=["GET"])
def api_get_products():
    """Get all tracked products for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    products = get_products(session)
    return jsonify([product.to_dict() for product in products])

@app.route("/api/products", methods=["POST"])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def api_add_product():
    """Add a new product to track"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Product name is required"}), 400

    product = add_product(
        name=data.get("name"),
        url=data.get("url"),
        description=data.get("description"),
        price=data.get("price"),
        source=data.get("source"),
        session=session
    )

    if product:
        return jsonify(product.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add product"}), 500

@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_get_product(product_id):
    """Get a specific product"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    product = get_product_by_id(product_id, session)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product.to_dict())

@app.route("/api/products/<int:product_id>/recurring", methods=["PUT"])
def api_set_product_recurring(product_id):
    """Set a product as recurring"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("frequency_days"):
        return jsonify({"error": "frequency_days is required"}), 400

    try:
        frequency_days = int(data.get("frequency_days"))
    except (ValueError, TypeError):
        return jsonify({"error": "frequency_days must be a number"}), 400

    product = set_product_as_recurring(product_id, frequency_days, session)
    if product:
        return jsonify(product.to_dict())
    else:
        return jsonify({"error": "Failed to update product or product not found"}), 404

@app.route("/api/products/<int:product_id>/ordered", methods=["PUT"])
def api_mark_product_ordered(product_id):
    """Mark a product as ordered"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    product = mark_product_as_ordered(product_id, session)
    if product:
        return jsonify(product.to_dict())
    else:
        return jsonify({"error": "Failed to update product or product not found"}), 404

@app.route("/api/products/due", methods=["GET"])
def api_get_due_products():
    """Get products that are due for ordering"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    products = get_due_product_orders(session)
    return jsonify([product.to_dict() for product in products])

@app.route("/api/products/<int:product_id>/price", methods=["PUT"])
def api_update_product_price(product_id):
    """Update a product's price"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or "price" not in data:
        return jsonify({"error": "Price is required"}), 400

    try:
        price = float(data.get("price"))
    except (ValueError, TypeError):
        return jsonify({"error": "Price must be a number"}), 400

    product = update_product_price(product_id, price, session)
    if product:
        return jsonify(product.to_dict())
    else:
        return jsonify({"error": "Failed to update product or product not found"}), 404

# Budget & Expense Tracking API endpoints
@app.route("/api/budgets", methods=["GET"])
def api_get_budgets():
    """Get all budgets for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    budgets = get_budgets(session)
    return jsonify([budget.to_dict() for budget in budgets])

@app.route("/api/budgets/summary", methods=["GET"])
def api_get_budget_summary():
    """Get a summary of all budgets for the current month"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    summary = get_budget_summary(session)
    return jsonify(summary)

@app.route("/api/budgets", methods=["POST"])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def api_create_budget():
    """Create a new budget"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name") or "amount" not in data:
        return jsonify({"error": "Name and amount are required"}), 400

    try:
        amount = float(data.get("amount"))
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a number"}), 400

    budget = create_budget(
        name=data.get("name"),
        amount=amount,
        category=data.get("category"),
        is_recurring=data.get("is_recurring", True),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        session=session
    )

    if budget:
        return jsonify(budget.to_dict()), 201
    else:
        return jsonify({"error": "Failed to create budget"}), 500

@app.route("/api/budgets/<int:budget_id>", methods=["GET"])
def api_get_budget(budget_id):
    """Get a specific budget"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    budget = get_budget_by_id(budget_id, session)
    if not budget:
        return jsonify({"error": "Budget not found"}), 404

    return jsonify(budget.to_dict())

@app.route("/api/budgets/<int:budget_id>", methods=["PUT"])
def api_update_budget(budget_id):
    """Update a budget"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        amount = float(data.get("amount")) if "amount" in data else None
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a number"}), 400

    budget = update_budget(
        budget_id=budget_id,
        name=data.get("name"),
        amount=amount,
        category=data.get("category"),
        is_recurring=data.get("is_recurring"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        session=session
    )

    if budget:
        return jsonify(budget.to_dict())
    else:
        return jsonify({"error": "Failed to update budget or budget not found"}), 404

@app.route("/api/budgets/<int:budget_id>", methods=["DELETE"])
def api_delete_budget(budget_id):
    """Delete a budget"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = delete_budget(budget_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete budget or budget not found"}), 404

@app.route("/api/expenses", methods=["GET"])
def api_get_expenses():
    """Get all expenses for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    # Parse optional query parameters for filtering
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    category = request.args.get("category")

    expenses = get_expenses(session, start_date, end_date, category)
    return jsonify([expense.to_dict() for expense in expenses])

@app.route("/api/expenses", methods=["POST"])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def api_add_expense():
    """Add a new expense"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("description") or "amount" not in data:
        return jsonify({"error": "Description and amount are required"}), 400

    try:
        amount = float(data.get("amount"))
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a number"}), 400

    expense = add_expense(
        description=data.get("description"),
        amount=amount,
        date=data.get("date"),
        category=data.get("category"),
        payment_method=data.get("payment_method"),
        budget_name=data.get("budget_name"),
        is_recurring=data.get("is_recurring", False),
        recurring_frequency=data.get("recurring_frequency"),
        next_due_date=data.get("next_due_date"),
        notes=data.get("notes"),
        session=session
    )

    if expense:
        return jsonify(expense.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add expense"}), 500

@app.route("/api/expenses/<int:expense_id>", methods=["GET"])
def api_get_expense(expense_id):
    """Get a specific expense"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    expense = get_expense_by_id(expense_id, session)
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify(expense.to_dict())

@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def api_update_expense(expense_id):
    """Update an expense"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        amount = float(data.get("amount")) if "amount" in data else None
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be a number"}), 400

    expense = update_expense(
        expense_id=expense_id,
        description=data.get("description"),
        amount=amount,
        date=data.get("date"),
        category=data.get("category"),
        payment_method=data.get("payment_method"),
        budget_name=data.get("budget_name"),
        is_recurring=data.get("is_recurring"),
        recurring_frequency=data.get("recurring_frequency"),
        next_due_date=data.get("next_due_date"),
        notes=data.get("notes"),
        session=session
    )

    if expense:
        return jsonify(expense.to_dict())
    else:
        return jsonify({"error": "Failed to update expense or expense not found"}), 404

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def api_delete_expense(expense_id):
    """Delete an expense"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = delete_expense(expense_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete expense or expense not found"}), 404

@app.route("/api/recurring-payments", methods=["GET"])
def api_get_recurring_payments():
    """Get all recurring payments for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    payments = get_recurring_payments(session)
    return jsonify([payment.to_dict() for payment in payments])

@app.route("/api/recurring-payments/upcoming", methods=["GET"])
def api_get_upcoming_payments():
    """Get upcoming payments due in the next 30 days"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    # Get days parameter (default: 30)
    days = request.args.get("days", 30, type=int)

    payments = get_upcoming_payments(session, days)
    return jsonify([payment.to_dict() for payment in payments])

@app.route("/api/recurring-payments/<int:payment_id>/paid", methods=["PUT"])
def api_mark_payment_paid(payment_id):
    """Mark a recurring payment as paid"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    payment = mark_payment_paid(payment_id, session)
    if payment:
        return jsonify(payment.to_dict())
    else:
        return jsonify({"error": "Failed to mark payment as paid or payment not found"}), 404

# Travel Planning API endpoints
@app.route("/api/trips", methods=["GET"])
def api_get_trips():
    """Get all trips for the current user"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    # Parse optional query parameters
    include_past = request.args.get("include_past", "false").lower() == "true"

    trips = get_trips(session, include_past)
    return jsonify([trip.to_dict() for trip in trips])

@app.route("/api/trips/upcoming", methods=["GET"])
def api_get_upcoming_trips():
    """Get trips starting in the next 30 days"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    # Get days parameter (default: 30)
    days = request.args.get("days", 30, type=int)

    trips = get_upcoming_trips(session, days)
    return jsonify([trip.to_dict() for trip in trips])

@app.route("/api/trips/active", methods=["GET"])
def api_get_active_trip():
    """Get currently active trip (if any)"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    trip = get_active_trip(session)
    if trip:
        return jsonify(trip.to_dict())
    else:
        return jsonify({"message": "No active trip found"}), 404

@app.route("/api/trips", methods=["POST"])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def api_create_trip():
    """Create a new trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name") or not data.get("destination"):
        return jsonify({"error": "Name and destination are required"}), 400

    trip = create_trip(
        name=data.get("name"),
        destination=data.get("destination"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        budget=data.get("budget"),
        notes=data.get("notes"),
        session=session
    )

    if trip:
        return jsonify(trip.to_dict()), 201
    else:
        return jsonify({"error": "Failed to create trip"}), 500

@app.route("/api/trips/<int:trip_id>", methods=["GET"])
def api_get_trip(trip_id):
    """Get a specific trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    trip = get_trip_by_id(trip_id, session)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify(trip.to_dict())

@app.route("/api/trips/<int:trip_id>/cost", methods=["GET"])
def api_get_trip_cost(trip_id):
    """Get the total cost of a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    cost_data = get_trip_cost(trip_id, session)
    if not cost_data:
        return jsonify({"error": "Trip not found"}), 404

    return jsonify(cost_data)

@app.route("/api/trips/<int:trip_id>", methods=["PUT"])
def api_update_trip(trip_id):
    """Update a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    trip = update_trip(
        trip_id=trip_id,
        name=data.get("name"),
        destination=data.get("destination"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        budget=data.get("budget"),
        notes=data.get("notes"),
        session=session
    )

    if trip:
        return jsonify(trip.to_dict())
    else:
        return jsonify({"error": "Failed to update trip or trip not found"}), 404

@app.route("/api/trips/<int:trip_id>", methods=["DELETE"])
def api_delete_trip(trip_id):
    """Delete a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = delete_trip(trip_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete trip or trip not found"}), 404

# Itinerary endpoints
@app.route("/api/trips/<int:trip_id>/itinerary", methods=["GET"])
def api_get_itinerary(trip_id):
    """Get all itinerary items for a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    items = get_itinerary(trip_id, session)
    return jsonify([item.to_dict() for item in items])

@app.route("/api/trips/<int:trip_id>/itinerary", methods=["POST"])
def api_add_itinerary_item(trip_id):
    """Add an item to a trip itinerary"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Item name is required"}), 400

    item = add_itinerary_item(
        trip_id=trip_id,
        name=data.get("name"),
        date=data.get("date"),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        location=data.get("location"),
        address=data.get("address"),
        category=data.get("category"),
        cost=data.get("cost"),
        reservation_confirmation=data.get("reservation_confirmation"),
        notes=data.get("notes"),
        session=session
    )

    if item:
        return jsonify(item.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add itinerary item"}), 500

@app.route("/api/itinerary/<int:item_id>", methods=["PUT"])
def api_update_itinerary_item(item_id):
    """Update an itinerary item"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    item = update_itinerary_item(
        item_id=item_id,
        name=data.get("name"),
        date=data.get("date"),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        location=data.get("location"),
        address=data.get("address"),
        category=data.get("category"),
        cost=data.get("cost"),
        reservation_confirmation=data.get("reservation_confirmation"),
        notes=data.get("notes"),
        session=session
    )

    if item:
        return jsonify(item.to_dict())
    else:
        return jsonify({"error": "Failed to update itinerary item or item not found"}), 404

@app.route("/api/itinerary/<int:item_id>", methods=["DELETE"])
def api_delete_itinerary_item(item_id):
    """Delete an itinerary item"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = delete_itinerary_item(item_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete itinerary item or item not found"}), 404

# Accommodation endpoints
@app.route("/api/trips/<int:trip_id>/accommodations", methods=["GET"])
def api_get_accommodations(trip_id):
    """Get all accommodations for a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    accommodations = get_accommodations(trip_id, session)
    return jsonify([accommodation.to_dict() for accommodation in accommodations])

@app.route("/api/trips/<int:trip_id>/accommodations", methods=["POST"])
def api_add_accommodation(trip_id):
    """Add an accommodation to a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Accommodation name is required"}), 400

    accommodation = add_accommodation(
        trip_id=trip_id,
        name=data.get("name"),
        check_in_date=data.get("check_in_date"),
        check_out_date=data.get("check_out_date"),
        address=data.get("address"),
        booking_confirmation=data.get("booking_confirmation"),
        booking_site=data.get("booking_site"),
        phone=data.get("phone"),
        cost=data.get("cost"),
        notes=data.get("notes"),
        session=session
    )

    if accommodation:
        return jsonify(accommodation.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add accommodation"}), 500

@app.route("/api/accommodations/<int:accommodation_id>", methods=["PUT"])
def api_update_accommodation(accommodation_id):
    """Update an accommodation"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    accommodation = update_accommodation(
        accommodation_id=accommodation_id,
        name=data.get("name"),
        check_in_date=data.get("check_in_date"),
        check_out_date=data.get("check_out_date"),
        address=data.get("address"),
        booking_confirmation=data.get("booking_confirmation"),
        booking_site=data.get("booking_site"),
        phone=data.get("phone"),
        cost=data.get("cost"),
        notes=data.get("notes"),
        session=session
    )

    if accommodation:
        return jsonify(accommodation.to_dict())
    else:
        return jsonify({"error": "Failed to update accommodation or accommodation not found"}), 404

@app.route("/api/accommodations/<int:accommodation_id>", methods=["DELETE"])
def api_delete_accommodation(accommodation_id):
    """Delete an accommodation"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = delete_accommodation(accommodation_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete accommodation or accommodation not found"}), 404

# Travel documents endpoints
@app.route("/api/trips/<int:trip_id>/documents", methods=["GET"])
def api_get_travel_documents(trip_id):
    """Get all travel documents for a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    documents = get_travel_documents(trip_id, session)
    return jsonify([document.to_dict() for document in documents])

@app.route("/api/trips/<int:trip_id>/documents", methods=["POST"])
def api_add_travel_document(trip_id):
    """Add a travel document to a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Document name is required"}), 400

    document = add_travel_document(
        trip_id=trip_id,
        name=data.get("name"),
        document_type=data.get("document_type"),
        confirmation_number=data.get("confirmation_number"),
        provider=data.get("provider"),
        departure_location=data.get("departure_location"),
        arrival_location=data.get("arrival_location"),
        departure_time=data.get("departure_time"),
        arrival_time=data.get("arrival_time"),
        cost=data.get("cost"),
        notes=data.get("notes"),
        session=session
    )

    if document:
        return jsonify(document.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add travel document"}), 500

@app.route("/api/documents/<int:document_id>", methods=["PUT"])
def api_update_travel_document(document_id):
    """Update a travel document"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    document = update_travel_document(
        document_id=document_id,
        name=data.get("name"),
        document_type=data.get("document_type"),
        confirmation_number=data.get("confirmation_number"),
        provider=data.get("provider"),
        departure_location=data.get("departure_location"),
        arrival_location=data.get("arrival_location"),
        departure_time=data.get("departure_time"),
        arrival_time=data.get("arrival_time"),
        cost=data.get("cost"),
        notes=data.get("notes"),
        session=session
    )

    if document:
        return jsonify(document.to_dict())
    else:
        return jsonify({"error": "Failed to update travel document or document not found"}), 404

@app.route("/api/documents/<int:document_id>", methods=["DELETE"])
def api_delete_travel_document(document_id):
    """Delete a travel document"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = delete_travel_document(document_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete travel document or document not found"}), 404

# Packing list endpoints
@app.route("/api/trips/<int:trip_id>/packing", methods=["GET"])
def api_get_packing_list(trip_id):
    """Get all packing items for a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    items = get_packing_list(trip_id, session)
    return jsonify([item.to_dict() for item in items])

@app.route("/api/trips/<int:trip_id>/packing/progress", methods=["GET"])
def api_get_packing_progress(trip_id):
    """Get packing progress statistics"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    progress = get_packing_progress(trip_id, session)
    if progress:
        return jsonify(progress)
    else:
        return jsonify({"error": "Trip not found"}), 404

@app.route("/api/trips/<int:trip_id>/packing/generate", methods=["POST"])
def api_generate_packing_list(trip_id):
    """Generate a standard packing list for a trip"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    items = generate_standard_packing_list(trip_id, session)
    if items:
        return jsonify({"message": f"Generated {len(items)} packing items"}), 201
    else:
        return jsonify({"error": "Failed to generate packing list"}), 500

@app.route("/api/trips/<int:trip_id>/packing", methods=["POST"])
def api_add_packing_item(trip_id):
    """Add an item to a trip packing list"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Item name is required"}), 400

    item = add_packing_item(
        trip_id=trip_id,
        name=data.get("name"),
        category=data.get("category"),
        quantity=data.get("quantity", 1),
        notes=data.get("notes"),
        session=session
    )

    if item:
        return jsonify(item.to_dict()), 201
    else:
        return jsonify({"error": "Failed to add packing item"}), 500

@app.route("/api/packing/<int:item_id>/toggle", methods=["PUT"])
def api_toggle_packed_status(item_id):
    """Toggle the packed status of a packing item"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    item = toggle_packed_status(item_id, session)
    if item:
        return jsonify(item.to_dict())
    else:
        return jsonify({"error": "Failed to toggle item status or item not found"}), 404

@app.route("/api/packing/<int:item_id>", methods=["DELETE"])
def api_delete_packing_item(item_id):
    """Delete a packing item"""
    if "google_creds" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    success = delete_packing_item(item_id, session)
    if success:
        return jsonify({"status": "deleted"})
    else:
        return jsonify({"error": "Failed to delete packing item or item not found"}), 404


# Weather API endpoints
@app.route("/api/weather/current", methods=["GET"])
def api_get_current_weather():
    """Get current weather for a location"""
    try:
        location = request.args.get("location")
        units = request.args.get("units", "imperial")

        if not location:
            # Try to get primary saved location
            primary_location = WeatherLocation.query.filter_by(user_id=session.get("user_id"), is_primary=True).first()

            if primary_location:
                # Update last accessed time
                primary_location.last_accessed = datetime.utcnow()
                db.session.commit()

                # Get weather using coordinates
                weather_data = get_current_weather(f"{primary_location.latitude},{primary_location.longitude}", primary_location.units)
                return jsonify({"success": True, "location": primary_location.to_dict(), "weather": weather_data})
            else:
                return jsonify({"success": False, "error": "No location provided and no primary location saved"}), 400

        # Get weather for the provided location
        weather_data = get_current_weather(location, units)

        if not weather_data:
            return jsonify({"success": False, "error": "Location not found"}), 404

        return jsonify({"success": True, "weather": weather_data})
    except Exception as e:
        logging.error(f"Error getting weather: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/weather/forecast", methods=["GET"])
def api_get_weather_forecast():
    """Get weather forecast for a location"""
    try:
        location = request.args.get("location")
        days = int(request.args.get("days", "5"))
        units = request.args.get("units", "imperial")

        if not location:
            # Try to get primary saved location
            primary_location = WeatherLocation.query.filter_by(user_id=session.get("user_id"), is_primary=True).first()

            if primary_location:
                # Update last accessed time
                primary_location.last_accessed = datetime.utcnow()
                db.session.commit()

                # Get forecast using coordinates
                forecast_data = get_weather_forecast(f"{primary_location.latitude},{primary_location.longitude}", days, primary_location.units)
                return jsonify({"success": True, "location": primary_location.to_dict(), "forecast": forecast_data})
            else:
                return jsonify({"success": False, "error": "No location provided and no primary location saved"}), 400

        # Get forecast for provided location
        forecast_data = get_weather_forecast(location, days, units)

        if not forecast_data:
            return jsonify({"success": False, "error": "Location not found"}), 404

        return jsonify({"success": True, "forecast": forecast_data})
    except Exception as e:
        logging.error(f"Error getting weather forecast: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/weather/locations", methods=["GET"])
def api_get_weather_locations():
    """Get all saved weather locations for the current user"""
    try:
        user_id = session.get("user_id")
        locations = WeatherLocation.query.filter_by(user_id=user_id).all()
        return jsonify({"success": True, "locations": [loc.to_dict() for loc in locations]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/weather/locations", methods=["POST"])
def api_add_weather_location():
    """Add a new weather location"""
    try:
        data = request.json
        location_name = data.get("name")

        if not location_name:
            return jsonify({"success": False, "error": "Location name is required"}), 400

        # Get coordinates using OpenWeatherMap Geocoding API
        lat, lon, display_name = get_location_coordinates(location_name)

        if lat is None or lon is None:
            return jsonify({"success": False, "error": "Location not found"}), 404

        user_id = session.get("user_id")
        is_primary = data.get("is_primary", False)

        # If setting as primary, remove primary flag from other locations
        if is_primary:
            WeatherLocation.query.filter_by(user_id=user_id, is_primary=True).update({"is_primary": False})

        # Create new location
        new_location = WeatherLocation(
            name=location_name,
            display_name=display_name,
            latitude=lat,
            longitude=lon,
            is_primary=is_primary,
            units=data.get("units", "imperial"),
            user_id=user_id,
            last_accessed=datetime.utcnow()
        )

        db.session.add(new_location)
        db.session.commit()

        return jsonify({"success": True, "location": new_location.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/weather/locations/<int:location_id>", methods=["DELETE"])
def api_delete_weather_location(location_id):
    """Delete a saved weather location"""
    try:
        location = WeatherLocation.query.filter_by(id=location_id, user_id=session.get("user_id")).first()

        if not location:
            return jsonify({"success": False, "error": "Location not found"}), 404

        db.session.delete(location)
        db.session.commit()

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/weather/locations/<int:location_id>/primary", methods=["PUT"])
def api_set_primary_weather_location(location_id):
    """Set a location as the primary weather location"""
    try:
        user_id = session.get("user_id")

        # Remove primary flag from all locations
        WeatherLocation.query.filter_by(user_id=user_id, is_primary=True).update({"is_primary": False})

        # Set new primary location
        location = WeatherLocation.query.filter_by(id=location_id, user_id=user_id).first()

        if not location:
            return jsonify({"success": False, "error": "Location not found"}), 404

        location.is_primary = True
        location.last_accessed = datetime.utcnow()
        db.session.commit()

        return jsonify({"success": True, "location": location.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/weather/pain-forecast", methods=["GET"])
def api_pain_flare_forecast():
    """API endpoint to get pain flare forecast based on weather"""
    try:
        # Get location parameters
        location = request.args.get('location')
        lat = request.args.get('lat')
        lon = request.args.get('lon')

        # Either location name or coordinates must be provided
        if not location and not (lat and lon):
            return jsonify({"error": "Either location name or lat/lon coordinates must be provided"}), 400

        # Get forecast
        if location:
            # Get by location name
            forecast = get_pain_flare_forecast(location)
        else:
            # Get by coordinates
            lat = float(lat)
            lon = float(lon)
            forecast = get_pain_flare_forecast(None, lat, lon)

        if not forecast:
            return jsonify({"error": "Unable to get pain flare forecast"}), 404

        return jsonify(forecast)
    except Exception as e:
        logging.error(f"Error getting pain flare forecast: {str(e)}")
        return jsonify({"error": "Error processing request"}), 500

# Health Check Endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring system health"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "version": os.environ.get("APP_VERSION", "1.0.0"),
            "components": {}
        }

        # Check database connection
        try:
            # Simple query to check if database is responsive
            db.session.execute("SELECT 1").scalar()
            health_status["components"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }

        # Check OpenRouter API (if configured)
        from utils.key_config import APIKeyManager
        openrouter_key = APIKeyManager.get_key("openrouter")
        if openrouter_key:
            health_status["components"]["openrouter"] = {
                "status": "configured",
                "message": "OpenRouter API key is configured"
            }
        else:
            health_status["components"]["openrouter"] = {
                "status": "unconfigured",
                "message": "OpenRouter API key is not configured"
            }

        # Check external services (just check connectivity)
        external_services = ["https://openrouter.ai/", "https://huggingface.co/"]
        health_status["components"]["external_services"] = {}
        import requests
        for service_url in external_services:
            try:
                # Just check if the service is reachable with a 2s timeout
                response = requests.head(service_url, timeout=2)
                health_status["components"]["external_services"][service_url] = {
                    "status": "reachable" if response.status_code < 400 else "error",
                    "code": response.status_code
                }
            except requests.RequestException as e:
                health_status["components"]["external_services"][service_url] = {
                    "status": "unreachable",
                    "message": str(e)
                }

        # Check file system (make sure important directories are writable)
        upload_dir = os.path.join(app.root_path, 'uploads')
        if os.path.exists(upload_dir):
            if os.access(upload_dir, os.W_OK):
                health_status["components"]["filesystem"] = {
                    "status": "writable",
                    "message": "Upload directory is writable"
                }
            else:
                health_status["status"] = "unhealthy"
                health_status["components"]["filesystem"] = {
                    "status": "unwritable",
                    "message": "Upload directory is not writable"
                }
        else:
            health_status["components"]["filesystem"] = {
                "status": "missing",
                "message": "Upload directory does not exist"
            }

        # Return appropriate status code
        status_code = 200 if health_status["status"] == "healthy" else 503
        return jsonify(health_status), status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error running health check: {str(e)}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500

# Main entry point
if __name__ == "__main__":
    from config import PORT, HOST, DEBUG
    app.run(host=HOST, port=PORT, debug=DEBUG)
