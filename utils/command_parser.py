import datetime
import logging
from flask import url_for
import re
from utils.logger import log_workout, log_mood
from utils.scraper import scrape_aa_reflection

def parse_command(cmd, calendar, tasks, keep, spotify, log):
    """Parse and execute user commands"""
    result = {"redirect": None}
    
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
                hour, minute = map(int, time_str.split(":", 1))
            else:
                hour = int(re.search(r'\d+', time_str).group())
                minute = 0
                
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
        log.append("- connect spotify - Connect Spotify account")
        log.append("- connect google - Connect Google account")
        log.append("- help - Show this help menu")
        log.append("- clear - Clear the command log")
        
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
