import datetime
import logging
import re
from flask import url_for
from utils.logger import log_workout, log_mood
from utils.scraper import scrape_aa_reflection
from utils.ai_helper import parse_natural_language
from utils.google_helper import create_calendar_event

# Import doctor appointment helpers
from utils.doctor_appointment_helper import (
    get_doctors, get_doctor_by_name, add_doctor, 
    add_appointment, get_upcoming_appointments,
    get_due_appointment_reminders
)

# Import shopping list helpers
from utils.shopping_helper import (
    get_shopping_lists, get_shopping_list_by_name, create_shopping_list,
    add_item_to_list, get_items_in_list, toggle_item_checked,
    get_due_shopping_lists, mark_list_as_ordered
)

# Import medication helpers
from utils.medication_helper import (
    get_medications, get_medication_by_name, add_medication,
    update_medication_quantity, refill_medication, get_medications_to_refill
)

# Import product helpers
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
    
    # Doctor Command Handlers
    elif cmd.startswith("add doctor"):
        try:
            # Extract doctor name
            doctor_name = cmd.replace("add doctor", "", 1).strip()
            if not doctor_name:
                log.append("❌ Please provide a doctor name.")
                return True
                
            # Add the doctor
            doctor = add_doctor(name=doctor_name, session=session)
            
            if doctor:
                log.append(f"✅ Added Dr. {doctor_name} to your records.")
                log.append("You can add more details with commands like:")
                log.append(f"- 'set Dr. {doctor_name} specialty to [specialty]'")
                log.append(f"- 'set Dr. {doctor_name} phone to [phone]'")
            else:
                log.append("❌ Failed to add doctor. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error adding doctor: {str(e)}")
            return True
    
    elif cmd == "list doctors" or "show doctors" in cmd or "my doctors" in cmd:
        try:
            doctors = get_doctors(session)
            if not doctors:
                log.append("ℹ️ You don't have any doctors saved yet.")
                log.append("Use 'add doctor [name]' to add one.")
            else:
                log.append("🩺 Your doctors:")
                for doctor in doctors:
                    specialty = f" ({doctor.specialty})" if doctor.specialty else ""
                    log.append(f"- Dr. {doctor.name}{specialty}")
                    if doctor.phone:
                        log.append(f"  📞 Phone: {doctor.phone}")
                    if doctor.address:
                        log.append(f"  📍 Location: {doctor.address}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving doctors: {str(e)}")
            return True
    
    elif cmd.startswith("set appointment with "):
        try:
            # Extract doctor name and date
            parts = cmd[20:].split(" on ")
            if len(parts) != 2:
                log.append("❌ Invalid format. Use 'set appointment with [doctor] on [date/time]'")
                return True
                
            doctor_name = parts[0].strip()
            date_str = parts[1].strip()
            
            # Find the doctor
            doctor = get_doctor_by_name(doctor_name, session)
            if not doctor:
                log.append(f"❌ Doctor '{doctor_name}' not found.")
                log.append("Use 'list doctors' to see your saved doctors.")
                return True
                
            # Parse the date
            try:
                # Try to parse date in various formats
                date_formats = [
                    "%Y-%m-%d %H:%M",  # 2023-10-15 14:30
                    "%B %d at %I:%M %p",  # October 15 at 2:30 PM
                    "%B %d at %H:%M",  # October 15 at 14:30
                    "%B %d, %Y at %I:%M %p",  # October 15, 2023 at 2:30 PM
                    "%A, %B %d at %I:%M %p",  # Monday, October 15 at 2:30 PM
                    "%A %B %d at %I:%M %p",  # Monday October 15 at 2:30 PM
                    "%A at %I:%M %p",  # Monday at 2:30 PM
                    "next %A at %I:%M %p",  # next Monday at 2:30 PM
                ]
                
                appt_date = None
                for fmt in date_formats:
                    try:
                        appt_date = datetime.datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                        
                # Handle relative dates like "next Monday"
                if appt_date is None and "next" in date_str.lower():
                    today = datetime.datetime.now()
                    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                        if day in date_str.lower():
                            # Calculate days until next occurrence
                            day_idx = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(day)
                            days_ahead = day_idx - today.weekday()
                            if days_ahead <= 0:  # Target day already happened this week
                                days_ahead += 7
                            next_day = today + datetime.timedelta(days=days_ahead)
                            
                            # Try to extract time
                            time_match = re.search(r'at (\d{1,2}):?(\d{2})?\s?(am|pm)?', date_str.lower())
                            if time_match:
                                hour = int(time_match.group(1))
                                minute = int(time_match.group(2) or 0)
                                am_pm = time_match.group(3)
                                
                                # Adjust hour for PM
                                if am_pm == 'pm' and hour < 12:
                                    hour += 12
                                elif am_pm == 'am' and hour == 12:
                                    hour = 0
                                    
                                appt_date = next_day.replace(hour=hour, minute=minute)
                                break
                            
                if appt_date is None:
                    log.append(f"❌ Could not parse date: {date_str}")
                    log.append("Please use a format like 'October 15 at 2:30 PM' or 'next Monday at 2:30 PM'")
                    return True
                    
                # Add appointment
                appointment = add_appointment(doctor_id=doctor.id, date=appt_date, session=session)
                
                if appointment:
                    # Format date for display
                    formatted_date = appt_date.strftime("%A, %B %d at %I:%M %p")
                    log.append(f"✅ Appointment scheduled with Dr. {doctor.name} on {formatted_date}")
                    
                    # If Google Calendar is connected, create event
                    if calendar:
                        try:
                            # Create a 1-hour appointment by default
                            end_time = appt_date + datetime.timedelta(hours=1)
                            event = create_calendar_event(
                                calendar, 
                                f"Appointment with Dr. {doctor.name}",
                                appt_date,
                                end_time,
                                f"Medical appointment with Dr. {doctor.name} ({doctor.specialty or 'No specialty'})"
                            )
                            log.append("📅 Added to your Google Calendar")
                        except Exception as e:
                            log.append(f"⚠️ Could not add to Google Calendar: {str(e)}")
                else:
                    log.append("❌ Failed to schedule appointment. Please try again.")
                    
            except Exception as e:
                log.append(f"❌ Error scheduling appointment: {str(e)}")
                
            return True
            
        except Exception as e:
            log.append(f"❌ Error setting appointment: {str(e)}")
            return True
    
    elif cmd == "show appointments" or "my appointments" in cmd:
        try:
            appointments = get_upcoming_appointments(session)
            if not appointments:
                log.append("ℹ️ You don't have any upcoming appointments scheduled.")
                log.append("Use 'set appointment with [doctor] on [date/time]' to schedule one.")
                
                # Check for appointment reminders
                reminders = get_due_appointment_reminders(session)
                if reminders:
                    log.append("\n⏰ Reminder: It's time for these regular check-ups:")
                    for reminder in reminders:
                        doctor = Doctor.query.get(reminder.doctor_id)
                        doctor_name = doctor.name if doctor else "Unknown Doctor"
                        log.append(f"- Dr. {doctor_name} (due since {reminder.next_reminder.strftime('%B %d')})")
            else:
                log.append("📅 Your upcoming appointments:")
                for appointment in appointments:
                    # Format the date
                    formatted_date = appointment.date.strftime("%A, %B %d at %I:%M %p")
                    
                    # Get doctor name
                    doctor = Doctor.query.get(appointment.doctor_id)
                    doctor_name = doctor.name if doctor else "Unknown Doctor"
                    
                    # Get reason if available
                    reason = f" ({appointment.reason})" if appointment.reason else ""
                    
                    log.append(f"- {formatted_date}: Dr. {doctor_name}{reason}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving appointments: {str(e)}")
            return True
            
    # Shopping List Command Handlers
    elif cmd.startswith("create list "):
        try:
            list_name = cmd[12:].strip()
            if not list_name:
                log.append("❌ Please provide a name for the shopping list.")
                return True
                
            shopping_list = create_shopping_list(name=list_name, session=session)
            if shopping_list:
                log.append(f"✅ Created shopping list: {list_name}")
                log.append(f"Use 'add [item] to {list_name}' to add items to this list.")
            else:
                log.append("❌ Failed to create shopping list. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error creating shopping list: {str(e)}")
            return True
            
    elif "add " in cmd.lower() and " to " in cmd.lower():
        try:
            # Parse "add [item] to [list name]"
            parts = cmd.split(" to ", 1)
            if len(parts) == 2 and parts[0].lower().startswith("add "):
                item_name = parts[0][4:].strip()
                list_name = parts[1].strip()
                
                # Find the shopping list
                shopping_list = get_shopping_list_by_name(list_name, session)
                if not shopping_list:
                    log.append(f"❌ Shopping list '{list_name}' not found.")
                    log.append("Use 'show lists' to see your available lists.")
                    return True
                    
                # Add the item
                item = add_item_to_list(shopping_list.id, item_name, session=session)
                if item:
                    log.append(f"✅ Added '{item_name}' to your '{shopping_list.name}' list")
                else:
                    log.append(f"❌ Failed to add item to list. Please try again.")
                return True
        except Exception as e:
            pass  # Not a shopping list command, continue to next checks
    
    elif cmd == "show lists" or cmd == "show shopping lists" or "my lists" in cmd:
        try:
            shopping_lists = get_shopping_lists(session)
            if not shopping_lists:
                log.append("ℹ️ You don't have any shopping lists yet.")
                log.append("Use 'create list [name]' to create one.")
            else:
                log.append("📋 Your shopping lists:")
                for lst in shopping_lists:
                    items_count = len(lst.items) if lst.items else 0
                    log.append(f"- {lst.name} ({items_count} items)")
                    if lst.store:
                        log.append(f"  📍 Store: {lst.store}")
                    if lst.is_recurring:
                        next_date = lst.next_order_date.strftime("%B %d") if lst.next_order_date else "not scheduled"
                        log.append(f"  ↻ Recurring every {lst.frequency_days} days (Next: {next_date})")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving shopping lists: {str(e)}")
            return True
            
    elif cmd.startswith("show items in "):
        try:
            list_name = cmd[14:].strip()
            if not list_name:
                log.append("❌ Please specify which list to show items from.")
                return True
                
            # Find the shopping list
            shopping_list = get_shopping_list_by_name(list_name, session)
            if not shopping_list:
                log.append(f"❌ Shopping list '{list_name}' not found.")
                log.append("Use 'show lists' to see your available lists.")
                return True
                
            # Get items in the list
            items = get_items_in_list(shopping_list.id, session)
            if not items:
                log.append(f"ℹ️ Your '{shopping_list.name}' list is empty.")
                log.append(f"Use 'add [item] to {shopping_list.name}' to add items.")
            else:
                log.append(f"📋 Items in '{shopping_list.name}':")
                
                # Group items by category
                categories = {}
                uncategorized = []
                for item in items:
                    if item.category:
                        if item.category not in categories:
                            categories[item.category] = []
                        categories[item.category].append(item)
                    else:
                        uncategorized.append(item)
                
                # Display categorized items
                for category, cat_items in categories.items():
                    log.append(f"\n{category}:")
                    for item in cat_items:
                        check = "☑️" if item.is_checked else "☐"
                        quantity_str = f"{item.quantity} {item.unit}" if item.unit else f"{item.quantity}"
                        log.append(f"- {check} {item.name} ({quantity_str})")
                
                # Display uncategorized items
                if uncategorized:
                    log.append("\nOther Items:")
                    for item in uncategorized:
                        check = "☑️" if item.is_checked else "☐"
                        quantity_str = f"{item.quantity} {item.unit}" if item.unit else f"{item.quantity}"
                        log.append(f"- {check} {item.name} ({quantity_str})")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving shopping list items: {str(e)}")
            return True
            
    elif cmd.startswith("mark list ") and " as ordered" in cmd.lower():
        try:
            # Parse "mark list [name] as ordered"
            parts = cmd.lower().split(" as ordered", 1)[0]
            if parts.startswith("mark list "):
                list_name = parts[10:].strip()
                
                # Find the shopping list
                shopping_list = get_shopping_list_by_name(list_name, session)
                if not shopping_list:
                    log.append(f"❌ Shopping list '{list_name}' not found.")
                    log.append("Use 'show lists' to see your available lists.")
                    return True
                    
                # Mark as ordered
                updated_list = mark_list_as_ordered(shopping_list.id, session)
                if updated_list:
                    log.append(f"✅ Marked '{shopping_list.name}' as ordered")
                    if updated_list.is_recurring:
                        next_date = updated_list.next_order_date.strftime("%B %d") if updated_list.next_order_date else "not scheduled"
                        log.append(f"Next order scheduled for: {next_date}")
                else:
                    log.append(f"❌ Failed to update list. Please try again.")
                return True
                
        except Exception as e:
            log.append(f"❌ Error marking list as ordered: {str(e)}")
            return True
    
    # Medication Command Handlers
    elif cmd.startswith("add medication "):
        try:
            med_name = cmd[15:].strip()
            if not med_name:
                log.append("❌ Please provide a name for the medication.")
                return True
                
            medication = add_medication(name=med_name, session=session)
            if medication:
                log.append(f"✅ Added medication: {med_name}")
                log.append("You can add more details with these commands:")
                log.append(f"- 'set {med_name} dosage to [amount]'")
                log.append(f"- 'set {med_name} refills to [number]'")
                log.append(f"- 'set {med_name} quantity to [number]'")
            else:
                log.append("❌ Failed to add medication. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error adding medication: {str(e)}")
            return True
            
    elif cmd.startswith("refill ") and " with " in cmd.lower():
        try:
            # Parse "refill [medication] with [quantity]"
            parts = cmd.split(" with ", 1)
            if len(parts) == 2 and parts[0].lower().startswith("refill "):
                med_name = parts[0][7:].strip()
                quantity_str = parts[1].strip()
                
                # Find the medication
                medication = get_medication_by_name(med_name, session)
                if not medication:
                    log.append(f"❌ Medication '{med_name}' not found.")
                    log.append("Use 'show medications' to see your tracked medications.")
                    return True
                    
                try:
                    quantity = int(quantity_str)
                    
                    # Record the refill
                    updated_med = refill_medication(medication.id, quantity, session=session)
                    if updated_med:
                        log.append(f"✅ Refilled '{medication.name}' with {quantity} units")
                        log.append(f"New quantity: {updated_med.quantity_remaining}")
                        if updated_med.refills_remaining is not None:
                            log.append(f"Refills remaining: {updated_med.refills_remaining}")
                    else:
                        log.append(f"❌ Failed to refill medication. Please try again.")
                except ValueError:
                    log.append(f"❌ Invalid quantity: {quantity_str}. Please enter a number.")
                    
                return True
                
        except Exception as e:
            log.append(f"❌ Error refilling medication: {str(e)}")
            return True
            
    elif cmd == "show medications" or "my medications" in cmd or "my meds" in cmd:
        try:
            medications = get_medications(session)
            if not medications:
                log.append("ℹ️ You don't have any medications tracked yet.")
                log.append("Use 'add medication [name]' to add one.")
            else:
                log.append("💊 Your medications:")
                for med in medications:
                    log.append(f"- {med.name}")
                    if med.dosage:
                        log.append(f"  Dosage: {med.dosage}")
                    if med.instructions:
                        log.append(f"  Instructions: {med.instructions}")
                    if med.quantity_remaining is not None:
                        log.append(f"  Quantity remaining: {med.quantity_remaining}")
                    if med.refills_remaining is not None:
                        log.append(f"  Refills remaining: {med.refills_remaining}")
                    if med.pharmacy:
                        log.append(f"  Pharmacy: {med.pharmacy}")
                    doctor = Doctor.query.get(med.doctor_id) if med.doctor_id else None
                    if doctor:
                        log.append(f"  Prescribed by: Dr. {doctor.name}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving medications: {str(e)}")
            return True
            
    elif cmd == "show medications to refill" or "meds to refill" in cmd:
        try:
            medications = get_medications_to_refill(session)
            if not medications:
                log.append("✅ No medications need to be refilled soon.")
            else:
                log.append("⚠️ Medications to refill soon:")
                for med in medications:
                    log.append(f"- {med.name}")
                    if med.quantity_remaining is not None:
                        log.append(f"  Quantity remaining: {med.quantity_remaining}")
                    if med.refills_remaining is not None:
                        log.append(f"  Refills remaining: {med.refills_remaining}")
                    if med.pharmacy:
                        log.append(f"  Pharmacy: {med.pharmacy}")
                    if med.pharmacy_phone:
                        log.append(f"  Pharmacy phone: {med.pharmacy_phone}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error checking medications to refill: {str(e)}")
            return True
    
    # Product Command Handlers  
    elif cmd.startswith("track product "):
        try:
            # Parse "track product [name] [url]"
            product_info = cmd[14:].strip()
            parts = product_info.split(" ", 1)
            
            if len(parts) < 2:
                log.append("❌ Please provide both a product name and URL.")
                log.append("Format: track product [name] [url]")
                return True
                
            product_name = parts[0]
            product_url = parts[1]
            
            product = add_product(name=product_name, url=product_url, session=session)
            if product:
                log.append(f"✅ Added product: {product_name}")
                if product.source:
                    log.append(f"Source: {product.source}")
                if product.price:
                    log.append(f"Price: ${product.price:.2f}")
            else:
                log.append("❌ Failed to add product. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error tracking product: {str(e)}")
            return True
            
    elif cmd.startswith("set product ") and " as recurring every " in cmd.lower():
        try:
            # Parse "set product [name] as recurring every [days] days"
            product_parts = cmd.lower().split(" as recurring every ", 1)
            if len(product_parts) == 2 and product_parts[0].startswith("set product "):
                product_name = product_parts[0][12:].strip()
                frequency_parts = product_parts[1].split(" days", 1)
                
                # Find the product
                product = get_product_by_name(product_name, session)
                if not product:
                    log.append(f"❌ Product '{product_name}' not found.")
                    log.append("Use 'show products' to see your tracked products.")
                    return True
                    
                try:
                    frequency_days = int(frequency_parts[0].strip())
                    
                    # Set as recurring
                    updated_product = set_product_as_recurring(product.id, frequency_days, session)
                    if updated_product:
                        next_date = updated_product.next_order_date.strftime("%B %d") if updated_product.next_order_date else "not scheduled"
                        log.append(f"✅ Set '{product.name}' to reorder every {frequency_days} days")
                        log.append(f"Next order scheduled for: {next_date}")
                    else:
                        log.append(f"❌ Failed to update product. Please try again.")
                except ValueError:
                    log.append(f"❌ Invalid number of days. Please enter a number.")
                    
                return True
                
        except Exception as e:
            log.append(f"❌ Error setting product as recurring: {str(e)}")
            return True
            
    elif cmd.startswith("order product "):
        try:
            product_name = cmd[14:].strip()
            if not product_name:
                log.append("❌ Please specify which product you ordered.")
                return True
                
            # Find the product
            product = get_product_by_name(product_name, session)
            if not product:
                log.append(f"❌ Product '{product_name}' not found.")
                log.append("Use 'show products' to see your tracked products.")
                return True
                
            # Mark as ordered
            updated_product = mark_product_as_ordered(product.id, session)
            if updated_product:
                log.append(f"✅ Marked '{product.name}' as ordered")
                if updated_product.is_recurring:
                    next_date = updated_product.next_order_date.strftime("%B %d") if updated_product.next_order_date else "not scheduled"
                    log.append(f"Next order scheduled for: {next_date}")
            else:
                log.append(f"❌ Failed to update product. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error marking product as ordered: {str(e)}")
            return True
            
    elif cmd == "show products" or "my products" in cmd:
        try:
            products = get_products(session)
            if not products:
                log.append("ℹ️ You don't have any products tracked yet.")
                log.append("Use 'track product [name] [url]' to add one.")
            else:
                log.append("🛒 Your tracked products:")
                for product in products:
                    log.append(f"- {product.name}")
                    if product.source:
                        log.append(f"  Source: {product.source}")
                    if product.price:
                        log.append(f"  Price: ${product.price:.2f}")
                    if product.is_recurring:
                        next_date = product.next_order_date.strftime("%B %d") if product.next_order_date else "not scheduled"
                        log.append(f"  ↻ Recurring every {product.frequency_days} days (Next: {next_date})")
                    if product.url:
                        log.append(f"  URL: {product.url}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving products: {str(e)}")
            return True
            
    elif cmd == "show products to order" or "products due" in cmd:
        try:
            products = get_due_product_orders(session)
            if not products:
                log.append("✅ No products are currently due for ordering.")
            else:
                log.append("🔔 Products due for ordering:")
                for product in products:
                    log.append(f"- {product.name}")
                    if product.source:
                        log.append(f"  Source: {product.source}")
                    if product.price:
                        log.append(f"  Price: ${product.price:.2f}")
                    if product.url:
                        log.append(f"  URL: {product.url}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error checking products to order: {str(e)}")
            return True
    
    # General command handling
    elif cmd == "clear":
        log.clear()
        log.append("Command log cleared.")
    
    elif cmd == "logout":
        log.append("🔄 Logging out and clearing credentials...")
        result["redirect"] = url_for("logout")
    
    else:
        # Try to use AI to parse the command as a last resort
        try:
            # If we already tried AI parsing above, no need to try again
            if "I understood that as:" not in '\n'.join(log):
                ai_parsed = parse_natural_language(cmd)
                
                if ai_parsed and isinstance(ai_parsed, dict) and "error" not in ai_parsed:
                    confidence = ai_parsed.get("confidence", 0)
                    
                    if float(confidence) > 0.5:
                        log.append(f"🧠 I think you're trying to: {ai_parsed.get('intent', 'do something')}")
                        log.append(f"Try using one of these commands:")
                        
                        for suggestion in ai_parsed.get("suggestions", []):
                            log.append(f"- {suggestion}")
                    else:
                        log.append("I'm not sure what you're asking. Type 'help' to see available commands.")
                else:
                    log.append("I'm not sure what you're asking. Type 'help' to see available commands.")
        except Exception as e:
            logging.error(f"Error in fallback AI parsing: {str(e)}")
            log.append("I don't understand that command. Type 'help' to see available commands.")
    
    return result