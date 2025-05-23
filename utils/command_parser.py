import datetime
import logging
from flask import url_for
import re
from utils.logger import log_workout, log_mood
from utils.scraper import scrape_aa_reflection
from utils.ai_helper import parse_natural_language
from utils.doctor_appointment_helper import (
    get_doctors, get_doctor_by_name, add_doctor, 
    add_appointment, get_upcoming_appointments,
    get_due_appointment_reminders
)
from utils.shopping_helper import (
    get_shopping_lists, get_shopping_list_by_name, create_shopping_list,
    add_item_to_list, get_items_in_list, toggle_item_checked,
    get_due_shopping_lists
)
from utils.medication_helper import (
    get_medications, get_medication_by_name, add_medication,
    update_medication_quantity, refill_medication, get_medications_to_refill
)
from utils.product_helper import (
    get_products, add_product, get_product_by_name,
    set_product_as_recurring, mark_product_as_ordered, get_due_product_orders
)
from models import Doctor, ShoppingList, ShoppingItem, Medication, Product

def parse_command(cmd, calendar, tasks, keep, spotify, log, session=None):
    """
    Parse and execute user commands, with natural language support
    """
    result = {"redirect": None}
    
    # First, try to use AI to understand natural language commands
    try:
        # Check if this is a built-in command that doesn't need AI parsing
        if cmd in ["help", "clear", "logout", "connect spotify", "connect google"] or \
           cmd.startswith("add ") and " at " in cmd or \
           cmd.startswith("what's my day") or cmd.startswith("whats my day") or \
           "aa reflection" in cmd or "daily reflection" in cmd or \
           cmd.startswith("log workout") or cmd.startswith("log mood") or \
           cmd.startswith("add task") or cmd.startswith("add note") or \
           cmd.startswith("play "):
            # Use the standard parsing logic for recognized command formats
            pass
        else:
            # Try AI parsing for natural language
            ai_parsed = parse_natural_language(cmd)
            
            if ai_parsed and isinstance(ai_parsed, dict) and "error" not in ai_parsed:
                confidence = ai_parsed.get("confidence")
                if confidence and float(confidence) > 0.7:
                    # Replace the original command with the AI-structured version
                    old_cmd = cmd
                    cmd = ai_parsed.get("structured_command", cmd)
                    log.append(f"🧠 I understood that as: {cmd}")
    except Exception as e:
        logging.error(f"Error in AI command parsing: {str(e)}")
        # Continue with standard parsing if AI fails
    
    # Handle calendar events: "add X at Y"
    if cmd.startswith("add ") and " at " in cmd:
        # Extract event details
        title, time_str = cmd[4:].split(" at ", 1)
        title = title.strip().title()
        
        # Simple datetime parsing (could be enhanced with dateparser library)
        try:
            # For now, we'll use a simple approach
            now = datetime.datetime.now()
            
            # Handle "tomorrow", "next week", etc.
            if "tomorrow" in time_str:
                start_date = now.date() + datetime.timedelta(days=1)
                time_str = time_str.replace("tomorrow", "").strip()
            else:
                start_date = now.date()
                
            # Parse time
            if ":" in time_str:
                try:
                    hour, minute = map(int, time_str.split(":", 1))
                except (ValueError, TypeError):
                    # Default to noon if we can't parse the time
                    hour, minute = 12, 0
            else:
                time_match = re.search(r'\d+', time_str)
                if time_match:
                    try:
                        hour = int(time_match.group())
                        minute = 0
                    except (ValueError, TypeError):
                        # Default to noon if we can't parse the time
                        hour, minute = 12, 0
                else:
                    # Default to noon if no time found
                    hour, minute = 12, 0
                
            # Handle am/pm
            if "pm" in time_str.lower() and hour < 12:
                hour += 12
            elif "am" in time_str.lower() and hour == 12:
                hour = 0
                
            start_time = datetime.datetime.combine(
                start_date, 
                datetime.time(hour, minute)
            )
            end_time = start_time + datetime.timedelta(hours=1)
            
            # Create the event
            event = {
                "summary": title,
                "start": {"dateTime": start_time.isoformat()},
                "end": {"dateTime": end_time.isoformat()}
            }
            
            calendar.events().insert(calendarId="primary", body=event).execute()
            log.append(f"🗓️ Event '{title}' created.")
        except Exception as e:
            logging.error(f"Error creating event: {str(e)}")
            log.append(f"❌ Error creating event: {str(e)}")
    
    # Handle workout logging
    elif cmd.startswith("log workout"):
        entry = cmd.replace("log workout", "").strip()
        if entry.startswith(":"):
            entry = entry[1:].strip()
        
        if not entry:
            log.append("❌ Please provide workout details.")
        else:
            log_workout(entry)
            log.append("💪 Workout logged.")
            
    # Handle mood logging
    elif cmd.startswith("log mood"):
        entry = cmd.replace("log mood", "").strip()
        if entry.startswith(":"):
            entry = entry[1:].strip()
            
        if not entry:
            log.append("❌ Please provide mood details.")
        else:
            log_mood(entry)
            log.append("😊 Mood logged.")
            
    # Calendar query
    elif cmd.startswith("what's my day") or cmd.startswith("whats my day"):
        try:
            now = datetime.date.today()
            time_min = f"{now.isoformat()}T00:00:00Z"
            time_max = f"{now.isoformat()}T23:59:59Z"
            
            events_result = calendar.events().list(
                calendarId="primary", 
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            
            if not events:
                log.append("📆 No events scheduled for today.")
            else:
                log.append("📆 Today's schedule:")
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    # Format the time for better readability
                    if "T" in start:
                        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        time_str = start_dt.strftime("%I:%M %p")
                    else:
                        time_str = "All day"
                    log.append(f"- {event['summary']} @ {time_str}")
        except Exception as e:
            logging.error(f"Error fetching calendar: {str(e)}")
            log.append(f"❌ Error fetching calendar: {str(e)}")
            
    # AA Reflection
    elif "aa reflection" in cmd or "daily reflection" in cmd:
        reflection = scrape_aa_reflection()
        log.append(reflection)
        
    # Google Tasks
    elif cmd.startswith("add task"):
        title = cmd.replace("add task", "").strip()
        if title.startswith(":"):
            title = title[1:].strip()
            
        if not title:
            log.append("❌ Please provide a task title.")
        else:
            try:
                task = {"title": title}
                tasks.tasks().insert(tasklist="@default", body=task).execute()
                log.append(f"✅ Task added: {title}")
            except Exception as e:
                logging.error(f"Error adding task: {str(e)}")
                log.append(f"❌ Error adding task: {str(e)}")
                
    # Google Keep
    elif cmd.startswith("add note"):
        note_text = cmd.replace("add note", "").strip()
        if note_text.startswith(":"):
            note_text = note_text[1:].strip()
            
        if not note_text:
            log.append("❌ Please provide note content.")
        else:
            try:
                gnote = keep.createNote("Quick Note", note_text)
                keep.sync()
                log.append(f"📝 Note added: {note_text[:30]}...")
            except Exception as e:
                logging.error(f"Error adding note: {str(e)}")
                log.append(f"❌ Error adding note: {str(e)}")
                
    # Spotify commands
    elif cmd.startswith("play ") and spotify:
        query = cmd[5:].strip()
        if not query:
            log.append("❌ Please specify what to play.")
        else:
            try:
                # Check if devices are available
                devices = spotify.devices()
                if not devices or not devices.get('devices'):
                    log.append("⚠️ No active Spotify devices found. Please open Spotify on a device first.")
                else:
                    # Search for the track
                    results = spotify.search(q=query, type='track', limit=1)
                    if not results['tracks']['items']:
                        log.append(f"❌ No tracks found for '{query}'")
                    else:
                        track = results['tracks']['items'][0]
                        spotify.start_playback(uris=[track['uri']])
                        log.append(f"▶️ Playing '{track['name']}' by {track['artists'][0]['name']}")
            except Exception as e:
                logging.error(f"Error playing music: {str(e)}")
                log.append(f"❌ Error playing music: {str(e)}")
                
    # Auth commands
    elif cmd == "connect spotify":
        result["redirect"] = url_for("authorize_spotify")
        log.append("🔄 Redirecting to Spotify authorization...")
        
    elif cmd == "connect google":
        result["redirect"] = url_for("authorize_google")
        log.append("🔄 Redirecting to Google authorization...")
        
    # Help command
    elif cmd == "help":
        log.append("🔍 Available commands:")
        log.append("- add [event] at [time] - Create a calendar event")
        log.append("- what's my day - Show today's calendar events")
        log.append("- log workout: [details] - Log workout details")
        log.append("- log mood: [mood] [details] - Log your mood")
        log.append("- show aa reflection - Display AA daily reflection")
        log.append("- play [song/artist] - Play music on Spotify")
        log.append("- add task: [task] - Add a task to Google Tasks")
        log.append("- add note: [note] - Add a note to Google Keep")
        log.append("- weekly summary - Get an AI summary of your week")
        log.append("- motivate me - Get a motivational quote")
        log.append("- add doctor [name] - Add a new doctor to your list")
        log.append("- list doctors - Show your saved doctors")
        log.append("- set appointment with [doctor] on [date/time] - Schedule an appointment")
        log.append("- show appointments - List your upcoming appointments")
        log.append("")
        log.append("📋 Shopping Lists:")
        log.append("- create list [name] - Create a new shopping list")
        log.append("- add [item] to [list name] - Add an item to a shopping list")
        log.append("- show lists - Display all your shopping lists")
        log.append("- show items in [list name] - Show items in a specific list")
        log.append("- mark list [name] as ordered - Mark a list as ordered")
        log.append("")
        log.append("💊 Medications:")
        log.append("- add medication [name] - Add a medication to track")
        log.append("- refill [medication] with [quantity] - Record a medication refill")
        log.append("- show medications - List all your tracked medications")
        log.append("- show medications to refill - Show medications that need refills")
        log.append("")
        log.append("🛒 Products:")
        log.append("- track product [name] [url] - Add a product to track")
        log.append("- set product [name] as recurring every [days] days - Set up recurring orders")
        log.append("- order product [name] - Mark a product as ordered")
        log.append("- show products - List all your tracked products")
        log.append("- show products to order - Show products due for ordering")
        log.append("")
        log.append("- connect spotify - Connect Spotify account")
        log.append("- connect google - Connect Google account")
        log.append("- help - Show this help menu")
        log.append("- clear - Clear the command log")
        log.append("")
        log.append("💡 You can also type commands in natural language! For example:")
        log.append("  \"I need to see the dentist next Friday at 2pm\"")
        log.append("  \"What does my schedule look like today?\"")
        log.append("  \"I went for a 5k run this morning\"")
        log.append("  \"Add Dr. Smith as my dentist\"")
        log.append("  \"When is my next doctor's appointment?\"")
        
    # Weekly summary
    elif "weekly summary" in cmd.lower():
        try:
            from utils.ai_helper import generate_weekly_summary
            from utils.logger import get_workout_entries, get_mood_entries
            
            # Get calendar events for the week
            now = datetime.datetime.now()
            start_of_week = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_week = start_of_week + datetime.timedelta(days=7)
            
            events_result = calendar.events().list(
                calendarId="primary", 
                timeMin=start_of_week.isoformat() + "Z",
                timeMax=end_of_week.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            # Get recent tasks
            tasks_result = tasks.tasks().list(tasklist="@default", maxResults=10).execute()
            
            # Get workout and mood logs
            workout_entries = get_workout_entries(limit=7)
            mood_entries = get_mood_entries(limit=7)
            
            # Generate summary
            summary = generate_weekly_summary(
                events_result.get("items", []),
                tasks_result.get("items", []),
                workout_entries,
                mood_entries
            )
            
            log.append("📊 Your Weekly Summary")
            log.append(summary)
            
        except Exception as e:
            logging.error(f"Error generating weekly summary: {str(e)}")
            log.append(f"❌ Error generating weekly summary: {str(e)}")
    
    # Motivational quote
    elif "motivate" in cmd.lower() or "quote" in cmd.lower():
        try:
            from utils.ai_helper import get_motivation_quote
            theme = None
            
            # Extract theme if provided
            if "about" in cmd.lower():
                theme = cmd.lower().split("about", 1)[1].strip()
            
            quote = get_motivation_quote(theme)
            log.append(f"✨ {quote}")
            
        except Exception as e:
            logging.error(f"Error generating motivational quote: {str(e)}")
            log.append(f"❌ Error generating quote: {str(e)}")
    
    # Add doctor command
    elif cmd.startswith("add doctor"):
        try:
            # Extract doctor name
            doctor_name = cmd.replace("add doctor", "", 1).strip()
            if not doctor_name:
                log.append("❌ Please provide a doctor name.")
                return result
                
            # Check if doctor already exists
            existing_doctor = get_doctor_by_name(doctor_name, session)
            if existing_doctor:
                log.append(f"ℹ️ Doctor '{doctor_name}' is already in your list.")
                return result
                
            # Add the doctor
            doctor = add_doctor(name=doctor_name, session=session)
            if doctor:
                log.append(f"✅ Added doctor: {doctor_name}")
                log.append("You can add more details later using the web interface.")
            else:
                log.append(f"❌ Error adding doctor: {doctor_name}")
        except Exception as e:
            logging.error(f"Error adding doctor: {str(e)}")
            log.append(f"❌ Error adding doctor: {str(e)}")
    
    # List doctors command
    elif cmd == "list doctors" or "show doctors" in cmd or "my doctors" in cmd:
        try:
            doctors = get_doctors(session)
            if not doctors:
                log.append("ℹ️ You don't have any doctors saved yet.")
                log.append("Use 'add doctor [name]' to add one.")
            else:
                log.append("👨‍⚕️ Your Doctors:")
                for doctor in doctors:
                    specialty = f" ({doctor.specialty})" if doctor.specialty else ""
                    log.append(f"- {doctor.name}{specialty}")
        except Exception as e:
            logging.error(f"Error listing doctors: {str(e)}")
            log.append(f"❌ Error listing doctors: {str(e)}")
    
    # Set appointment command
    elif cmd.startswith("set appointment") or "schedule" in cmd and "appointment" in cmd:
        try:
            # First, check if we have a doctor name
            doctor_name = None
            appointment_date = None
            
            # Try to extract doctor name
            if "with" in cmd:
                parts = cmd.split("with", 1)
                if len(parts) > 1 and "on" in parts[1]:
                    doctor_part, date_part = parts[1].split("on", 1)
                    doctor_name = doctor_part.strip()
                    date_str = date_part.strip()
                elif len(parts) > 1:
                    doctor_name = parts[1].strip()
            
            if not doctor_name:
                log.append("❌ Please specify a doctor name using 'with [doctor name]'.")
                return result
                
            # Find the doctor
            doctor = get_doctor_by_name(doctor_name, session)
            if not doctor:
                log.append(f"❌ Doctor '{doctor_name}' not found in your list.")
                log.append("Use 'add doctor [name]' to add them first.")
                return result
                
            # Parse the date/time
            now = datetime.datetime.now()
            appointment_date = now + datetime.timedelta(days=7)  # Default to a week from now
            
            if "tomorrow" in cmd:
                appointment_date = now + datetime.timedelta(days=1)
            elif "today" in cmd:
                appointment_date = now
            elif "next week" in cmd:
                appointment_date = now + datetime.timedelta(days=7)
            
            # Try to extract time if specified
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', cmd, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                am_pm = time_match.group(3).lower() if time_match.group(3) else None
                
                if am_pm == 'pm' and hour < 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                    
                appointment_date = appointment_date.replace(hour=hour, minute=minute)
            
            # Add the appointment
            appointment = add_appointment(
                doctor_id=doctor.id,
                date=appointment_date,
                reason="Regular checkup",  # Default reason
                session=session
            )
            
            if appointment:
                # Format date for display
                formatted_date = appointment_date.strftime("%A, %B %d at %I:%M %p")
                log.append(f"🗓️ Appointment scheduled with Dr. {doctor.name} on {formatted_date}")
                
                # If Google Calendar is connected, add it there too
                if calendar:
                    end_time = appointment_date + datetime.timedelta(hours=1)
                    event = {
                        "summary": f"Doctor Appointment: {doctor.name}",
                        "location": doctor.address if doctor.address else "",
                        "description": "Created via NOUS Assistant",
                        "start": {"dateTime": appointment_date.isoformat()},
                        "end": {"dateTime": end_time.isoformat()},
                        "reminders": {
                            "useDefault": False,
                            "overrides": [
                                {"method": "popup", "minutes": 60},
                                {"method": "popup", "minutes": 24 * 60}  # Day before
                            ]
                        }
                    }
                    calendar.events().insert(calendarId="primary", body=event).execute()
                    log.append("📅 Added to your Google Calendar with reminders.")
            else:
                log.append(f"❌ Error scheduling appointment")
        except Exception as e:
            logging.error(f"Error scheduling appointment: {str(e)}")
            log.append(f"❌ Error scheduling appointment: {str(e)}")
    
    # Show appointments command
    elif cmd == "show appointments" or "my appointments" in cmd:
        try:
            appointments = get_upcoming_appointments(session)
            if not appointments:
                log.append("ℹ️ You don't have any upcoming appointments scheduled.")
            else:
                log.append("🗓️ Your Upcoming Appointments:")
                for appointment in appointments:
                    # Get doctor name
                    doctor = Doctor.query.get(appointment.doctor_id)
                    doctor_name = doctor.name if doctor else "Unknown Doctor"
                    
                    # Format date
                    formatted_date = appointment.date.strftime("%A, %B %d at %I:%M %p")
                    reason = f" for {appointment.reason}" if appointment.reason else ""
                    log.append(f"- {formatted_date}: Dr. {doctor_name}{reason}")
        except Exception as e:
            logging.error(f"Error showing appointments: {str(e)}")
            log.append(f"❌ Error showing appointments: {str(e)}")
            
    # Clear command
    elif cmd == "clear":
        log.clear()
        log.append("🧹 Log cleared.")
        
    # Logout command
    elif cmd == "logout":
        result["redirect"] = url_for("logout")
        
    # Unknown command
    else:
        log.append("❓ Command not recognized. Type 'help' for available commands.")
        
    return result
