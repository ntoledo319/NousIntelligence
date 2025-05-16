import logging
import datetime
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
import pytz

def get_time_based_playlist_params(current_time=None, user_timezone=None):
    """
    Generate Spotify playlist parameters based on time of day
    
    Args:
        current_time: Optional datetime object (defaults to now)
        user_timezone: Optional timezone string (e.g. 'America/New_York')
        
    Returns:
        Dictionary with playlist parameters and time description
    """
    try:
        # Set up time information
        if not current_time:
            current_time = datetime.datetime.now()
            
        # Apply timezone if provided
        if user_timezone:
            try:
                tz = pytz.timezone(user_timezone)
                if not current_time.tzinfo:
                    # Make the time timezone-aware
                    current_time = tz.localize(current_time)
                else:
                    # Convert to the specified timezone
                    current_time = current_time.astimezone(tz)
            except Exception as e:
                logging.error(f"Error applying timezone: {str(e)}")
        
        # Extract time components
        hour = current_time.hour
        weekday = current_time.weekday()  # 0 = Monday, 6 = Sunday
        is_weekend = weekday >= 5
        
        # Default parameters
        params = {
            'name': 'Time-Based Playlist',
            'description': 'Music for your current time of day',
            'seed_genres': ['pop'],
            'target_energy': 0.6,
            'target_valence': 0.6,
            'min_tempo': 100,
            'max_tempo': 130
        }
        
        # Early morning (5-8 AM): Gentle wake-up music
        if 5 <= hour < 8:
            params['name'] = 'Early Morning Rise'
            params['description'] = 'Gentle music to start your day'
            params['seed_genres'] = ['ambient', 'acoustic', 'chill']
            params['target_energy'] = 0.4
            params['target_valence'] = 0.6
            params['min_tempo'] = 70
            params['max_tempo'] = 100
            time_desc = "Early Morning"
            
        # Morning (8-11 AM): Upbeat, motivational music
        elif 8 <= hour < 11:
            params['name'] = 'Morning Momentum'
            params['description'] = 'Upbeat tracks to energize your morning'
            params['seed_genres'] = ['pop', 'indie', 'feel-good']
            params['target_energy'] = 0.7
            params['target_valence'] = 0.8
            params['min_tempo'] = 100
            params['max_tempo'] = 130
            time_desc = "Morning"
            
        # Midday (11 AM-2 PM): Balanced, productive music
        elif 11 <= hour < 14:
            params['name'] = 'Midday Focus'
            params['description'] = 'Music to maintain your productivity'
            params['seed_genres'] = ['focus', 'work', 'instrumental']
            params['target_energy'] = 0.5
            params['target_valence'] = 0.6
            params['min_tempo'] = 90
            params['max_tempo'] = 120
            time_desc = "Midday"
            
        # Afternoon (2-5 PM): Upbeat, prevents afternoon slump
        elif 14 <= hour < 17:
            params['name'] = 'Afternoon Boost'
            params['description'] = 'Energizing music to beat the afternoon slump'
            params['seed_genres'] = ['dance', 'pop', 'electronic']
            params['target_energy'] = 0.7
            params['target_valence'] = 0.7
            params['min_tempo'] = 110
            params['max_tempo'] = 140
            time_desc = "Afternoon"
            
        # Evening (5-8 PM): Relaxing, transition from work
        elif 17 <= hour < 20:
            params['name'] = 'Evening Unwind'
            params['description'] = 'Music to help you transition from work to relaxation'
            params['seed_genres'] = ['chill', 'indie', 'alternative']
            params['target_energy'] = 0.5
            params['target_valence'] = 0.5
            params['min_tempo'] = 80
            params['max_tempo'] = 110
            time_desc = "Evening"
            
        # Night (8-11 PM): Relaxing, winding down
        elif 20 <= hour < 23:
            params['name'] = 'Night Relaxation'
            params['description'] = 'Calming music for your evening relaxation'
            params['seed_genres'] = ['chill', 'acoustic', 'sleep']
            params['target_energy'] = 0.3
            params['target_valence'] = 0.5
            params['min_tempo'] = 60
            params['max_tempo'] = 90
            time_desc = "Night"
            
        # Late night (11 PM-5 AM): Sleep, ambient
        else:
            params['name'] = 'Late Night Ambience'
            params['description'] = 'Ambient sounds for late night hours'
            params['seed_genres'] = ['ambient', 'sleep', 'classical']
            params['target_energy'] = 0.2
            params['target_valence'] = 0.4
            params['min_tempo'] = 50
            params['max_tempo'] = 80
            time_desc = "Late Night"
        
        # Weekend adjustments
        if is_weekend:
            # Weekends generally more relaxed/fun
            if hour < 10:  # Weekend mornings more relaxed
                params['target_energy'] = max(0.2, params['target_energy'] - 0.1)
                params['min_tempo'] = max(60, params['min_tempo'] - 10)
                params['max_tempo'] = max(90, params['max_tempo'] - 20)
                params['name'] = f"Weekend {params['name']}"
            elif 10 <= hour < 23:  # Daytime/evening more upbeat on weekends
                params['target_energy'] = min(0.9, params['target_energy'] + 0.1)
                params['target_valence'] = min(0.9, params['target_valence'] + 0.1)
                params['name'] = f"Weekend {params['name']}"
            
            time_desc = f"Weekend {time_desc}"
        
        return {
            'playlist_params': params,
            'time_description': time_desc
        }
    
    except Exception as e:
        logging.error(f"Error generating time-based playlist parameters: {str(e)}")
        return {
            'playlist_params': {
                'name': 'Default Time Playlist',
                'description': 'A playlist for any time',
                'seed_genres': ['pop', 'rock', 'indie'],
                'target_energy': 0.6,
                'target_valence': 0.6
            },
            'time_description': 'Current Time'
        }

