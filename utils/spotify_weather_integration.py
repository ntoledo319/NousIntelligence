import logging
from utils.weather_helper import get_current_weather, get_location_coordinates

def get_weather_based_playlist_params(weather_data):
    """
    Generate Spotify playlist parameters based on current weather conditions
    
    Args:
        weather_data: Dictionary containing weather information
        
    Returns:
        Dictionary with playlist parameters and weather description
    """
    try:
        # Extract relevant weather information
        temp_c = weather_data.get('temp_c')
        condition = weather_data.get('condition', {}).get('text', '').lower()
        is_day = weather_data.get('is_day', 1) == 1
        
        # Default parameters (medium energy, medium tempo)
        params = {
            'name': 'Weather-Inspired Playlist',
            'description': 'Music to match your weather',
            'seed_genres': ['pop'],
            'target_energy': 0.5,
            'target_valence': 0.5,
            'min_tempo': 90,
            'max_tempo': 130
        }
        
        # Adjust based on temperature
        if temp_c is not None:
            # Cold weather (below 10°C) - more acoustic, slightly less energy
            if temp_c < 10:
                params['target_energy'] = 0.4
                params['target_acousticness'] = 0.6
                params['min_tempo'] = 70
                params['max_tempo'] = 110
                params['name'] = 'Cold Weather Comfort'
                params['description'] = 'Warm, comforting tracks for cold weather'
                params['seed_genres'] = ['acoustic', 'indie', 'folk']
                
            # Cool weather (10-18°C) - balanced
            elif temp_c < 18:
                params['target_energy'] = 0.5
                params['target_valence'] = 0.6
                params['min_tempo'] = 85
                params['max_tempo'] = 120
                params['name'] = 'Cool Weather Vibes'
                params['description'] = 'Perfect tracks for cool, pleasant weather'
                params['seed_genres'] = ['indie', 'pop', 'alternative']
                
            # Warm weather (18-25°C) - upbeat, positive
            elif temp_c < 25:
                params['target_energy'] = 0.7
                params['target_valence'] = 0.8
                params['min_tempo'] = 100
                params['max_tempo'] = 130
                params['name'] = 'Sunny Day Soundtrack'
                params['description'] = 'Upbeat tracks for warm, sunny weather'
                params['seed_genres'] = ['pop', 'dance', 'tropical']
                
            # Hot weather (above 25°C) - energetic, summer vibes
            else:
                params['target_energy'] = 0.8
                params['target_valence'] = 0.8
                params['min_tempo'] = 110
                params['max_tempo'] = 140
                params['name'] = 'Summer Heat Beats'
                params['description'] = 'High-energy tracks for hot weather'
                params['seed_genres'] = ['dance', 'electronic', 'reggae']
        
        # Adjust based on conditions
        if condition:
            # Rainy conditions
            if any(word in condition for word in ['rain', 'drizzle', 'shower']):
                params['target_energy'] = max(0.3, params['target_energy'] - 0.2)
                params['target_acousticness'] = min(0.8, params.get('target_acousticness', 0.4) + 0.3)
                params['min_tempo'] = max(60, params['min_tempo'] - 15)
                params['max_tempo'] = max(100, params['max_tempo'] - 20)
                params['name'] = 'Rainy Day Melodies'
                params['description'] = 'Soothing tracks for rainy weather'
                params['seed_genres'] = ['chill', 'ambient', 'study']
                
            # Stormy conditions
            elif any(word in condition for word in ['storm', 'thunder', 'lightning']):
                params['target_energy'] = 0.7
                params['target_valence'] = 0.4
                params['min_tempo'] = 80
                params['max_tempo'] = 140
                params['name'] = 'Storm Intensity'
                params['description'] = 'Dramatic tracks for stormy weather'
                params['seed_genres'] = ['rock', 'epic', 'classical']
                
            # Cloudy conditions
            elif any(word in condition for word in ['cloud', 'overcast']):
                params['target_energy'] = 0.5
                params['target_valence'] = 0.5
                params['name'] = 'Cloudy Day Contemplation'
                params['description'] = 'Thoughtful tracks for cloudy weather'
                params['seed_genres'] = ['indie', 'alternative', 'chill']
                
            # Foggy/misty conditions
            elif any(word in condition for word in ['fog', 'mist']):
                params['target_energy'] = 0.4
                params['target_acousticness'] = 0.7
                params['target_valence'] = 0.4
                params['min_tempo'] = 70
                params['max_tempo'] = 100
                params['name'] = 'Foggy Morning Atmosphere'
                params['description'] = 'Atmospheric tracks for foggy weather'
                params['seed_genres'] = ['ambient', 'chill', 'instrumental']
                
            # Snowy conditions
            elif any(word in condition for word in ['snow', 'blizzard', 'flurry']):
                params['target_energy'] = 0.4
                params['target_acousticness'] = 0.6
                params['target_valence'] = 0.6
                params['min_tempo'] = 70
                params['max_tempo'] = 110
                params['name'] = 'Winter Wonderland'
                params['description'] = 'Cozy tracks for snowy weather'
                params['seed_genres'] = ['indie', 'folk', 'acoustic']
                
            # Clear conditions
            elif any(word in condition for word in ['clear', 'sunny']):
                params['target_energy'] = 0.7
                params['target_valence'] = 0.8
                params['min_tempo'] = 100
                params['max_tempo'] = 130
                params['name'] = 'Sunshine Melodies'
                params['description'] = 'Uplifting tracks for clear skies'
                params['seed_genres'] = ['pop', 'happy', 'summer']
        
        # Adjust based on day/night
        if not is_day:
            # Nighttime - slightly lower energy, more atmospheric
            params['target_energy'] = max(0.2, params['target_energy'] - 0.1)
            params['target_valence'] = max(0.3, params.get('target_valence', 0.5) - 0.1)
            params['name'] = f"Night {params['name']}"
            params['description'] = f"Nighttime {params['description'].lower()}"
            
            # Add nighttime genres
            night_genres = ['chill', 'electronic', 'ambient']
            for genre in night_genres:
                if genre not in params['seed_genres']:
                    params['seed_genres'].append(genre)
                    if len(params['seed_genres']) > 5:  # Spotify API limits to 5 seed genres
                        params['seed_genres'] = params['seed_genres'][:5]
                        break
        
        return {
            'playlist_params': params,
            'weather_description': f"{condition.capitalize()}, {temp_c}°C, {'Day' if is_day else 'Night'}"
        }
    
    except Exception as e:
        logging.error(f"Error generating weather-based playlist parameters: {str(e)}")
        return {
            'playlist_params': {
                'name': 'Default Weather Playlist',
                'description': 'A playlist for any weather',
                'seed_genres': ['pop', 'rock', 'indie'],
                'target_energy': 0.6,
                'target_valence': 0.6
            },
            'weather_description': 'Weather data unavailable'
        }

