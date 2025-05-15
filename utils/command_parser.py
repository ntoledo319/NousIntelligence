import datetime
import logging
import re
from flask import url_for
from utils.logger import log_workout, log_mood
from utils.scraper import scrape_aa_reflection
from utils.ai_helper import parse_natural_language, handle_conversation, analyze_gmail_content, analyze_gmail_threads
from utils.google_helper import create_calendar_event
from utils.gmail_helper import get_gmail_service, get_gmail_messages, get_message_content, get_gmail_threads, search_gmail
from utils.google_api_manager import GoogleApiManager
from utils.weather_helper import (
    get_current_weather, get_weather_forecast, get_location_coordinates,
    format_weather_output, format_forecast_output, get_pressure_trend,
    calculate_pain_flare_risk, get_storm_severity, format_pain_forecast_output
)
# Import DBT helper functions
from utils.dbt_helper import (
    skills_on_demand, generate_diary_card, validate_experience, 
    distress_tolerance, chain_analysis, wise_mind, radical_acceptance,
    interpersonal_effectiveness, dialectic_generator, trigger_map,
    skill_of_the_day, edit_message, advise, log_dbt_skill,
    get_skill_logs, create_diary_card, get_diary_cards,
    analyze_skill_effectiveness, get_skill_recommendations
)

# Import DBT challenges functions
from utils.dbt_helper import (
    get_available_challenges, create_challenge, update_challenge_progress,
    mark_challenge_completed, reset_challenge, generate_personalized_challenge
)

# Import crisis management functions
from utils.dbt_crisis_helper import (
    get_crisis_resources, add_crisis_resource, update_crisis_resource,
    delete_crisis_resource, generate_crisis_plan, get_grounding_exercise,
    get_crisis_de_escalation
)

# Import emotion regulation functions
from utils.dbt_emotion_helper import (
    log_emotion, get_emotion_history, get_emotion_stats, generate_emotion_insights,
    get_opposite_action_suggestion, identify_emotion, check_emotion_vulnerability
)

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

# Import budget helpers
from utils.budget_helper import (
    get_budgets, get_budget_by_name, create_budget, get_budget_summary,
    get_expenses, add_expense, get_recurring_payments, get_upcoming_payments,
    mark_payment_paid, ExpenseCategory
)

# Import travel helpers
from utils.travel_helper import (
    get_trips, get_trip_by_name, create_trip, get_upcoming_trips, get_active_trip,
    get_itinerary, add_itinerary_item, get_accommodations, add_accommodation,
    get_travel_documents, add_travel_document, get_packing_list, add_packing_item,
    toggle_packed_status, generate_standard_packing_list, get_packing_progress
)