def get_calendar_event_playlist_params(event_type=None, duration_minutes=60):
    """
    Generate Spotify playlist parameters based on calendar event type
    
    Args:
        event_type: String indicating event type ('workout', 'meeting', 'focus', etc.)
        duration_minutes: Duration of event in minutes (for playlist length)
        
    Returns:
        Dictionary with playlist parameters
    """
    try:
        # Default parameters
        params = {
            'name': 'Event Playlist',
            'description': 'Music for your calendar event',
            'seed_genres': ['pop'],
            'target_energy': 0.6,
            'target_valence': 0.6,
            'min_tempo': 100,
            'max_tempo': 130,
            'duration_minutes': min(180, max(30, duration_minutes))  # Limit between 30-180 minutes
        }
        
        # Determine track count based on duration (assuming ~3.5 min per track)
        track_count = max(5, min(50, int(params['duration_minutes'] / 3.5)))
        params['track_count'] = track_count
        
        if not event_type:
            return params
            
        event_type = event_type.lower()
        
        # Workout/exercise event
        if any(word in event_type for word in ['workout', 'exercise', 'gym', 'training', 'fitness']):
            params['name'] = 'Workout Session'
            params['description'] = f"{params['duration_minutes']} minute workout playlist"
            params['seed_genres'] = ['workout', 'electronic', 'power']
            params['target_energy'] = 0.9
            params['target_valence'] = 0.7
            params['min_tempo'] = 120
            params['max_tempo'] = 150
            
        # Focus/work/study event
        elif any(word in event_type for word in ['focus', 'work', 'study', 'concentration', 'deep']):
            params['name'] = 'Deep Focus Session'
            params['description'] = f"{params['duration_minutes']} minute concentration playlist"
            params['seed_genres'] = ['focus', 'ambient', 'study']
            params['target_energy'] = 0.4
            params['target_valence'] = 0.5
            params['min_tempo'] = 70
            params['max_tempo'] = 100
            params['target_instrumentalness'] = 0.7
            
        # Meditation/relaxation event
        elif any(word in event_type for word in ['meditation', 'relax', 'mindfulness', 'yoga']):
            params['name'] = 'Meditation & Mindfulness'
            params['description'] = f"{params['duration_minutes']} minute relaxation playlist"
            params['seed_genres'] = ['ambient', 'meditation', 'chill']
            params['target_energy'] = 0.2
            params['target_valence'] = 0.5
            params['min_tempo'] = 50
            params['max_tempo'] = 80
            params['target_instrumentalness'] = 0.8
            
        # Meeting/call event
        elif any(word in event_type for word in ['meeting', 'call', 'conference', 'interview']):
            params['name'] = 'Pre-Meeting Preparation'
            params['description'] = 'Calm focus music before your meeting'
            params['seed_genres'] = ['classical', 'ambient', 'instrumental']
            params['target_energy'] = 0.3
            params['target_valence'] = 0.6
            params['min_tempo'] = 60
            params['max_tempo'] = 90
            params['target_instrumentalness'] = 0.6
            
        # Commute event
        elif any(word in event_type for word in ['commute', 'travel', 'drive', 'train', 'bus']):
            params['name'] = 'Commute Companion'
            params['description'] = f"Music for your {params['duration_minutes']} minute journey"
            params['seed_genres'] = ['pop', 'indie', 'rock']
            params['target_energy'] = 0.7
            params['target_valence'] = 0.7
            params['min_tempo'] = 90
            params['max_tempo'] = 130
            
        # Social/party event
        elif any(word in event_type for word in ['party', 'celebration', 'social', 'dinner', 'drinks']):
            params['name'] = 'Social Gathering Mix'
            params['description'] = 'Upbeat music for your social event'
            params['seed_genres'] = ['party', 'pop', 'dance']
            params['target_energy'] = 0.8
            params['target_valence'] = 0.8
            params['min_tempo'] = 110
            params['max_tempo'] = 140
            
        # Cooking event
        elif any(word in event_type for word in ['cook', 'baking', 'kitchen', 'dinner']):
            params['name'] = 'Cooking Session Soundtrack'
            params['description'] = 'Perfect music for your time in the kitchen'
            params['seed_genres'] = ['jazz', 'soul', 'indie']
            params['target_energy'] = 0.6
            params['target_valence'] = 0.7
            params['min_tempo'] = 80
            params['max_tempo'] = 120
        
        return params
        
    except Exception as e:
        logging.error(f"Error generating event-based playlist parameters: {str(e)}")
        return {
            'name': 'Event Playlist',
            'description': 'Music for your event',
            'seed_genres': ['pop', 'rock', 'indie'],
            'target_energy': 0.6,
            'target_valence': 0.6,
            'duration_minutes': 60,
            'track_count': 15
        }