def get_mood_based_on_weather(location=None):
    """
    Get current weather and determine appropriate musical mood
    
    Args:
        location: Optional location string (city, zip, etc.)
        
    Returns:
        Tuple of (mood_description, weather_description)
    """
    try:
        # Get location coordinates
        if location:
            coords = get_location_coordinates(location)
            if not coords:
                return "balanced", "Location not found"
            
            lat, lon = coords
        else:
            # Default to no coordinates
            lat, lon = None, None
        
        # Get current weather
        weather_data = get_current_weather(lat, lon)
        if not weather_data:
            return "balanced", "Weather data unavailable"
        
        # Get playlist parameters based on weather
        result = get_weather_based_playlist_params(weather_data)
        
        # Extract mood from parameters
        params = result['playlist_params']
        
        # Determine overall mood based on energy and valence
        energy = params.get('target_energy', 0.5)
        valence = params.get('target_valence', 0.5)
        
        if energy > 0.7 and valence > 0.7:
            mood = "energetic and upbeat"
        elif energy > 0.6 and valence > 0.6:
            mood = "positive and lively"
        elif energy < 0.4 and valence < 0.4:
            mood = "mellow and introspective"
        elif energy < 0.4 and valence > 0.6:
            mood = "relaxed and positive"
        elif energy > 0.6 and valence < 0.4:
            mood = "energetic but serious"
        else:
            mood = "balanced"
            
        return mood, result['weather_description']
    
    except Exception as e:
        logging.error(f"Error determining weather-based mood: {str(e)}")
        return "balanced", "Error processing weather data"

def create_weather_based_playlist(spotify, location=None, custom_name=None):
    """
    Create a Spotify playlist based on current weather conditions
    
    Args:
        spotify: Authenticated Spotify client
        location: Optional location string (city, zip, etc.)
        custom_name: Optional custom name for the playlist
        
    Returns:
        String with result message
    """
    try:
        # Get location coordinates
        if location:
            coords = get_location_coordinates(location)
            if not coords:
                return "❌ Location not found. Please try a different location."
            
            lat, lon = coords
        else:
            # Default to no coordinates
            lat, lon = None, None
        
        # Get current weather
        weather_data = get_current_weather(lat, lon)
        if not weather_data:
            return "❌ Unable to get weather data. Please try again later."
        
        # Get playlist parameters based on weather
        result = get_weather_based_playlist_params(weather_data)
        params = result['playlist_params']
        
        # Update name if provided
        if custom_name:
            params['name'] = custom_name
        
        # Import here to avoid circular imports
        from utils.spotify_helper import create_recommendations_playlist
        
        # Create the playlist
        seed_description = f"Weather-inspired ({result['weather_description']})"
        playlist_result = create_recommendations_playlist(
            spotify, 
            params['name'], 
            seed_description, 
            limit=25,
            audio_features=params
        )
        
        return f"🎵 Created weather-inspired playlist based on: {result['weather_description']}\n{playlist_result}"
    
    except Exception as e:
        logging.error(f"Error creating weather-based playlist: {str(e)}")
        return f"❌ Error creating weather-based playlist: {str(e)}"