from models import (
    Doctor, ShoppingList, ShoppingItem, Medication, Product,
    Budget, Expense, RecurringPayment, Trip, ItineraryItem, 
    Accommodation, TravelDocument, PackingItem
)

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
           cmd.startswith("play ") or cmd.startswith("chat:") or \
           cmd.startswith("analyze email:"):
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
        # Check for specific types of playback commands
        if cmd.startswith("play artist "):
            # Play an artist's top tracks
            artist_name = cmd[12:].strip()
            if not artist_name:
                log.append("❌ Please specify an artist to play.")
            else:
                from utils.spotify_helper import play_artist
                log.append(play_artist(spotify, artist_name))
                
        elif cmd.startswith("play album "):
            # Play an album
            album_name = cmd[11:].strip()
            if not album_name:
                log.append("❌ Please specify an album to play.")
            else:
                from utils.spotify_helper import play_album
                log.append(play_album(spotify, album_name))
                
        elif cmd.startswith("play playlist "):
            # Play a playlist
            playlist_name = cmd[14:].strip()
            if not playlist_name:
                log.append("❌ Please specify a playlist to play.")
            else:
                from utils.spotify_helper import play_playlist
                log.append(play_playlist(spotify, playlist_name))
                
        else:
            # Default: play a track
            query = cmd[5:].strip()
            if not query:
                log.append("❌ Please specify what to play.")
            else:
                from utils.spotify_helper import play_track
                log.append(play_track(spotify, query))
    
    # Spotify playback control commands
    elif cmd == "pause" and spotify:
        from utils.spotify_helper import pause_playback
        log.append(pause_playback(spotify))
        
    elif cmd in ["resume", "continue"] and spotify:
        from utils.spotify_helper import resume_playback
        log.append(resume_playback(spotify))
        
    elif cmd in ["next", "skip"] and spotify:
        from utils.spotify_helper import skip_track
        log.append(skip_track(spotify))
        
    elif cmd in ["previous", "prev", "back"] and spotify:
        from utils.spotify_helper import previous_track
        log.append(previous_track(spotify))
        
    elif cmd.startswith("volume ") and spotify:
        try:
            vol = int(cmd[7:].strip())
            from utils.spotify_helper import set_volume
            log.append(set_volume(spotify, vol))
        except ValueError:
            log.append("❌ Please specify a volume level between 0 and 100.")
            
    elif cmd == "shuffle" and spotify:
        from utils.spotify_helper import toggle_shuffle
        log.append(toggle_shuffle(spotify))
        
    elif cmd == "repeat" and spotify:
        from utils.spotify_helper import toggle_repeat
        log.append(toggle_repeat(spotify))
        
    elif cmd in ["now playing", "current song", "what's playing"] and spotify:
        from utils.spotify_helper import get_currently_playing
        log.append(get_currently_playing(spotify))
    
    # Spotify playlist management
    elif cmd.startswith("create playlist ") and spotify:
        parts = cmd[16:].strip().split(" - ", 1)
        playlist_name = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else None
        
        if not playlist_name:
            log.append("❌ Please specify a name for the playlist.")
        else:
            from utils.spotify_helper import create_playlist
            log.append(create_playlist(spotify, playlist_name, description=description))
            
    elif cmd.startswith("add to playlist ") and spotify:
        # Format: add to playlist <playlist_name> - <track_name>
        parts = cmd[16:].strip().split(" - ", 1)
        if len(parts) < 2:
            log.append("❌ Please use format: add to playlist <playlist_name> - <track_name>")
        else:
            playlist_name = parts[0].strip()
            track_query = parts[1].strip()
            
            if not playlist_name or not track_query:
                log.append("❌ Please specify both playlist name and track to add.")
            else:
                from utils.spotify_helper import search_and_add_to_playlist
                log.append(search_and_add_to_playlist(spotify, playlist_name, track_query))
                
    elif cmd.startswith("recommend ") and spotify:
        query = cmd[10:].strip()
        if not query:
            log.append("❌ Please specify what kind of music you'd like recommended.")
        else:
            from utils.spotify_helper import get_recommendations
            # Use the search term as a seed track
            results = spotify.search(q=query, type='track,artist', limit=1)
            seed_tracks = []
            seed_artists = []
            
            if results['tracks']['items']:
                seed_tracks.append(results['tracks']['items'][0]['id'])
            if results['artists']['items']:
                seed_artists.append(results['artists']['items'][0]['id'])
                
            if not seed_tracks and not seed_artists:
                log.append(f"❌ No tracks or artists found for '{query}'")
            else:
                log.append(get_recommendations(spotify, seed_artists=seed_artists, seed_tracks=seed_tracks))
    
    elif cmd.startswith("create recommendations playlist ") and spotify:
        parts = cmd[31:].strip().split(" - ", 1)
        if len(parts) < 2:
            log.append("❌ Please use format: create recommendations playlist <name> - <based on...>")
        else:
            playlist_name = parts[0].strip()
            seed_description = parts[1].strip()
            
            if not playlist_name or not seed_description:
                log.append("❌ Please specify both playlist name and what it should be based on.")
            else:
                from utils.spotify_helper import create_recommendations_playlist
                log.append(create_recommendations_playlist(spotify, playlist_name, seed_description))
    
    elif cmd.startswith("mood playlist ") and spotify:
        parts = cmd[14:].strip().split(" - ", 1)
        mood = parts[0].strip().lower()
        playlist_name = parts[1].strip() if len(parts) > 1 else None
        
        if not mood:
            log.append("❌ Please specify a mood (happy, sad, energetic, relaxed, workout, focus, party, sleep).")
        else:
            from utils.spotify_helper import create_mood_playlist
            log.append(create_mood_playlist(spotify, mood, playlist_name))
            
    elif cmd == "my playlists" and spotify:
        from utils.spotify_helper import get_user_playlists
        log.append(get_user_playlists(spotify))
    
    # Spotify user profile and stats
    elif cmd in ["my top tracks", "top tracks"] and spotify:
        from utils.spotify_helper import get_top_tracks
        log.append(get_top_tracks(spotify))
        
    elif cmd.startswith("my top tracks ") and spotify:
        time_range = cmd[13:].strip().lower()
        valid_ranges = {"recent": "short_term", "all time": "long_term", "overall": "medium_term"}
        time_range = valid_ranges.get(time_range, "medium_term")
        
        from utils.spotify_helper import get_top_tracks
        log.append(get_top_tracks(spotify, time_range=time_range))
        
    elif cmd in ["my top artists", "top artists"] and spotify:
        from utils.spotify_helper import get_top_artists
        log.append(get_top_artists(spotify))
        
    elif cmd.startswith("my top artists ") and spotify:
        time_range = cmd[14:].strip().lower()
        valid_ranges = {"recent": "short_term", "all time": "long_term", "overall": "medium_term"}
        time_range = valid_ranges.get(time_range, "medium_term")
        
        from utils.spotify_helper import get_top_artists
        log.append(get_top_artists(spotify, time_range=time_range))
        
    elif cmd in ["recently played", "my recent tracks"] and spotify:
        from utils.spotify_helper import get_recently_played
        log.append(get_recently_played(spotify))
        
    elif cmd in ["my albums", "saved albums"] and spotify:
        from utils.spotify_helper import get_saved_albums
        log.append(get_saved_albums(spotify))
        
    elif cmd in ["followed artists", "artists i follow"] and spotify:
        from utils.spotify_helper import get_followed_artists
        log.append(get_followed_artists(spotify))
        
    elif cmd in ["music stats", "my listening stats", "spotify stats"] and spotify:
        from utils.spotify_helper import get_listening_stats
        log.append(get_listening_stats(spotify))
    
    # Spotify music discovery
    elif cmd in ["new releases", "new music"] and spotify:
        from utils.spotify_helper import get_new_releases
        log.append(get_new_releases(spotify))
        
    elif cmd.startswith("similar artists to ") and spotify:
        artist_name = cmd[18:].strip()
        if not artist_name:
            log.append("❌ Please specify an artist to find similar ones.")
        else:
            from utils.spotify_helper import discover_similar_artists
            log.append(discover_similar_artists(spotify, artist_name))
            
    elif cmd in ["featured playlists", "spotify featured"] and spotify:
        from utils.spotify_helper import get_featured_playlists
        log.append(get_featured_playlists(spotify))
        
    elif cmd.startswith("category playlists ") and spotify:
        category = cmd[19:].strip()
        if not category:
            log.append("❌ Please specify a category to browse playlists.")
        else:
            from utils.spotify_helper import get_category_playlists
            log.append(get_category_playlists(spotify, category))
            
    elif cmd.startswith("analyze track ") and spotify:
        track_name = cmd[14:].strip()
        if not track_name:
            log.append("❌ Please specify a track to analyze.")
        else:
            from utils.spotify_helper import get_track_audio_features
            log.append(get_track_audio_features(spotify, track_name))
    
    # Spotify social features
    elif cmd.startswith("follow artist ") and spotify:
        artist_name = cmd[14:].strip()
        if not artist_name:
            log.append("❌ Please specify an artist to follow.")
        else:
            from utils.spotify_helper import follow_artist
            log.append(follow_artist(spotify, artist_name))
            
    elif cmd.startswith("unfollow artist ") and spotify:
        artist_name = cmd[16:].strip()
        if not artist_name:
            log.append("❌ Please specify an artist to unfollow.")
        else:
            from utils.spotify_helper import unfollow_artist
            log.append(unfollow_artist(spotify, artist_name))
            
    elif cmd.startswith("share track ") and spotify:
        track_name = cmd[12:].strip()
        if not track_name:
            log.append("❌ Please specify a track to share.")
        else:
            from utils.spotify_helper import share_track
            log.append(share_track(spotify, track_name))
    
    # Spotify context-specific playlists
    elif cmd.startswith("travel playlist ") and spotify:
        parts = cmd[16:].strip().split(" - ", 1)
        destination = parts[0].strip()
        playlist_name = parts[1].strip() if len(parts) > 1 else None
        
        if not destination:
            log.append("❌ Please specify a travel destination.")
        else:
            from utils.spotify_helper import create_travel_playlist
            log.append(create_travel_playlist(spotify, destination, playlist_name))
            
    elif cmd.startswith("workout playlist ") and spotify:
        parts = cmd[17:].strip().split(" - ", 1)
        workout_type = parts[0].strip().lower()
        duration = 45  # Default duration
        
        # Check if there's a duration specified
        if len(parts) > 1 and parts[1].strip().isdigit():
            duration = int(parts[1].strip())
        elif len(parts) > 1 and "min" in parts[1].lower():
            try:
                duration = int(parts[1].lower().replace("min", "").strip())
            except ValueError:
                duration = 45
        
        if not workout_type:
            log.append("❌ Please specify a workout type (cardio, hiit, strength, yoga, running).")
        else:
            from utils.spotify_helper import create_workout_playlist
            log.append(create_workout_playlist(spotify, workout_type, duration))
    
    # Auth commands
    elif cmd == "connect spotify":
        result["redirect"] = url_for("authorize_spotify")
        log.append("🔄 Redirecting to Spotify authorization...")
        
    elif cmd == "connect google":
        result["redirect"] = url_for("authorize_google")
        log.append("🔄 Redirecting to Google authorization...")
        
    # Spotify-specific help command
    elif cmd == "help spotify" and spotify:
        log.append("🎵 Spotify Commands:")
        
        log.append("▶️ Playback Controls:")
        log.append("- play [song] - Play a song")
        log.append("- play artist [name] - Play top tracks from an artist")
        log.append("- play album [name] - Play an album")
        log.append("- play playlist [name] - Play a playlist")
        log.append("- pause - Pause playback")
        log.append("- resume/continue - Resume playback")
        log.append("- next/skip - Skip to next track")
        log.append("- previous/prev/back - Go to previous track")
        log.append("- volume [0-100] - Set volume level")
        log.append("- shuffle - Toggle shuffle mode")
        log.append("- repeat - Toggle repeat mode")
        log.append("- now playing/current song/what's playing - Show current track")
        
        log.append("")
        log.append("📝 Playlist Management:")
        log.append("- create playlist [name] - [description] - Create a new playlist")
        log.append("- add to playlist [name] - [track] - Add a track to a playlist")
        log.append("- my playlists - List your playlists")
        log.append("- recommend [artist/track] - Get music recommendations")
        log.append("- create recommendations playlist [name] - [based on...] - Make playlist with recommendations")
        
        log.append("")
        log.append("🔮 Smart Playlists:")
        log.append("- mood playlist [mood] - Create a playlist based on mood")
        log.append("  Available moods: happy, sad, energetic, relaxed, workout, focus, party, sleep")
        log.append("- travel playlist [destination] - Create a playlist for your trip")
        log.append("- workout playlist [type] - [duration] - Create a workout playlist")
        log.append("  Workout types: cardio, hiit, strength, yoga, running")
        
        log.append("")
        log.append("👤 Your Profile & Stats:")
        log.append("- my top tracks - Show your most played tracks (last 6 months)")
        log.append("- my top tracks recent - Show your recently most played tracks (4 weeks)")
        log.append("- my top tracks all time - Show your all-time most played tracks")
        log.append("- my top artists - Show your most played artists")
        log.append("- recently played - Show recently played tracks")
        log.append("- my albums/saved albums - Show your saved albums")
        log.append("- followed artists - Show artists you follow")
        log.append("- music stats - Get listening statistics and insights")
        
        log.append("")
        log.append("🔎 Music Discovery:")
        log.append("- new releases - Browse new album releases")
        log.append("- similar artists to [name] - Find similar artists")
        log.append("- featured playlists - Show Spotify's featured playlists")
        log.append("- category playlists [category] - Browse playlists by category")
        log.append("- analyze track [name] - Get audio features analysis for a track")
        
        log.append("")
        log.append("🔗 Social & Sharing:")
        log.append("- follow artist [name] - Follow an artist")
        log.append("- unfollow artist [name] - Unfollow an artist")
        log.append("- share track [name] - Get a shareable link for a track")
        
        return redirect(url_for("index"))
        
    # Help command
    elif cmd == "help":
        log.append("🔍 Available commands:")
        log.append("- add [event] at [time] - Create a calendar event")
        log.append("- what's my day - Show today's calendar events")
        log.append("- log workout: [details] - Log workout details")
        log.append("- log mood: [mood] [details] - Log your mood")
        log.append("- show aa reflection - Display AA daily reflection")
        log.append("- add task: [task] - Add a task to Google Tasks")
        log.append("- add note: [note] - Add a note to Google Keep")
        log.append("- weekly summary - Get an AI summary of your week")
        log.append("- motivate me - Get a motivational quote")
        log.append("- add doctor [name] - Add a new doctor to your list")
        
        # AI Assistant section
        log.append("")
        log.append("🤖 AI Assistant Commands:")
        log.append("- chat: [message] - Have a conversation with the AI assistant")
        
        # Gmail section
        log.append("")
        log.append("📧 Gmail Analysis Commands:")
        log.append("- analyze email: [content] - Analyze email content for key points and action items")
        
        # Google Drive section
        log.append("")
        log.append("📁 Google Drive Commands:")
        log.append("- list files - Show your recent files in Google Drive")
        log.append("- search drive: [query] - Search for files in Google Drive")
        log.append("- create document: [title] - Create a new Google Doc")
        log.append("- create spreadsheet: [title] - Create a new Google Sheet")
        
        # Google Maps section
        log.append("")
        log.append("🗺️ Google Maps Commands:")
        log.append("- directions from [origin] to [destination] - Get directions between locations")
        log.append("- find places near [location] - Find interesting places near a location")
        
        # Google Photos section
        log.append("")
        log.append("📷 Google Photos Commands:")
        log.append("- list albums - Show your photo albums")
        log.append("- recent photos - Show your recently added photos")
        
        # Google Docs/Sheets section
        log.append("")
        log.append("📝 Google Docs & Sheets Commands:")
        log.append("- create recovery journal - Create a recovery journal document")
        log.append("- create medication tracker - Create a medication tracking spreadsheet")
        log.append("- create budget tracker - Create a budget spreadsheet")
        log.append("- create travel planner: [destination] - Create a travel planning document")
        
        # YouTube section
        log.append("")
        log.append("🎥 YouTube Commands:")
        log.append("- search youtube: [query] - Search for videos on YouTube")
        log.append("- find recovery videos - Find AA and recovery-related videos")
        log.append("- find meditation videos - Find guided meditation videos")
        log.append("- create recovery playlist - Create a playlist with recovery-related videos")
        
        # Medical commands
        log.append("")
        log.append("🩺 Medical Commands:")
        log.append("- list doctors - Show your saved doctors")
        log.append("- set appointment with [doctor] on [date/time] - Schedule an appointment")
        log.append("- show appointments - List your upcoming appointments")
        log.append("")
        log.append("📋 Shopping Lists:")
        log.append("- create shopping list [name] - Create a new shopping list")
        log.append("- show shopping lists - Show all your shopping lists")
        log.append("")
        
        # If Spotify is available, show Spotify commands
        if spotify:
            log.append("🎵 Spotify Commands:")
            log.append("▶️ Playback:")
            log.append("- play [song] - Play a song")
            log.append("- play artist [name] - Play top tracks from an artist")
            log.append("- play album [name] - Play an album")
            log.append("- play playlist [name] - Play a playlist")
            log.append("- pause - Pause playback")
            log.append("- resume/continue - Resume playback")
            log.append("- next/skip - Skip to next track")
            log.append("- previous/prev/back - Go to previous track")
            log.append("- volume [0-100] - Set volume level")
            log.append("- shuffle - Toggle shuffle mode")
            log.append("- repeat - Toggle repeat mode")
            log.append("- now playing/current song/what's playing - Show current track")
            log.append("")
            
            log.append("📝 Playlists:")
            log.append("- create playlist [name] - [description] - Create a new playlist")
            log.append("- add to playlist [name] - [track] - Add a track to a playlist")
            log.append("- my playlists - List your playlists")
            log.append("- recommend [artist/track] - Get music recommendations")
            log.append("- create recommendations playlist [name] - [based on...] - Create a playlist with recommendations")
            log.append("- mood playlist [mood] - [optional name] - Create a playlist based on mood")
            log.append("- travel playlist [destination] - Create a playlist for your trip")
            log.append("- workout playlist [type] - [duration] - Create a playlist for working out")
            log.append("")
            
            log.append("👤 Your Profile:")
            log.append("- my top tracks/top tracks - Show your most played tracks")
            log.append("- my top tracks [recent/all time] - Show tracks for specific time period")
            log.append("- my top artists/top artists - Show your most played artists")
            log.append("- my top artists [recent/all time] - Show artists for specific time period")
            log.append("- recently played/my recent tracks - Show recently played tracks")
            log.append("- my albums/saved albums - Show your saved albums")
            log.append("- followed artists/artists i follow - Show artists you follow")
            log.append("- music stats/my listening stats/spotify stats - Get listening statistics")
            log.append("")
            
            log.append("🔎 Discovery:")
            log.append("- new releases/new music - Browse new album releases")
            log.append("- similar artists to [name] - Find similar artists")
            log.append("- featured playlists/spotify featured - Show Spotify's featured playlists")
            log.append("- category playlists [category] - Browse playlists by category")
            log.append("- analyze track [name] - Get audio features analysis for a track")
            log.append("")
            
            log.append("🔗 Social:")
            log.append("- follow artist [name] - Follow an artist")
            log.append("- unfollow artist [name] - Unfollow an artist")
            log.append("- share track [name] - Get a shareable link for a track")
            log.append("")
            
            log.append("🔄 Connection:")
            log.append("- connect spotify - Link your Spotify account")
            log.append("")
            log.append("For full Spotify command details, type 'help spotify'")
            log.append("")
        else:
            log.append("🎵 Spotify: Run 'connect spotify' to enable Spotify commands")
            log.append("")
        log.append("- add [item] to [list] - Add an item to a shopping list")
        log.append("- show [list] - View items in a specific shopping list")
        log.append("")
        log.append("💼 Products:")
        log.append("- add product [name] - Add a product to track")
        log.append("- show products - List all your tracked products")
        log.append("- set [product] as recurring every [days] days - Set up automatic reordering")
        log.append("- show products to order - Show products due for ordering")
        log.append("")
        log.append("💰 Budget & Expenses:")
        log.append("- create budget [name] [amount] - Create a new budget")
        log.append("- show budgets - List all your budgets")
        log.append("- budget summary - Show your current month's budget summary")
        log.append("- add expense [description] [amount] - Record a new expense")
        log.append("- show expenses - List your recent expenses")
        log.append("- show upcoming payments - Show bills and recurring payments due soon")
        log.append("")
        log.append("✈️ Travel Planning:")
        log.append("- plan trip to [destination] from [start_date] to [end_date] - Plan a new trip")
        log.append("- show trips - List all your upcoming trips")
        log.append("- show trip details for [destination] - Show detailed info about a trip")
        log.append("- generate packing list for [destination] - Create a standard packing list")
        log.append("- show packing list for [destination] - View your trip packing list")
        log.append("- pack/unpack [item] - Mark items on your packing list")
        log.append("- add to packing list [item] - Add a new item to your packing list")
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
        log.append("🌦️ Weather & Pain Management:")
        log.append("- weather [location] - Get current weather for a location")
        log.append("- forecast [days] in [location] - Get weather forecast")
        log.append("- save location [name] - Save a location for weather tracking")
        log.append("- my locations - List your saved weather locations")
        log.append("- set primary location [name] - Set your default weather location")
        log.append("- pain forecast in [location] - Get pain flare risk prediction")
        log.append("- pain forecast next [hours] hours - Check extended pain forecast")
        log.append("")
        log.append("🧠 DBT Skills & Mental Health:")
        log.append("- dbt skill for [situation] - Get a DBT skill suggestion for your situation")
        log.append("- diary card [description] - Generate and save a DBT diary card")
        log.append("- validate [experience] - Get validation for difficult feelings")
        log.append("- distress [situation] - Get distress tolerance skills for crisis")
        log.append("- chain analysis [behavior] - Start a DBT chain analysis")
        log.append("- wise mind [dilemma] - Balance emotional and rational thinking")
        log.append("- radical acceptance [situation] - Practice radical acceptance")
        log.append("- accept [situation] - Short form for radical acceptance")
        log.append("- interpersonal [situation] - Get interpersonal effectiveness skills")
        log.append("- dialectic [thought] - Generate a dialectical perspective")
        log.append("- trigger map [pattern] - Analyze your trigger patterns")
        log.append("- skill of the day - Get a random DBT skill to practice")
        log.append("- dbt advice [situation] - Get general DBT advice")
        log.append("- edit message with [skill] tone [tone]: [message] - Edit your communication")
        log.append("- log skill [name] category [category] effectiveness [1-5]: [situation] - Log your skill use")
        log.append("- show diary cards - View your recent diary cards")
        log.append("- my dbt skills - View your logged DBT skills")
        log.append("")
        log.append("📊 DBT Skill Recommendations:")
        log.append("- recommend skills - Get personalized skill recommendations")
        log.append("- recommend for [situation] - Get skills for a specific situation")
        log.append("- analyze skills - Update your skill recommendations")
        log.append("")
        log.append("🎯 DBT Skill Challenges:")
        log.append("- my challenges - List your skill practice challenges")
        log.append("- new challenge - Generate a personalized skill challenge")
        log.append("- challenge details [id] - View challenge details")
        log.append("- update challenge [id] [0-100] - Update challenge progress")
        log.append("- complete challenge [id] - Mark a challenge as completed")
        log.append("")
        log.append("🚨 Crisis Management:")
        log.append("- crisis help - Show crisis resources and options")
        log.append("- crisis plan - Generate a personalized crisis plan")
        log.append("- ground me - Get a grounding exercise")
        log.append("- crisis steps [1-10] - Get crisis de-escalation steps")
        log.append("")
        log.append("😊 Emotion Regulation:")
        log.append("- track emotion [name] [intensity 1-10] - Log an emotion")
        log.append("- my emotions - View your emotion history")
        log.append("- emotion stats - Get emotion statistics")
        log.append("- emotion insights - Get personalized insights")
        log.append("- opposite action for [emotion] - Get opposite action suggestions")
        log.append("- identify emotion from [description] - Help identify emotions")
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
            
    # Budget & Expense Command Handlers
    elif cmd.startswith("create budget "):
        try:
            # Parse "create budget [name] [amount]"
            parts = cmd[14:].strip().split(" ", 1)
            if len(parts) < 2:
                log.append("❌ Please include both a name and amount for the budget.")
                log.append("Format: create budget [name] [amount]")
                return True
                
            budget_name = parts[0]
            
            # Try to extract the amount
            try:
                # Look for the amount in the second part
                amount_match = re.search(r'(\d+(\.\d+)?)', parts[1])
                if amount_match:
                    amount = float(amount_match.group(1))
                else:
                    log.append("❌ Could not find a valid amount in your command.")
                    log.append("Format: create budget [name] [amount]")
                    return True
            except (ValueError, TypeError):
                log.append(f"❌ Invalid amount: {parts[1]}. Please enter a number.")
                return True
                
            # Try to extract category if provided
            category = None
            category_match = re.search(r'category (\w+)', parts[1].lower())
            if category_match:
                category_name = category_match.group(1).upper()
                # Find matching category if available
                for cat in ExpenseCategory:
                    if cat.name.startswith(category_name) or category_name in cat.value.upper():
                        category = cat.value
                        break
                        
            budget = create_budget(name=budget_name, amount=amount, category=category, session=session)
            if budget:
                log.append(f"✅ Created budget: {budget_name} with amount ${amount:.2f}")
                if category:
                    log.append(f"Category: {category}")
            else:
                log.append("❌ Failed to create budget. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error creating budget: {str(e)}")
            return True
            
    elif cmd == "show budgets" or "my budgets" in cmd:
        try:
            budgets = get_budgets(session)
            if not budgets:
                log.append("ℹ️ You don't have any budgets set up yet.")
                log.append("Use 'create budget [name] [amount]' to create one.")
            else:
                log.append("💰 Your budgets:")
                for budget in budgets:
                    amount_str = f"${budget.amount:.2f}"
                    category_str = f" ({budget.category})" if budget.category else ""
                    log.append(f"- {budget.name}: {amount_str}{category_str}")
                    
                    # Calculate spent/remaining
                    if budget.expenses:
                        spent = sum(expense.amount for expense in budget.expenses)
                        remaining = budget.amount - spent
                        percent = (spent / budget.amount * 100) if budget.amount > 0 else 0
                        log.append(f"  Spent: ${spent:.2f} ({percent:.1f}%) | Remaining: ${remaining:.2f}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving budgets: {str(e)}")
            return True
            
    elif cmd == "budget summary" or cmd == "show budget summary":
        try:
            summary = get_budget_summary(session)
            if not summary or summary.get('total_budget', 0) == 0:
                log.append("ℹ️ You don't have any budgets set up for this month.")
                log.append("Use 'create budget [name] [amount]' to create one.")
            else:
                log.append(f"💰 Budget Summary for {summary['month']}:")
                log.append(f"Total Budget: ${summary['total_budget']:.2f}")
                log.append(f"Total Spent: ${summary['total_spent']:.2f} ({summary['percent_used']:.1f}%)")
                log.append(f"Remaining: ${summary['remaining']:.2f}")
                
                # Show category breakdown if available
                categories = summary.get('categories', {})
                if categories:
                    log.append("\nCategory Breakdown:")
                    for cat_name, cat_data in categories.items():
                        if cat_data['budget'] > 0:
                            percent = (cat_data['spent'] / cat_data['budget'] * 100) if cat_data['budget'] > 0 else 0
                            log.append(f"- {cat_name}: ${cat_data['spent']:.2f} of ${cat_data['budget']:.2f} ({percent:.1f}%)")
            return True
            
        except Exception as e:
            log.append(f"❌ Error generating budget summary: {str(e)}")
            return True
            
    elif cmd.startswith("add expense "):
        try:
            # Parse "add expense [description] [amount]"
            parts = cmd[12:].strip().split(" ", 1)
            if len(parts) < 2:
                log.append("❌ Please include both a description and amount for the expense.")
                log.append("Format: add expense [description] [amount]")
                return True
                
            expense_desc = parts[0]
            
            # Try to extract the amount
            try:
                # Look for the amount in the second part
                amount_match = re.search(r'(\d+(\.\d+)?)', parts[1])
                if amount_match:
                    amount = float(amount_match.group(1))
                else:
                    log.append("❌ Could not find a valid amount in your command.")
                    log.append("Format: add expense [description] [amount]")
                    return True
            except (ValueError, TypeError):
                log.append(f"❌ Invalid amount: {parts[1]}. Please enter a number.")
                return True
                
            # Try to extract category if provided
            category = None
            category_match = re.search(r'category (\w+)', parts[1].lower())
            if category_match:
                category_name = category_match.group(1).upper()
                # Find matching category if available
                for cat in ExpenseCategory:
                    if cat.name.startswith(category_name) or category_name in cat.value.upper():
                        category = cat.value
                        break
                        
            # Try to extract budget name if provided
            budget_name = None
            budget_match = re.search(r'budget (\w+)', parts[1].lower())
            if budget_match:
                budget_name = budget_match.group(1)
                
            expense = add_expense(
                description=expense_desc, 
                amount=amount, 
                category=category,
                budget_name=budget_name,
                session=session
            )
            
            if expense:
                log.append(f"✅ Added expense: {expense_desc} for ${amount:.2f}")
                if category:
                    log.append(f"Category: {category}")
                if budget_name:
                    log.append(f"Budget: {budget_name}")
            else:
                log.append("❌ Failed to add expense. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error adding expense: {str(e)}")
            return True
            
    elif cmd == "show expenses" or "my expenses" in cmd:
        try:
            expenses = get_expenses(session)
            if not expenses:
                log.append("ℹ️ You don't have any expenses recorded yet.")
                log.append("Use 'add expense [description] [amount]' to add one.")
            else:
                log.append("💸 Your recent expenses:")
                
                # Group by date
                today = datetime.datetime.now().date()
                yesterday = today - datetime.timedelta(days=1)
                this_week = today - datetime.timedelta(days=7)
                this_month = today.replace(day=1)
                
                today_expenses = []
                yesterday_expenses = []
                week_expenses = []
                month_expenses = []
                older_expenses = []
                
                for expense in expenses:
                    expense_date = expense.date.date() if expense.date else None
                    if expense_date == today:
                        today_expenses.append(expense)
                    elif expense_date == yesterday:
                        yesterday_expenses.append(expense)
                    elif expense_date and expense_date >= this_week:
                        week_expenses.append(expense)
                    elif expense_date and expense_date >= this_month:
                        month_expenses.append(expense)
                    else:
                        older_expenses.append(expense)
                
                # Display expenses by time group
                if today_expenses:
                    log.append("\nToday:")
                    for expense in today_expenses:
                        category_str = f" ({expense.category})" if expense.category else ""
                        log.append(f"- {expense.description}: ${expense.amount:.2f}{category_str}")
                        
                if yesterday_expenses:
                    log.append("\nYesterday:")
                    for expense in yesterday_expenses:
                        category_str = f" ({expense.category})" if expense.category else ""
                        log.append(f"- {expense.description}: ${expense.amount:.2f}{category_str}")
                        
                if week_expenses:
                    log.append("\nThis Week:")
                    for expense in week_expenses:
                        date_str = expense.date.strftime("%a") if expense.date else "Unknown"
                        category_str = f" ({expense.category})" if expense.category else ""
                        log.append(f"- {date_str}: {expense.description}: ${expense.amount:.2f}{category_str}")
                        
                if month_expenses:
                    log.append("\nThis Month:")
                    for expense in month_expenses[:5]:  # Limit to 5 entries
                        date_str = expense.date.strftime("%b %d") if expense.date else "Unknown"
                        category_str = f" ({expense.category})" if expense.category else ""
                        log.append(f"- {date_str}: {expense.description}: ${expense.amount:.2f}{category_str}")
                    
                    if len(month_expenses) > 5:
                        log.append(f"  ... and {len(month_expenses) - 5} more expenses this month")
                
                # Calculate and show totals
                total_today = sum(e.amount for e in today_expenses)
                total_week = sum(e.amount for e in today_expenses + yesterday_expenses + week_expenses)
                total_month = sum(e.amount for e in today_expenses + yesterday_expenses + week_expenses + month_expenses)
                
                log.append("\nSummary:")
                log.append(f"Today: ${total_today:.2f}")
                log.append(f"This Week: ${total_week:.2f}")
                log.append(f"This Month: ${total_month:.2f}")
            
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving expenses: {str(e)}")
            return True
            
    elif cmd == "show upcoming payments" or "bills due" in cmd:
        try:
            payments = get_upcoming_payments(session)
            if not payments:
                log.append("✅ You don't have any upcoming payments due.")
            else:
                log.append("📅 Upcoming payments due:")
                for payment in payments:
                    due_date = payment.next_due_date.strftime("%B %d") if payment.next_due_date else "Unknown"
                    category_str = f" ({payment.category})" if payment.category else ""
                    log.append(f"- {payment.name}: ${payment.amount:.2f} due {due_date}{category_str}")
                    
                    # Show payment link if available
                    if payment.website:
                        log.append(f"  🔗 Pay at: {payment.website}")
            return True
            
        except Exception as e:
            log.append(f"❌ Error checking upcoming payments: {str(e)}")
            return True
            
    # Travel Planning Command Handlers
    elif cmd.startswith("plan trip "):
        try:
            # Parse "plan trip to [destination] from [start_date] to [end_date]"
            trip_info = cmd[10:].strip()
            
            # Extract destination
            destination = None
            destination_match = re.search(r'to ([^\"]*?)(?= from| on| for| starting| $)', trip_info)
            if destination_match:
                destination = destination_match.group(1).strip()
            
            if not destination:
                log.append("❌ Please specify a destination for your trip.")
                log.append("Format: plan trip to [destination] from [start_date] to [end_date]")
                return True
                
            # Extract dates if provided
            start_date = None
            end_date = None
            
            # Look for "from [date] to [date]" pattern
            dates_match = re.search(r'from (.*?) to (.*?)(?= for| $)', trip_info)
            if dates_match:
                start_date_str = dates_match.group(1).strip()
                end_date_str = dates_match.group(2).strip()
                
                # Parse dates
                date_formats = [
                    "%Y-%m-%d",  # 2023-10-15
                    "%B %d",  # October 15
                    "%B %d, %Y",  # October 15, 2023
                    "%b %d",  # Oct 15
                    "%b %d, %Y",  # Oct 15, 2023
                ]
                
                # Try to parse start date
                for fmt in date_formats:
                    try:
                        # Add current year if not specified
                        if "%Y" not in fmt and "," not in start_date_str:
                            current_year = datetime.datetime.now().year
                            start_date = datetime.datetime.strptime(f"{start_date_str}, {current_year}", f"{fmt}, %Y")
                        else:
                            start_date = datetime.datetime.strptime(start_date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                # Try to parse end date
                for fmt in date_formats:
                    try:
                        # Add current year if not specified
                        if "%Y" not in fmt and "," not in end_date_str:
                            current_year = datetime.datetime.now().year
                            end_date = datetime.datetime.strptime(f"{end_date_str}, {current_year}", f"{fmt}, %Y")
                        else:
                            end_date = datetime.datetime.strptime(end_date_str, fmt)
                        break
                    except ValueError:
                        continue
            
            # Generate a name for the trip
            name = f"Trip to {destination}"
            
            # Create the trip
            trip = create_trip(
                name=name,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                session=session
            )
            
            if trip:
                log.append(f"✅ Created trip to {destination}")
                if start_date and end_date:
                    duration = (end_date - start_date).days
                    log.append(f"Dates: {start_date.strftime('%B %d')} to {end_date.strftime('%B %d')} ({duration} days)")
                
                # Offer to generate a packing list
                log.append("\nWould you like me to generate a standard packing list for this trip?")
                log.append("Type 'generate packing list for [destination]' to create one.")
            else:
                log.append("❌ Failed to create trip. Please try again.")
            return True
            
        except Exception as e:
            log.append(f"❌ Error planning trip: {str(e)}")
            return True
            
    elif cmd == "show trips" or "my trips" in cmd:
        try:
            # Get both upcoming and active trips
            upcoming_trips = get_upcoming_trips(session)
            active_trip = get_active_trip(session)
            
            if not upcoming_trips and not active_trip:
                log.append("ℹ️ You don't have any upcoming trips.")
                log.append("Use 'plan trip to [destination]' to plan one.")
            else:
                # Show active trip first if any
                if active_trip:
                    log.append("🌟 Currently Active Trip:")
                    log.append(f"- {active_trip.name} ({active_trip.destination})")
                    if active_trip.start_date and active_trip.end_date:
                        duration = (active_trip.end_date - active_trip.start_date).days
                        today = datetime.datetime.now()
                        days_left = (active_trip.end_date - today).days
                        log.append(f"  Dates: {active_trip.start_date.strftime('%B %d')} to {active_trip.end_date.strftime('%B %d')} ({duration} days)")
                        log.append(f"  {days_left} days remaining")
                    log.append(f"  Type 'show trip details for {active_trip.destination}' for more information")
                
                # Show upcoming trips
                upcoming_trips = [t for t in upcoming_trips if not active_trip or t.id != active_trip.id]
                if upcoming_trips:
                    log.append("\n🗓️ Upcoming Trips:")
                    for trip in upcoming_trips:
                        log.append(f"- {trip.name} ({trip.destination})")
                        if trip.start_date:
                            # Calculate days until trip
                            today = datetime.datetime.now()
                            days_until = (trip.start_date - today).days
                            date_str = trip.start_date.strftime("%B %d")
                            log.append(f"  Starting: {date_str} (in {days_until} days)")
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving trips: {str(e)}")
            return True
            
    elif "trip details" in cmd.lower():
        try:
            # Parse "show trip details for [destination]"
            destination = None
            destination_match = re.search(r'for ([^\"]*?)(?= $|$)', cmd)
            if destination_match:
                destination = destination_match.group(1).strip()
            
            if destination:
                # Try to find trip by destination
                trip = get_trip_by_name(destination, session)
                if not trip:
                    # Try getting active trip if no destination specified
                    trip = get_active_trip(session)
                    
            else:
                # If no destination specified, get active trip
                trip = get_active_trip(session)
                
            if not trip:
                log.append("❌ No matching trip found.")
                log.append("Use 'show trips' to see your trips.")
                return True
                
            log.append(f"🧳 {trip.name} Details:")
            log.append(f"Destination: {trip.destination}")
            
            if trip.start_date and trip.end_date:
                duration = (trip.end_date - trip.start_date).days
                log.append(f"Dates: {trip.start_date.strftime('%B %d')} to {trip.end_date.strftime('%B %d')} ({duration} days)")
                
                # Show countdown if trip is upcoming
                today = datetime.datetime.now()
                if trip.start_date > today:
                    days_until = (trip.start_date - today).days
                    log.append(f"Starting in {days_until} days")
                elif trip.end_date > today:
                    days_left = (trip.end_date - today).days
                    log.append(f"{days_left} days remaining")
                    
            if trip.budget:
                log.append(f"Budget: ${trip.budget:.2f}")
                
            if trip.notes:
                log.append(f"Notes: {trip.notes}")
                
            # Show itinerary summary
            itinerary = get_itinerary(trip.id, session)
            if itinerary:
                log.append(f"\nItinerary: {len(itinerary)} items")
                # Group by date
                by_date = {}
                for item in itinerary:
                    date_key = item.date.strftime("%Y-%m-%d") if item.date else "Unscheduled"
                    if date_key not in by_date:
                        by_date[date_key] = []
                    by_date[date_key].append(item)
                    
                # Show first few days
                for date_key in sorted(by_date.keys())[:3]:
                    if date_key == "Unscheduled":
                        display_date = "Unscheduled"
                    else:
                        display_date = datetime.datetime.strptime(date_key, "%Y-%m-%d").strftime("%A, %B %d")
                    log.append(f"- {display_date}: {len(by_date[date_key])} activities")
                
                if len(by_date) > 3:
                    log.append(f"  ... and {len(by_date) - 3} more days")
                    
                log.append("Type 'show itinerary for [destination]' to see the full schedule")
                
            # Show accommodation summary
            accommodations = get_accommodations(trip.id, session)
            if accommodations:
                log.append(f"\nAccommodations: {len(accommodations)}")
                for acc in accommodations[:2]:
                    check_in = acc.check_in_date.strftime("%B %d") if acc.check_in_date else "?"
                    check_out = acc.check_out_date.strftime("%B %d") if acc.check_out_date else "?"
                    log.append(f"- {acc.name}: {check_in} to {check_out}")
                    
                if len(accommodations) > 2:
                    log.append(f"  ... and {len(accommodations) - 2} more accommodations")
                    
            # Show travel document summary
            documents = get_travel_documents(trip.id, session)
            if documents:
                log.append(f"\nTravel Documents: {len(documents)}")
                for doc in documents[:2]:
                    doc_type = f"({doc.document_type})" if doc.document_type else ""
                    log.append(f"- {doc.name} {doc_type}")
                    
                if len(documents) > 2:
                    log.append(f"  ... and {len(documents) - 2} more documents")
                    
            # Show packing progress
            packing_progress = get_packing_progress(trip.id, session)
            if packing_progress and packing_progress['total_items'] > 0:
                log.append(f"\nPacking List: {packing_progress['packed_items']}/{packing_progress['total_items']} items packed ({packing_progress['percent_packed']:.0f}%)")
                log.append("Type 'show packing list for [destination]' to view and update")
                
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving trip details: {str(e)}")
            return True
            
    elif "generate packing list" in cmd.lower():
        try:
            # Parse "generate packing list for [destination]"
            destination = None
            destination_match = re.search(r'for ([^\"]*?)(?= $|$)', cmd)
            if destination_match:
                destination = destination_match.group(1).strip()
            
            if destination:
                # Try to find trip by destination
                trip = get_trip_by_name(destination, session)
                if not trip:
                    # Try getting active trip if no destination specified
                    trip = get_active_trip(session)
                    
            else:
                # If no destination specified, get active trip
                trip = get_active_trip(session)
                
            if not trip:
                log.append("❌ No matching trip found.")
                log.append("Use 'show trips' to see your trips.")
                return True
                
            # Generate the packing list
            items = generate_standard_packing_list(trip.id, session)
            if items:
                log.append(f"✅ Generated a packing list with {len(items)} items for your trip to {trip.destination}")
                log.append("Type 'show packing list for [destination]' to view and update")
            else:
                log.append("❌ Failed to generate packing list. Please try again.")
                
            return True
            
        except Exception as e:
            log.append(f"❌ Error generating packing list: {str(e)}")
            return True
            
    elif "packing list" in cmd.lower() and ("show" in cmd.lower() or "view" in cmd.lower()):
        try:
            # Parse "show packing list for [destination]"
            destination = None
            destination_match = re.search(r'for ([^\"]*?)(?= $|$)', cmd)
            if destination_match:
                destination = destination_match.group(1).strip()
            
            if destination:
                # Try to find trip by destination
                trip = get_trip_by_name(destination, session)
                if not trip:
                    # Try getting active trip if no destination specified
                    trip = get_active_trip(session)
                    
            else:
                # If no destination specified, get active trip
                trip = get_active_trip(session)
                
            if not trip:
                log.append("❌ No matching trip found.")
                log.append("Use 'show trips' to see your trips.")
                return True
                
            # Get packing items organized by category
            items = get_packing_list(trip.id, session)
            if not items:
                log.append(f"ℹ️ No packing list found for your trip to {trip.destination}")
                log.append("Type 'generate packing list for [destination]' to create one")
                return True
                
            # Group by category
            categories = {}
            for item in items:
                category = item.category or "Uncategorized"
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
                
            log.append(f"🧳 Packing List for {trip.destination}:")
            
            # Show packing progress
            packed_items = sum(1 for item in items if item.is_packed)
            percent_packed = (packed_items / len(items) * 100) if items else 0
            log.append(f"Progress: {packed_items}/{len(items)} items packed ({percent_packed:.0f}%)")
            
            # Show items by category
            for category, cat_items in categories.items():
                log.append(f"\n{category}:")
                for item in cat_items:
                    check = "☑️" if item.is_packed else "☐"
                    quantity_str = f" ({item.quantity})" if item.quantity > 1 else ""
                    log.append(f"- {check} {item.name}{quantity_str}")
                    
            log.append("\nUse 'pack [item]' to mark an item as packed")
            log.append("Use 'unpack [item]' to mark an item as not packed")
            log.append("Use 'add to packing list [item]' to add a new item")
                
            return True
            
        except Exception as e:
            log.append(f"❌ Error retrieving packing list: {str(e)}")
            return True
            
    elif cmd.startswith("pack "):
        try:
            item_name = cmd[5:].strip()
            
            # Find the active trip
            trip = get_active_trip(session)
            if not trip:
                log.append("❌ No active trip found.")
                log.append("Use 'show trips' to see your trips.")
                return True
                
            # Get all packing items for this trip
            items = get_packing_list(trip.id, session)
            
            # Find the item by name (case-insensitive)
            matching_items = [i for i in items if item_name.lower() in i.name.lower()]
            
            if not matching_items:
                log.append(f"❌ Item '{item_name}' not found in your packing list.")
                return True
                
            # If multiple matches, try to find an exact match
            if len(matching_items) > 1:
                exact_matches = [i for i in matching_items if i.name.lower() == item_name.lower()]
                if exact_matches:
                    matching_items = exact_matches
                    
            # Toggle the first matching item
            item = toggle_packed_status(matching_items[0].id, session)
            if item:
                status = "packed" if item.is_packed else "unpacked"
                log.append(f"✅ Marked '{item.name}' as {status}")
            else:
                log.append(f"❌ Failed to update item status. Please try again.")
                
            return True
            
        except Exception as e:
            log.append(f"❌ Error updating packing status: {str(e)}")
            return True
            
    elif cmd.startswith("unpack "):
        try:
            item_name = cmd[7:].strip()
            
            # Find the active trip
            trip = get_active_trip(session)
            if not trip:
                log.append("❌ No active trip found.")
                log.append("Use 'show trips' to see your trips.")
                return True
                
            # Get all packing items for this trip
            items = get_packing_list(trip.id, session)
            
            # Find the item by name (case-insensitive)
            matching_items = [i for i in items if item_name.lower() in i.name.lower()]
            
            if not matching_items:
                log.append(f"❌ Item '{item_name}' not found in your packing list.")
                return True
                
            # If multiple matches, try to find an exact match
            if len(matching_items) > 1:
                exact_matches = [i for i in matching_items if i.name.lower() == item_name.lower()]
                if exact_matches:
                    matching_items = exact_matches
                    
            # Toggle the first matching item
            item = toggle_packed_status(matching_items[0].id, session)
            if item:
                status = "packed" if item.is_packed else "unpacked"
                log.append(f"✅ Marked '{item.name}' as {status}")
            else:
                log.append(f"❌ Failed to update item status. Please try again.")
                
            return True
            
        except Exception as e:
            log.append(f"❌ Error updating packing status: {str(e)}")
            return True
            
    elif cmd.startswith("add to packing list "):
        try:
            item_name = cmd[19:].strip()
            
            # Find the active trip
            trip = get_active_trip(session)
            if not trip:
                log.append("❌ No active trip found.")
                log.append("Use 'show trips' to see your trips.")
                return True
                
            # Try to extract category if provided
            category = None
            category_match = re.search(r'in (\w+)$', item_name)
            if category_match:
                category = category_match.group(1).strip()
                item_name = item_name.replace(f"in {category}", "").strip()
                
            # Try to extract quantity if provided
            quantity = 1
            quantity_match = re.search(r'(\d+) (.+)', item_name)
            if quantity_match:
                try:
                    quantity = int(quantity_match.group(1))
                    item_name = quantity_match.group(2)
                except ValueError:
                    pass
                    
            # Add the item
            item = add_packing_item(
                trip_id=trip.id,
                name=item_name,
                category=category,
                quantity=quantity,
                session=session
            )
            
            if item:
                log.append(f"✅ Added '{item_name}' to your packing list")
                if quantity > 1:
                    log.append(f"Quantity: {quantity}")
                if category:
                    log.append(f"Category: {category}")
            else:
                log.append(f"❌ Failed to add item to packing list. Please try again.")
                
            return True
            
        except Exception as e:
            log.append(f"❌ Error adding to packing list: {str(e)}")
            return True
    
    # General command handling
    elif cmd == "clear":
        log.clear()
        log.append("Command log cleared.")
    
    elif cmd == "logout":
        log.append("🔄 Logging out and clearing credentials...")
        result["redirect"] = url_for("logout")
    
    # Handle chat with AI assistant
    elif cmd.startswith("chat:"):
        chat_message = cmd[5:].strip()  # Remove "chat:" prefix
        if not chat_message:
            log.append("Please include a message to chat with the assistant.")
        else:
            # Get user_id from session
            user_id = session.get('user_id', 'anonymous') if session else 'anonymous'
            response = handle_conversation(user_id, chat_message)
            log.append(f"🤖 {response}")
    
    # Handle Gmail content analysis
    elif cmd.startswith("analyze email:"):
        email_content = cmd[14:].strip()  # Remove "analyze email:" prefix
        
        if not email_content:
            log.append("Please include email content to analyze.")
        else:
            # Get user_id from session
            user_id = session.get('user_id', 'anonymous') if session else 'anonymous'
            
            # Analyze the email content
            analysis = analyze_gmail_content(user_id, email_content)
            
            if "error" in analysis:
                log.append(f"⚠️ Error analyzing email: {analysis['error']}")
            else:
                # Format the analysis results
                log.append("📧 Email Analysis:")
                log.append(f"📌 Summary: {analysis.get('summary', 'No summary available')}")
                
                # Priority
                priority = analysis.get('priority', 'Unknown')
                priority_emoji = "🔴" if priority.lower() == "high" else "🟡" if priority.lower() == "medium" else "🟢"
                log.append(f"{priority_emoji} Priority: {priority}")
                
                # Tone
                log.append(f"🎭 Tone: {analysis.get('tone', 'Unknown')}")
                
                # Key points
                key_points = analysis.get('key_points', [])
                if key_points:
                    log.append("📋 Key points:")
                    for point in key_points:
                        log.append(f"  • {point}")
                
                # Action items
                action_items = analysis.get('action_items', [])
                if action_items:
                    log.append("✅ Action items:")
                    for item in action_items:
                        log.append(f"  • {item}")
                
                # Deadlines
                deadlines = analysis.get('deadlines', [])
                if deadlines:
                    log.append("⏰ Deadlines:")
                    for deadline in deadlines:
                        log.append(f"  • {deadline}")
                
                # People mentioned
                people = analysis.get('people', [])
                if people:
                    log.append("👥 People mentioned:")
                    for person in people:
                        log.append(f"  • {person}")
                        
    elif cmd.startswith("pain forecast") or cmd.startswith("pain flare") or cmd == "pain":
        # Get pain flare forecast based on weather conditions
        location_match = re.search(r'(?:for|in|at) (.+)$', cmd)
        hours_match = re.search(r'next (\d+) hours', cmd)
        
        location = location_match.group(1) if location_match else None
        hours = int(hours_match.group(1)) if hours_match else 24
        
        try:
            # If no location provided, use primary or default
            if not location:
                # Try to get user's primary location
                from models import WeatherLocation
                user_id = session.get("user_id")
                primary_location = WeatherLocation.query.filter_by(user_id=user_id, is_primary=True).first()
                
                if primary_location:
                    location = primary_location.name
                    log.append(f"Using your primary location: {primary_location.display_name}")
                else:
                    log.append("❓ No location specified and no primary location set.")
                    log.append("Try 'pain forecast in [city name]' or 'save location [city name]' first.")
                    return result
            
            # Get current weather for the location (needed for storm data)
            weather_data = get_current_weather(location)
            if not weather_data:
                log.append(f"❓ Location '{location}' not found. Try a different location name.")
                return result
                
            # Get pressure trend data
            pressure_trend = get_pressure_trend(location, hours)
            if not pressure_trend:
                log.append(f"❌ Error retrieving pressure data for '{location}'")
                return result
                
            # Extract storm severity data
            storm_data = get_storm_severity(weather_data)
            
            # Calculate pain flare risk
            pain_risk = calculate_pain_flare_risk(pressure_trend, storm_data)
            
            # Format for display
            formatted_output = format_pain_forecast_output(pressure_trend, pain_risk)
            log.append(formatted_output)
            
            # Add tracking data to the response
            result["pain_forecast"] = {
                "location": pressure_trend["location"],
                "risk_level": pain_risk["risk_level"],
                "pressure_change": pressure_trend["overall_change"],
                "factors": pain_risk["factors"]
            }
        except Exception as e:
            log.append(f"❌ Error generating pain flare forecast: {str(e)}")
        
        return result
        
    # === DBT Commands ===
    
    # Handle DBT skill suggestions
    elif cmd.startswith("dbt skill for "):
        text = cmd[13:].strip()
        try:
            response = skills_on_demand(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"🧠 DBT Skill Suggestion: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error getting DBT skill suggestion: {str(e)}")
        return result
        
    # Handle DBT diary card generation
    elif cmd.startswith("diary card "):
        text = cmd[11:].strip()
        try:
            response = generate_diary_card(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                card_text = response['response']
                log.append(f"📝 Generated Diary Card:")
                log.append(card_text)
                
                # Try to parse and save the diary card
                try:
                    # Very basic parsing - would be better with structured response from API
                    mood_match = re.search(r'Mood rating.*?(\d)', card_text)
                    mood_rating = int(mood_match.group(1)) if mood_match else 3
                    
                    triggers = None
                    urges = None
                    skills_used = None
                    reflection = None
                    
                    # Extract triggers
                    triggers_match = re.search(r'Triggers:(.+?)(?:Urges:|$)', card_text, re.DOTALL)
                    if triggers_match:
                        triggers = triggers_match.group(1).strip()
                    
                    # Extract urges
                    urges_match = re.search(r'Urges:(.+?)(?:DBT skill|Skills used:|$)', card_text, re.DOTALL)
                    if urges_match:
                        urges = urges_match.group(1).strip()
                    
                    # Extract skills used
                    skills_match = re.search(r'(?:DBT skill|Skills used):(.+?)(?:Reflection|Note:|$)', card_text, re.DOTALL)
                    if skills_match:
                        skills_used = skills_match.group(1).strip()
                    
                    # Extract reflection
                    reflection_match = re.search(r'(?:Reflection|Note):(.+?)$', card_text, re.DOTALL)
                    if reflection_match:
                        reflection = reflection_match.group(1).strip()
                    
                    # Save to database
                    create_result = create_diary_card(
                        session, mood_rating, triggers, urges, skills_used, reflection
                    )
                    
                    if create_result.get("status") == "success":
                        log.append("✅ Diary card saved to your records")
                    else:
                        log.append(f"⚠️ {create_result.get('message', 'Could not save diary card')}")
                        
                except Exception as parse_error:
                    logging.error(f"Error parsing diary card: {str(parse_error)}")
                    log.append("⚠️ Generated diary card, but couldn't save it automatically")
        except Exception as e:
            log.append(f"❌ Error generating diary card: {str(e)}")
        return result
        
    # Handle DBT validation
    elif cmd.startswith("validate "):
        text = cmd[9:].strip()
        try:
            response = validate_experience(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"💙 Validation: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error with validation: {str(e)}")
        return result
        
    # Handle distress tolerance
    elif cmd.startswith("distress "):
        text = cmd[9:].strip()
        try:
            response = distress_tolerance(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"🧘 Distress Tolerance: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error with distress tolerance: {str(e)}")
        return result
        
    # Handle chain analysis
    elif cmd.startswith("chain analysis "):
        text = cmd[15:].strip()
        try:
            response = chain_analysis(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"🔗 Chain Analysis: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error with chain analysis: {str(e)}")
        return result
        
    # Handle wise mind
    elif cmd.startswith("wise mind "):
        text = cmd[10:].strip()
        try:
            response = wise_mind(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"🧠 Wise Mind: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error accessing wise mind: {str(e)}")
        return result
        
    # Handle radical acceptance
    elif cmd.startswith("radical acceptance ") or cmd.startswith("accept "):
        text = cmd[18:].strip() if cmd.startswith("radical acceptance ") else cmd[7:].strip()
        try:
            response = radical_acceptance(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"🙏 Radical Acceptance: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error with radical acceptance: {str(e)}")
        return result
        
    # Handle interpersonal effectiveness
    elif cmd.startswith("interpersonal "):
        text = cmd[14:].strip()
        try:
            response = interpersonal_effectiveness(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"👥 Interpersonal Effectiveness: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error with interpersonal effectiveness: {str(e)}")
        return result
        
    # Handle dialectic generation
    elif cmd.startswith("dialectic "):
        text = cmd[10:].strip()
        try:
            response = dialectic_generator(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"⚖️ Dialectic Perspective: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error generating dialectic: {str(e)}")
        return result
        
    # Handle trigger mapping
    elif cmd.startswith("trigger map "):
        text = cmd[12:].strip()
        try:
            response = trigger_map(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"🔍 Trigger Analysis: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error analyzing triggers: {str(e)}")
        return result
        
    # Handle skill of the day
    elif cmd == "skill of the day" or cmd == "dbt skill":
        try:
            response = skill_of_the_day()
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"✨ DBT Skill of the Day: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error getting skill of the day: {str(e)}")
        return result
        
    # Handle message editing with DBT skills
    elif cmd.startswith("edit message with "):
        # Example: "edit message with DEAR MAN tone firm: I need you to stop interrupting me"
        try:
            # Parse the command
            match = re.match(r'edit message with ([^:]+) tone ([^:]+):(.+)', cmd[16:])
            if match:
                skill = match.group(1).strip()
                tone = match.group(2).strip()
                message = match.group(3).strip()
                
                response = edit_message(message, skill, tone)
                if "error" in response:
                    log.append(f"❌ Error: {response['error']}")
                else:
                    log.append(f"✏️ Edited Message ({skill}, {tone} tone):")
                    log.append(response['response'])
            else:
                log.append("❌ Invalid format. Use: 'edit message with [skill] tone [tone]: [your message]'")
                log.append("Example: 'edit message with DEAR MAN tone firm: I need you to stop interrupting me'")
        except Exception as e:
            log.append(f"❌ Error editing message: {str(e)}")
        return result
        
    # Handle DBT advice
    elif cmd.startswith("dbt advice "):
        text = cmd[11:].strip()
        try:
            response = advise(text)
            if "error" in response:
                log.append(f"❌ Error: {response['error']}")
            else:
                log.append(f"💡 DBT Advice: {response['response']}")
        except Exception as e:
            log.append(f"❌ Error getting DBT advice: {str(e)}")
        return result
        
    # Handle viewing recent diary cards
    elif cmd == "show diary cards" or cmd == "my diary cards":
        try:
            cards = get_diary_cards(session)
            if not cards:
                log.append("📝 You don't have any diary cards yet. Try creating one with 'diary card [your day description]'")
            else:
                log.append(f"📝 Your recent diary cards ({len(cards)}):")
                for i, card in enumerate(cards[:3]):  # Show max 3 cards
                    log.append(f"--- Card {i+1} ({card['date']}) ---")
                    log.append(f"Mood: {card['mood_rating']}/5")
                    if card['triggers']:
                        log.append(f"Triggers: {card['triggers']}")
                    if card['skills_used']:
                        log.append(f"Skills: {card['skills_used']}")
                if len(cards) > 3:
                    log.append(f"...and {len(cards) - 3} more.")
        except Exception as e:
            log.append(f"❌ Error retrieving diary cards: {str(e)}")
        return result
        
    # Handle viewing recent skill logs
    elif cmd == "show skills" or cmd == "my dbt skills":
        try:
            logs = get_skill_logs(session)
            if not logs:
                log.append("🧠 You haven't logged any DBT skills yet.")
            else:
                log.append(f"🧠 Your recent DBT skills ({len(logs)}):")
                for i, skill_log in enumerate(logs[:5]):  # Show max 5 skills
                    log.append(f"- {skill_log['skill_name']} ({skill_log['category']})")
                    if skill_log['effectiveness']:
                        log.append(f"  Effectiveness: {skill_log['effectiveness']}/5")
                if len(logs) > 5:
                    log.append(f"...and {len(logs) - 5} more.")
        except Exception as e:
            log.append(f"❌ Error retrieving skill logs: {str(e)}")
        return result
        
    # DBT skill recommendation command
    elif cmd == "recommend skills" or cmd == "skill recommendations":
        try:
            # Get general recommendations
            recommendations = get_skill_recommendations(session)
            
            if not recommendations:
                log.append("I don't have enough data to make personalized recommendations yet. Try logging some skills first with 'log skill:'.")
                return result
                
            log.append("🔍 Your Top DBT Skill Recommendations:")
            for i, rec in enumerate(recommendations[:5]):
                log.append(f"{i+1}. **{rec['skill_name']}** ({rec['category']})")
                log.append(f"   Effectiveness: {rec['avg_effectiveness']:.1f}/5")
                log.append(f"   Best for: {rec['situation_type']}")
                log.append("")
            
            log.append("Use 'recommend for [situation]' to get recommendations for a specific situation.")
                
        except Exception as e:
            logging.error(f"Error getting skill recommendations: {str(e)}")
            log.append(f"❌ Error getting recommendations: {str(e)}")
        return result
    
    # Situation-specific recommendations
    elif cmd.startswith("recommend for "):
        try:
            # Get recommendations for a specific situation
            situation = cmd.replace("recommend for", "").strip()
            recommendations = get_skill_recommendations(session, situation_description=situation)
            
            if not recommendations:
                log.append("I couldn't find any personalized recommendations for this situation. Try logging more skills first.")
                return result
                
            log.append(f"🔍 Recommended Skills for '{situation}':")
            for i, rec in enumerate(recommendations[:5]):
                log.append(f"{i+1}. **{rec['skill_name']}** ({rec['category']})")
                log.append(f"   Effectiveness: {rec['avg_effectiveness']:.1f}/5")
                log.append("")
                
        except Exception as e:
            logging.error(f"Error getting situation recommendations: {str(e)}")
            log.append(f"❌ Error getting recommendations: {str(e)}")
        return result
    
    # Analyze skill effectiveness
    elif cmd == "analyze skills" or cmd == "update recommendations":
        try:
            # Analyze effectiveness and update recommendations
            result_data = analyze_skill_effectiveness(session)
            
            if result_data.get("status") == "success":
                log.append(f"✅ Your skill effectiveness has been analyzed! {result_data.get('message', '')}")
            elif result_data.get("status") == "info":
                log.append(f"ℹ️ Information: {result_data.get('message', '')}")
            else:
                log.append(f"❌ Error analyzing skills: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error analyzing skill effectiveness: {str(e)}")
            log.append(f"❌ Error analyzing skills: {str(e)}")
        return result
    
    # DBT skill challenges
    elif cmd == "my challenges" or cmd == "show challenges":
        try:
            # List available challenges
            challenges = get_available_challenges(session)
            
            if not challenges:
                log.append("You don't have any active DBT skill challenges. Use 'new challenge' to create one.")
                return result
                
            # Separate completed and active challenges
            active = [c for c in challenges if not c['is_completed']]
            completed = [c for c in challenges if c['is_completed']]
            
            if active:
                log.append("🎯 Your Active DBT Skill Challenges:")
                for i, c in enumerate(active[:5]):
                    log.append(f"{i+1}. **{c['challenge_name']}** (ID: {c['id']})")
                    log.append(f"   Difficulty: {'⭐' * c['difficulty']}")
                    log.append(f"   Progress: {c['progress']}%")
                    log.append(f"   Category: {c['skill_category']}")
                    log.append("")
                    
                if len(active) > 5:
                    log.append(f"...and {len(active) - 5} more active challenges.")
            else:
                log.append("You don't have any active challenges.")
                
            if completed:
                log.append(f"Completed challenges: {len(completed)}")
                
            log.append("Use 'challenge details [id]' to see details, 'complete challenge [id]' to mark as completed.")
                
        except Exception as e:
            logging.error(f"Error getting challenges: {str(e)}")
            log.append(f"❌ Error getting challenges: {str(e)}")
        return result
    
    # New challenge
    elif cmd == "new challenge":
        try:
            # Create new challenge with any category
            result_data = generate_personalized_challenge(session)
            
            if result_data.get("status") == "success":
                challenge = result_data.get("challenge", {})
                log.append("✅ New challenge created!")
                log.append(f"**{challenge.get('name')}** (Difficulty: {'⭐' * challenge.get('difficulty', 1)})")
                log.append(f"{challenge.get('description')}")
                log.append(f"Category: {challenge.get('category')}")
                log.append("")
                log.append(f"Use 'update challenge {result_data.get('id')} [0-100]' to update your progress.")
            else:
                log.append(f"❌ Error creating challenge: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error creating challenge: {str(e)}")
            log.append(f"❌ Error creating challenge: {str(e)}")
        return result
    
    # New category-specific challenge
    elif cmd.startswith("new challenge "):
        try:
            # Create new challenge with specified category
            category = cmd.replace("new challenge", "").strip().capitalize()
            result_data = generate_personalized_challenge(session, category)
            
            if result_data.get("status") == "success":
                challenge = result_data.get("challenge", {})
                log.append("✅ New challenge created!")
                log.append(f"**{challenge.get('name')}** (Difficulty: {'⭐' * challenge.get('difficulty', 1)})")
                log.append(f"{challenge.get('description')}")
                log.append(f"Category: {challenge.get('category')}")
                log.append("")
                log.append(f"Use 'update challenge {result_data.get('id')} [0-100]' to update your progress.")
            else:
                log.append(f"❌ Error creating challenge: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error creating category challenge: {str(e)}")
            log.append(f"❌ Error creating challenge: {str(e)}")
        return result
    
    # Challenge details
    elif cmd.startswith("challenge details "):
        try:
            # View challenge details by ID
            challenge_id = int(cmd.replace("challenge details", "").strip())
            challenges = get_available_challenges(session)
            
            found = False
            for c in challenges:
                if c["id"] == challenge_id:
                    found = True
                    log.append(f"🎯 **{c['challenge_name']}**")
                    log.append(f"Description: {c['description']}")
                    log.append(f"Category: {c['skill_category']}")
                    log.append(f"Difficulty: {'⭐' * c['difficulty']}")
                    log.append(f"Progress: {c['progress']}%")
                    log.append(f"Status: {'Completed ✅' if c['is_completed'] else 'In progress'}")
                    log.append(f"Started: {c['start_date']}")
                    break
                           
            if not found:
                log.append(f"❌ Challenge with ID {challenge_id} not found.")
                
        except ValueError:
            log.append("❌ Please provide a valid challenge ID. Use 'my challenges' to see your challenges.")
        except Exception as e:
            logging.error(f"Error getting challenge details: {str(e)}")
            log.append(f"❌ Error getting challenge details: {str(e)}")
        return result
    
    # Update challenge progress
    elif cmd.startswith("update challenge "):
        try:
            # Parse command
            parts = cmd.replace("update challenge", "").strip().split()
            if len(parts) < 2:
                log.append("❌ Please provide both challenge ID and progress percentage.")
                return result
                
            challenge_id = int(parts[0])
            progress = int(parts[1])
            
            result_data = update_challenge_progress(session, challenge_id, progress)
            
            if result_data.get("status") == "success":
                if result_data.get("completed"):
                    log.append(f"🎉 Great job! Challenge progress updated to {progress}% and marked as completed!")
                else:
                    log.append(f"✅ Challenge progress updated to {progress}%")
            else:
                log.append(f"❌ Error updating progress: {result_data.get('message', 'Unknown error')}")
                
        except ValueError:
            log.append("❌ Please provide a valid challenge ID and progress percentage (0-100).")
        except Exception as e:
            logging.error(f"Error updating challenge progress: {str(e)}")
            log.append(f"❌ Error updating progress: {str(e)}")
        return result
    
    # Complete challenge
    elif cmd.startswith("complete challenge "):
        try:
            # Mark challenge as completed
            challenge_id = int(cmd.replace("complete challenge", "").strip())
            
            result_data = mark_challenge_completed(session, challenge_id)
            
            if result_data.get("status") == "success":
                log.append(f"🎉 Congratulations! {result_data.get('message', 'Challenge completed!')}")
            else:
                log.append(f"❌ Error completing challenge: {result_data.get('message', 'Unknown error')}")
                
        except ValueError:
            log.append("❌ Please provide a valid challenge ID. Use 'my challenges' to see your challenges.")
        except Exception as e:
            logging.error(f"Error completing challenge: {str(e)}")
            log.append(f"❌ Error completing challenge: {str(e)}")
        return result
    
    # Reset challenge
    elif cmd.startswith("reset challenge "):
        try:
            # Reset challenge progress
            challenge_id = int(cmd.replace("reset challenge", "").strip())
            
            result_data = reset_challenge(session, challenge_id)
            
            if result_data.get("status") == "success":
                log.append(f"✅ {result_data.get('message', 'Challenge has been reset.')}")
            else:
                log.append(f"❌ Error resetting challenge: {result_data.get('message', 'Unknown error')}")
                
        except ValueError:
            log.append("❌ Please provide a valid challenge ID. Use 'my challenges' to see your challenges.")
        except Exception as e:
            logging.error(f"Error resetting challenge: {str(e)}")
            log.append(f"❌ Error resetting challenge: {str(e)}")
        return result
    
    # Crisis management
    elif cmd == "crisis help" or cmd == "crisis resources":
        try:
            # Get crisis resources and provide basic help
            resources = get_crisis_resources(session, is_emergency_only=True)
            
            if resources:
                log.append("🚨 Emergency Resources:")
                for i, r in enumerate(resources):
                    log.append(f"{i+1}. **{r['name']}**: {r['contact_info']}")
                log.append("")
            
            log.append("If you're in immediate danger, please call emergency services immediately.")
            log.append("")
            log.append("Crisis Management Commands:")
            log.append("- 'crisis plan' - Generate a personalized crisis plan")
            log.append("- 'ground me' - Get a grounding exercise")
            log.append("- 'crisis steps [1-10]' - Get crisis de-escalation steps")
            log.append("- 'all crisis resources' - List all your crisis resources")
            log.append("- 'add crisis resource' - Add a new crisis resource")
                
        except Exception as e:
            logging.error(f"Error getting crisis resources: {str(e)}")
            log.append(f"❌ Error accessing crisis resources: {str(e)}")
        return result
    
    # Generate crisis plan
    elif cmd == "crisis plan" or cmd.startswith("crisis plan for "):
        try:
            # Generate a crisis plan
            crisis_type = cmd.replace("crisis plan for", "").strip() if cmd.startswith("crisis plan for") else None
            result_data = generate_crisis_plan(session, crisis_type)
            
            if result_data.get("status") == "success":
                log.append(result_data.get('plan', 'Crisis plan could not be generated.'))
            else:
                log.append(f"❌ Error generating crisis plan: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error generating crisis plan: {str(e)}")
            log.append(f"❌ Error generating crisis plan: {str(e)}")
        return result
    
    # Grounding exercise
    elif cmd == "ground me" or cmd.startswith("ground me for "):
        try:
            # Get a grounding exercise
            trigger = cmd.replace("ground me for", "").strip() if cmd.startswith("ground me for") else None
            result_data = get_grounding_exercise(trigger)
            
            if result_data.get("status") == "success":
                log.append(result_data.get('exercise', 'Grounding exercise could not be generated.'))
            else:
                log.append(f"❌ Error generating grounding exercise: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error generating grounding exercise: {str(e)}")
            log.append(f"❌ Error generating grounding exercise: {str(e)}")
        return result
    
    # Crisis de-escalation steps
    elif cmd.startswith("crisis steps "):
        try:
            parts = cmd.replace("crisis steps", "").strip().split()
            intensity = int(parts[0]) if parts and parts[0].isdigit() else 5
            emotion = " ".join(parts[1:]) if len(parts) > 1 else None
            
            result_data = get_crisis_de_escalation(intensity, emotion)
            
            if result_data.get("status") == "success":
                log.append(result_data.get('steps', 'De-escalation steps could not be generated.'))
            else:
                log.append(f"❌ Error generating de-escalation steps: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error generating de-escalation steps: {str(e)}")
            log.append(f"❌ Error generating de-escalation steps: {str(e)}")
        return result
    
    # List all crisis resources
    elif cmd == "all crisis resources":
        try:
            # List all crisis resources
            resources = get_crisis_resources(session)
            
            if not resources:
                log.append("You don't have any crisis resources yet. Use 'add crisis resource' to add some.")
                return result
                
            log.append("Your Crisis Resources:")
            for i, r in enumerate(resources):
                log.append(f"{i+1}. {'🚨 ' if r['is_emergency'] else ''}**{r['name']}** (ID: {r['id']})")
                log.append(f"   Contact: {r['contact_info']}")
                log.append(f"   Type: {r['resource_type']}")
                if r.get('notes'):
                    log.append(f"   Notes: {r['notes']}")
                log.append("")
                
        except Exception as e:
            logging.error(f"Error listing crisis resources: {str(e)}")
            log.append(f"❌ Error listing resources: {str(e)}")
        return result
    
    # Add crisis resource
    elif cmd == "add crisis resource":
        log.append("To add a crisis resource, use this format:")
        log.append("add resource [name] [contact_info] [type] [emergency:yes/no]")
        log.append("Example: add resource 'My Therapist' '555-123-4567' therapist no")
        return result
    
    # Add resource with details
    elif cmd.startswith("add resource "):
        try:
            # Parse resource details - this is simplified and might need improvements for real-world use
            details = cmd.replace("add resource", "").strip().split()
            if len(details) < 4:
                log.append("❌ Please provide all required information: name, contact info, type, and emergency status (yes/no).")
                return result
                
            name = details[0]
            contact_info = details[1]
            resource_type = details[2]
            is_emergency = details[3].lower() in ("yes", "true", "1")
            notes = " ".join(details[4:]) if len(details) > 4 else None
            
            result_data = add_crisis_resource(session, name, contact_info, resource_type, notes, is_emergency)
            
            if result_data.get("status") == "success":
                log.append(f"✅ Crisis resource '{name}' added successfully!")
            else:
                log.append(f"❌ Error adding resource: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error adding crisis resource: {str(e)}")
            log.append(f"❌ Error adding resource: {str(e)}")
        return result
    
    # Emotion tracking
    elif cmd == "emotion help":
        log.append("Emotion Regulation Commands:")
        log.append("- 'track emotion [name] [intensity 1-10] [optional: trigger]' - Log an emotion")
        log.append("- 'my emotions' - View emotion history")
        log.append("- 'emotion stats' - Get emotion statistics")
        log.append("- 'emotion insights' - Get personalized insights")
        log.append("- 'opposite action for [emotion] [situation]' - Get opposite action suggestions")
        log.append("- 'identify emotion from [sensations/thoughts]' - Help identify emotions")
        log.append("- 'emotion vulnerability check' - Check emotional vulnerability factors")
        return result
    
    # Track emotion
    elif cmd.startswith("track emotion "):
        try:
            # Parse emotion information
            parts = cmd.replace("track emotion", "").strip().split()
            if len(parts) < 2:
                log.append("❌ Please provide emotion name and intensity level.")
                return result
                
            emotion_name = parts[0]
            try:
                intensity = int(parts[1])
                if intensity < 1 or intensity > 10:
                    log.append("❌ Intensity must be between 1-10.")
                    return result
            except ValueError:
                log.append("❌ Please provide a valid intensity level between 1-10.")
                return result
                
            trigger = " ".join(parts[2:]) if len(parts) > 2 else None
            
            # Store in session for further details
            session["emotion_log_temp"] = {
                "emotion_name": emotion_name,
                "intensity": intensity,
                "trigger": trigger
            }
            
            log.append(f"I'll track that you're feeling {emotion_name} at intensity level {intensity}.")
            log.append("")
            if trigger:
                log.append(f"Trigger: {trigger}")
            
            log.append("To complete the emotion log, you can add more details with these commands:")
            log.append("- 'emotion body [sensations]' - Add physical sensations")
            log.append("- 'emotion thoughts [thoughts]' - Add associated thoughts")
            log.append("- 'emotion urges [urges]' - Add action urges")
            log.append("- 'emotion action [actions]' - Add opposite actions taken")
            log.append("- 'save emotion' - Save the emotion log as is")
                
        except Exception as e:
            logging.error(f"Error tracking emotion: {str(e)}")
            log.append(f"❌ Error tracking emotion: {str(e)}")
        return result
    
    # Add emotion details
    elif cmd.startswith("emotion body ") or cmd.startswith("emotion thoughts ") or \
         cmd.startswith("emotion urges ") or cmd.startswith("emotion action "):
        try:
            # Store data in session for later saving
            if "emotion_log_temp" not in session:
                log.append("❌ Please start with 'track emotion [name] [intensity]' first.")
                return result
                
            temp_data = session["emotion_log_temp"]
            
            if cmd.startswith("emotion body "):
                temp_data["body_sensations"] = cmd.replace("emotion body", "").strip()
                field_name = "body sensations"
            elif cmd.startswith("emotion thoughts "):
                temp_data["thoughts"] = cmd.replace("emotion thoughts", "").strip()
                field_name = "thoughts"
            elif cmd.startswith("emotion urges "):
                temp_data["urges"] = cmd.replace("emotion urges", "").strip()
                field_name = "urges"
            elif cmd.startswith("emotion action "):
                temp_data["opposite_action"] = cmd.replace("emotion action", "").strip()
                field_name = "opposite action"
                
            session["emotion_log_temp"] = temp_data
            
            # Count how many fields are filled
            filled_count = sum(1 for key in ["body_sensations", "thoughts", "urges", "opposite_action"] 
                              if key in temp_data and temp_data[key])
            total_fields = 4
            
            log.append(f"Added {field_name} information. {filled_count}/{total_fields} optional fields completed.")
            log.append("Use 'save emotion' when you're ready to save this entry.")
                
        except Exception as e:
            logging.error(f"Error adding emotion details: {str(e)}")
            log.append(f"❌ Error adding emotion details: {str(e)}")
        return result
    
    # Save emotion log
    elif cmd == "save emotion":
        try:
            # Save the emotion log from session data
            if "emotion_log_temp" not in session:
                log.append("❌ No emotion data to save. Please start with 'track emotion [name] [intensity]' first.")
                return result
                
            temp_data = session["emotion_log_temp"]
            
            if "emotion_name" not in temp_data or "intensity" not in temp_data:
                log.append("❌ Missing required emotion information. Please start with 'track emotion [name] [intensity]'.")
                return result
                
            # Save to database
            result_data = log_emotion(
                session,
                temp_data["emotion_name"],
                temp_data["intensity"],
                temp_data.get("trigger"),
                temp_data.get("body_sensations"),
                temp_data.get("thoughts"),
                temp_data.get("urges"),
                temp_data.get("opposite_action")
            )
            
            # Clear temp data
            session.pop("emotion_log_temp", None)
            
            if result_data.get("status") == "success":
                log.append("✅ Emotion log saved successfully!")
                log.append("Use 'emotion insights' to get personalized recommendations.")
            else:
                log.append(f"❌ Error saving emotion log: {result_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            logging.error(f"Error saving emotion log: {str(e)}")
            log.append(f"❌ Error saving emotion log: {str(e)}")
        return result
    
    # View emotion history
    elif cmd == "my emotions" or cmd.startswith("my emotions "):
        try:
            # Get emotion history
            emotion_name = cmd.replace("my emotions", "").strip() if cmd.startswith("my emotions ") else None
            
            emotions = get_emotion_history(session, emotion_name=emotion_name)
            
            if not emotions:
                log.append("You don't have any emotion logs yet. Use 'track emotion' to start tracking.")
                return result
                
            filter_text = f" for '{emotion_name}'" if emotion_name else ""
            log.append(f"Your Emotion History{filter_text}:")
            
            for i, e in enumerate(emotions[:5]):
                log.append(f"{i+1}. **{e['emotion_name']}** (Intensity: {e['intensity']}/10) - {e['date_recorded']}")
                if e.get('trigger'):
                    log.append(f"   Trigger: {e['trigger']}")
                log.append("")
            
            count_text = f"Showing 5 of {len(emotions)} emotion logs" if len(emotions) > 5 else f"Showing all {len(emotions)} emotion logs"
            log.append(count_text)
                
        except Exception as e:
            logging.error(f"Error getting emotion history: {str(e)}")
            log.append(f"❌ Error getting emotion history: {str(e)}")
        return result
    
    # Emotion statistics
    elif cmd == "emotion stats" or cmd.startswith("emotion stats "):
        try:
            # Get emotion statistics
            days = 30  # Default
            if cmd.startswith("emotion stats "):
                try:
                    days = int(cmd.replace("emotion stats", "").strip())
                except ValueError:
                    pass
            
            stats = get_emotion_stats(session, days=days)
            
            if stats.get("status") == "info":
                log.append(f"ℹ️ Information: {stats.get('message', 'No emotion data available.')}")
                return result
            elif stats.get("status") == "error":
                log.append(f"❌ Error: {stats.get('message', 'Could not generate statistics.')}")
                return result
                
            log.append(f"Emotion Statistics (Last {days} Days):")
            log.append(f"Most common emotion: {stats.get('most_common_emotion', 'N/A')}")
            log.append(f"Average intensity: {stats.get('average_intensity', 0):.1f}/10")
            log.append(f"Highest intensity: {stats.get('highest_intensity', 0)}/10 ({stats.get('highest_intensity_emotion', 'N/A')})")
            if stats.get('most_common_trigger'):
                log.append(f"Most common trigger: {stats.get('most_common_trigger', 'N/A')}")
            log.append(f"Opposite action usage: {stats.get('opposite_action_percentage', 0):.1f}% of the time")
            log.append(f"Total entries: {stats.get('total_entries', 0)}")
                
        except Exception as e:
            logging.error(f"Error calculating emotion stats: {str(e)}")
            log.append(f"❌ Error calculating emotion statistics: {str(e)}")
        return result
    
    # Emotion insights
    elif cmd == "emotion insights" or cmd.startswith("emotion insights for "):
        try:
            # Get personalized insights
            emotion_name = cmd.replace("emotion insights for", "").strip() if cmd.startswith("emotion insights for") else None
            
            result_data = generate_emotion_insights(session, emotion_name)
            
            if result_data.get("status") == "info":
                log.append(f"ℹ️ Information: {result_data.get('message', 'Not enough data for insights yet.')}")
                return result
            elif result_data.get("status") == "error":
                log.append(f"❌ Error: {result_data.get('message', 'Could not generate insights.')}")
                return result
                
            log.append(result_data.get('insights', 'Could not generate insights.'))
                
        except Exception as e:
            logging.error(f"Error generating emotion insights: {str(e)}")
            log.append(f"❌ Error generating insights: {str(e)}")
        return result
    
    # Opposite action suggestions
    elif cmd.startswith("opposite action for "):
        try:
            # Get opposite action suggestions
            parts = cmd.replace("opposite action for", "").strip().split()
            if not parts:
                log.append("❌ Please specify an emotion.")
                return result
                
            emotion = parts[0]
            situation = " ".join(parts[1:]) if len(parts) > 1 else None
            
            result_data = get_opposite_action_suggestion(session, emotion, situation)
            
            if result_data.get("status") == "success":
                log.append(result_data.get('suggestions', 'Could not generate opposite action suggestions.'))
            else:
                log.append(f"❌ Error: {result_data.get('message', 'Could not generate suggestions.')}")
                
        except Exception as e:
            logging.error(f"Error generating opposite action suggestions: {str(e)}")
            log.append(f"❌ Error generating opposite action suggestions: {str(e)}")
        return result
    
    # Identify emotion
    elif cmd.startswith("identify emotion from "):
        try:
            # Help identify emotions based on provided information
            description = cmd.replace("identify emotion from", "").strip()
            
            result_data = identify_emotion(session, body_sensations=description, thoughts=description, situation=description)
            
            if result_data.get("status") == "success":
                log.append(result_data.get('analysis', 'Could not identify emotions.'))
            else:
                log.append(f"❌ Error: {result_data.get('message', 'Could not identify emotions.')}")
                
        except Exception as e:
            logging.error(f"Error identifying emotions: {str(e)}")
            log.append(f"❌ Error identifying emotions: {str(e)}")
        return result
    
    # Emotion vulnerability check
    elif cmd == "emotion vulnerability check":
        try:
            # Check emotional vulnerability
            result_data = check_emotion_vulnerability(session)
            
            if result_data.get("status") == "info":
                log.append(f"ℹ️ Information: {result_data.get('message', 'Not enough data for vulnerability check.')}")
                return result
            elif result_data.get("status") == "error":
                log.append(f"❌ Error: {result_data.get('message', 'Could not check vulnerability.')}")
                return result
                
            log.append(result_data.get('assessment', 'Could not generate vulnerability assessment.'))
                
        except Exception as e:
            logging.error(f"Error checking emotional vulnerability: {str(e)}")
            log.append(f"❌ Error checking emotional vulnerability: {str(e)}")
        return result
        
    # Handle logging a DBT skill
    elif cmd.startswith("log skill "):
        # Expected format: "log skill [skill_name] category [category] effectiveness [1-5]: [situation]"
        try:
            # Basic pattern matching - could be improved with regex
            parts = cmd[10:].split("category")
            if len(parts) < 2:
                log.append("❌ Please include a category. Format: 'log skill [name] category [category] effectiveness [1-5]: [situation]'")
                return result
                
            skill_name = parts[0].strip()
            
            category_parts = parts[1].split("effectiveness")
            category = category_parts[0].strip()
            
            effectiveness = None
            situation = None
            
            if len(category_parts) > 1:
                eff_parts = category_parts[1].split(":", 1)
                try:
                    effectiveness = int(eff_parts[0].strip())
                    if effectiveness < 1 or effectiveness > 5:
                        raise ValueError("Effectiveness must be between 1 and 5")
                except ValueError:
                    log.append("❌ Effectiveness must be a number between 1 and 5")
                    return result
                
                if len(eff_parts) > 1:
                    situation = eff_parts[1].strip()
            
            # Log the skill
            log_result = log_dbt_skill(session, skill_name, category, situation, effectiveness, None)
            
            if log_result["status"] == "success":
                log.append(f"✅ {log_result['message']}")
            else:
                log.append(f"❌ {log_result['message']}")
                
        except Exception as e:
            log.append(f"❌ Error logging skill: {str(e)}")
        return result
    
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