def create_calendar_event_playlist(spotify, event_type, duration_minutes=60, custom_name=None):
    """
    Create a Spotify playlist based on calendar event type
    
    Args:
        spotify: Authenticated Spotify client
        event_type: Type of calendar event
        duration_minutes: Duration of event in minutes
        custom_name: Optional custom name for the playlist
        
    Returns:
        String with result message
    """
    try:
        # Get playlist parameters based on event type
        params = get_calendar_event_playlist_params(event_type, duration_minutes)
        
        # Update name if provided
        if custom_name:
            params['name'] = custom_name
            
        # Import here to avoid circular imports
        from utils.spotify_helper import create_recommendations_playlist
        
        # Create the playlist
        playlist_result = create_recommendations_playlist(
            spotify, 
            params['name'], 
            f"Calendar event: {event_type}", 
            limit=params.get('track_count', 15),
            audio_features=params
        )
        
        return f"🎵 Created event playlist for {event_type} ({duration_minutes} minutes)\n{playlist_result}"
    
    except Exception as e:
        logging.error(f"Error creating event-based playlist: {str(e)}")
        return f"❌ Error creating event playlist: {str(e)}"

def create_time_based_playlist(spotify, custom_name=None, timezone=None):
    """
    Create a Spotify playlist based on current time of day
    
    Args:
        spotify: Authenticated Spotify client
        custom_name: Optional custom name for the playlist
        timezone: Optional timezone string
        
    Returns:
        String with result message
    """
    try:
        # Get playlist parameters based on time
        result = get_time_based_playlist_params(user_timezone=timezone)
        params = result['playlist_params']
        
        # Update name if provided
        if custom_name:
            params['name'] = custom_name
        
        # Import here to avoid circular imports
        from utils.spotify_helper import create_recommendations_playlist
        
        # Create the playlist
        seed_description = f"Time of day: {result['time_description']}"
        playlist_result = create_recommendations_playlist(
            spotify, 
            params['name'], 
            seed_description, 
            limit=20,
            audio_features=params
        )
        
        return f"🎵 Created time-based playlist for {result['time_description']}\n{playlist_result}"
    
    except Exception as e:
        logging.error(f"Error creating time-based playlist: {str(e)}")
        return f"❌ Error creating time-based playlist: {str(e)}"

def suggest_upcoming_event_playlists(spotify, google_events, days_ahead=7):
    """
    Suggest playlists for upcoming calendar events
    
    Args:
        spotify: Authenticated Spotify client
        google_events: List of Google Calendar events
        days_ahead: Number of days to look ahead
        
    Returns:
        String with suggestions
    """
    try:
        if not google_events:
            return "No upcoming events found in your calendar."
            
        now = datetime.datetime.now()
        max_time = now + datetime.timedelta(days=days_ahead)
        
        # Filter events to just the upcoming ones
        upcoming_events = []
        for event in google_events:
            try:
                start_time = parse_date(event.get('start', {}).get('dateTime', event.get('start', {}).get('date')))
                
                # Skip events without proper timing or past events
                if not start_time or start_time < now:
                    continue
                    
                # Skip events too far in the future
                if start_time > max_time:
                    continue
                
                # Calculate duration
                end_time = parse_date(event.get('end', {}).get('dateTime', event.get('end', {}).get('date')))
                if not end_time:
                    duration_minutes = 60  # Default to 60 minutes
                else:
                    duration_minutes = int((end_time - start_time).total_seconds() / 60)
                
                upcoming_events.append({
                    'summary': event.get('summary', 'Untitled Event'),
                    'start_time': start_time,
                    'duration_minutes': duration_minutes
                })
            except Exception as e:
                logging.error(f"Error processing event: {str(e)}")
                continue
        
        if not upcoming_events:
            return "No suitable upcoming events found for playlist suggestions."
            
        # Sort events by start time
        upcoming_events.sort(key=lambda x: x['start_time'])
        
        # Generate suggestions
        suggestions = "📅 Suggested playlists for your upcoming events:\n\n"
        
        for i, event in enumerate(upcoming_events[:5], 1):  # Limit to 5 suggestions
            event_type = event['summary'].lower()
            params = get_calendar_event_playlist_params(event_type, event['duration_minutes'])
            
            start_time_str = event['start_time'].strftime("%A, %I:%M %p")
            
            suggestions += f"{i}. \"{params['name']}\" for \"{event['summary']}\"\n"
            suggestions += f"   📅 {start_time_str}\n"
            suggestions += f"   🎵 {params['description']}\n\n"
            
        suggestions += "To create one of these playlists, use the command:\n"
        suggestions += "event playlist [event type] - [duration in minutes] - [optional custom name]"
        
        return suggestions
    
    except Exception as e:
        logging.error(f"Error suggesting event playlists: {str(e)}")
        return f"❌ Error generating playlist suggestions: {str(e)}"