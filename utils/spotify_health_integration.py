import logging
from datetime import datetime, timedelta
import random

def get_workout_playlist_params(workout_type, intensity, duration_minutes):
    """
    Generate Spotify playlist parameters based on workout type and intensity
    
    Args:
        workout_type: Type of workout (cardio, strength, yoga, etc.)
        intensity: Workout intensity level (1-10)
        duration_minutes: Workout duration in minutes
        
    Returns:
        Dictionary with playlist parameters
    """
    try:
        # Normalize intensity to 0-1 scale
        intensity_norm = max(0, min(10, intensity)) / 10
        
        # Default parameters
        params = {
            'name': 'Workout Playlist',
            'description': f'{duration_minutes} minute workout mix',
            'seed_genres': ['workout'],
            'target_energy': 0.7,
            'target_valence': 0.7,
            'min_tempo': 120,
            'max_tempo': 140,
            'duration_minutes': min(180, max(10, duration_minutes))
        }
        
        # Determine track count based on duration (assuming ~3 min per track)
        track_count = max(5, min(50, int(params['duration_minutes'] / 3)))
        params['track_count'] = track_count
        
        workout_type = workout_type.lower() if workout_type else 'general'
        
        # Cardio/Running/Cycling
        if any(word in workout_type for word in ['cardio', 'running', 'cycling', 'elliptical', 'treadmill']):
            params['name'] = f'{duration_minutes} Min Cardio Beat'
            params['description'] = f'High-energy tracks for your {workout_type} session'
            params['seed_genres'] = ['electronic', 'dance', 'edm']
            params['target_energy'] = 0.8 + (intensity_norm * 0.2)  # 0.8-1.0 based on intensity
            params['target_valence'] = 0.6 + (intensity_norm * 0.2)  # 0.6-0.8 based on intensity
            
            # Tempo increases with intensity
            base_tempo = 120 + (intensity_norm * 40)  # 120-160 based on intensity
            params['min_tempo'] = max(110, base_tempo - 10)
            params['max_tempo'] = min(180, base_tempo + 20)
            
        # Strength/Weight Training
        elif any(word in workout_type for word in ['strength', 'weight', 'lifting', 'resistance']):
            params['name'] = f'{duration_minutes} Min Strength Session'
            params['description'] = f'Powerful tracks for your {workout_type} workout'
            params['seed_genres'] = ['rock', 'metal', 'hip-hop']
            params['target_energy'] = 0.7 + (intensity_norm * 0.2)  # 0.7-0.9 based on intensity
            params['target_valence'] = 0.5 + (intensity_norm * 0.3)  # 0.5-0.8 based on intensity
            
            # More consistent tempo for strength training
            base_tempo = 100 + (intensity_norm * 30)  # 100-130 based on intensity
            params['min_tempo'] = max(90, base_tempo - 15)
            params['max_tempo'] = min(160, base_tempo + 15)
            
        # HIIT/Interval Training
        elif any(word in workout_type for word in ['hiit', 'interval', 'circuit']):
            params['name'] = f'{duration_minutes} Min HIIT Intensity'
            params['description'] = f'High-intensity interval training soundtrack'
            params['seed_genres'] = ['electronic', 'dance', 'drum-and-bass']
            params['target_energy'] = min(1.0, 0.85 + (intensity_norm * 0.15))  # 0.85-1.0
            params['target_valence'] = 0.7
            
            # Fast tempo for intervals
            base_tempo = 140 + (intensity_norm * 40)  # 140-180 based on intensity
            params['min_tempo'] = max(130, base_tempo - 10)
            params['max_tempo'] = min(200, base_tempo + 20)
            
        # Yoga/Pilates/Stretching
        elif any(word in workout_type for word in ['yoga', 'pilates', 'stretching', 'flexibility']):
            params['name'] = f'{duration_minutes} Min Flow Session'
            params['description'] = f'Mindful music for your {workout_type} practice'
            params['seed_genres'] = ['ambient', 'chill', 'instrumental']
            params['target_energy'] = 0.3 + (intensity_norm * 0.3)  # 0.3-0.6 based on intensity
            params['target_valence'] = 0.5 + (intensity_norm * 0.2)  # 0.5-0.7 based on intensity
            
            # Slower, consistent tempo for flow
            base_tempo = 70 + (intensity_norm * 30)  # 70-100 based on intensity
            params['min_tempo'] = max(60, base_tempo - 10)
            params['max_tempo'] = min(120, base_tempo + 10)
            params['target_instrumentalness'] = 0.7
            
        # Walking/Light Activity
        elif any(word in workout_type for word in ['walk', 'stroll', 'light']):
            params['name'] = f'{duration_minutes} Min Walking Companion'
            params['description'] = f'Perfect soundtrack for your {workout_type}'
            params['seed_genres'] = ['pop', 'indie', 'folk']
            params['target_energy'] = 0.5 + (intensity_norm * 0.2)  # 0.5-0.7 based on intensity
            params['target_valence'] = 0.6 + (intensity_norm * 0.2)  # 0.6-0.8 based on intensity
            
            # Moderate tempo for walking
            base_tempo = 90 + (intensity_norm * 20)  # 90-110 based on intensity
            params['min_tempo'] = max(80, base_tempo - 10)
            params['max_tempo'] = min(130, base_tempo + 10)
            
        # Cooldown/Recovery
        elif any(word in workout_type for word in ['cooldown', 'recovery', 'cool down', 'cool-down']):
            params['name'] = 'Post-Workout Cooldown'
            params['description'] = 'Relaxing tracks to help your body recover'
            params['seed_genres'] = ['chill', 'ambient', 'acoustic']
            params['target_energy'] = 0.3
            params['target_valence'] = 0.6
            params['min_tempo'] = 60
            params['max_tempo'] = 90
            
        # Custom adjustment for very short workouts
        if duration_minutes < 20:
            # Higher energy for short, likely intense workouts
            params['target_energy'] = min(1.0, params['target_energy'] + 0.1)
            
        # Custom adjustment for longer workouts
        if duration_minutes > 60:
            # More varied energy for longer sessions to prevent fatigue
            params['target_energy'] = max(0.5, params['target_energy'] - 0.05)
            
        return params
        
    except Exception as e:
        logging.error(f"Error generating workout playlist parameters: {str(e)}")
        return {
            'name': 'Workout Mix',
            'description': 'Music for your exercise session',
            'seed_genres': ['workout', 'pop', 'rock'],
            'target_energy': 0.8,
            'target_valence': 0.7,
            'min_tempo': 120,
            'max_tempo': 140,
            'duration_minutes': 30,
            'track_count': 10
        }

def get_recovery_playlist_params(recovery_type, pain_level=0):
    """
    Generate Spotify playlist parameters for recovery or pain management
    
    Args:
        recovery_type: Type of recovery (sleep, meditation, pain relief, etc.)
        pain_level: Pain level (0-10)
        
    Returns:
        Dictionary with playlist parameters
    """
    try:
        # Normalize pain level to 0-1 scale
        pain_norm = max(0, min(10, pain_level)) / 10
        
        # Default parameters
        params = {
            'name': 'Recovery Playlist',
            'description': 'Music to help you recover',
            'seed_genres': ['ambient'],
            'target_energy': 0.3,
            'target_valence': 0.5,
            'min_tempo': 60,
            'max_tempo': 80,
        }
        
        recovery_type = recovery_type.lower() if recovery_type else 'general'
        
        # Sleep/Insomnia
        if any(word in recovery_type for word in ['sleep', 'insomnia', 'bedtime']):
            params['name'] = 'Deep Sleep Aid'
            params['description'] = 'Gentle sounds to help you fall asleep'
            params['seed_genres'] = ['sleep', 'ambient', 'classical']
            params['target_energy'] = 0.1
            params['target_valence'] = 0.4
            params['min_tempo'] = 40
            params['max_tempo'] = 70
            params['target_instrumentalness'] = 0.8
            params['target_acousticness'] = 0.7
            
        # Meditation/Mindfulness
        elif any(word in recovery_type for word in ['meditation', 'mindfulness', 'breathing']):
            params['name'] = 'Meditation Soundscape'
            params['description'] = 'Ambient sounds for meditation and mindfulness'
            params['seed_genres'] = ['ambient', 'world', 'new-age']
            params['target_energy'] = 0.2
            params['target_valence'] = 0.5
            params['min_tempo'] = 50
            params['max_tempo'] = 70
            params['target_instrumentalness'] = 0.9
            
        # Pain Relief (adjusts based on pain level)
        elif any(word in recovery_type for word in ['pain', 'relief', 'chronic']):
            params['name'] = 'Pain Relief Sounds'
            params['description'] = 'Music designed to help manage pain'
            params['seed_genres'] = ['ambient', 'classical', 'piano']
            
            # Higher pain = lower tempo, lower energy
            pain_energy = 0.4 - (pain_norm * 0.2)  # 0.4 to 0.2 based on pain
            pain_tempo = 70 - (pain_norm * 20)  # 70 to 50 based on pain
            
            params['target_energy'] = max(0.1, pain_energy)
            params['target_valence'] = 0.5
            params['min_tempo'] = max(40, pain_tempo - 10)
            params['max_tempo'] = min(90, pain_tempo + 10)
            params['target_instrumentalness'] = 0.7
            params['target_acousticness'] = 0.8
            
        # Stress Relief/Anxiety
        elif any(word in recovery_type for word in ['stress', 'anxiety', 'relax', 'calm']):
            params['name'] = 'Stress Reduction'
            params['description'] = 'Calming music to reduce stress and anxiety'
            params['seed_genres'] = ['chill', 'ambient', 'study']
            params['target_energy'] = 0.3
            params['target_valence'] = 0.6
            params['min_tempo'] = 60
            params['max_tempo'] = 80
            params['target_acousticness'] = 0.7
            
        # Physical Recovery/Muscle Relaxation
        elif any(word in recovery_type for word in ['muscle', 'physical', 'recovery', 'soreness']):
            params['name'] = 'Muscle Recovery'
            params['description'] = 'Soothing sounds for physical recovery'
            params['seed_genres'] = ['ambient', 'classical', 'instrumental']
            params['target_energy'] = 0.3
            params['target_valence'] = 0.5
            params['min_tempo'] = 60
            params['max_tempo'] = 90
            
        # Mental Health/Mood
        elif any(word in recovery_type for word in ['mental', 'mood', 'depression', 'therapy']):
            params['name'] = 'Mood Elevation'
            params['description'] = 'Music to gently elevate your mood'
            params['seed_genres'] = ['feel-good', 'indie', 'folk']
            params['target_energy'] = 0.4
            params['target_valence'] = 0.7
            params['min_tempo'] = 70
            params['max_tempo'] = 100
            
        return params
        
    except Exception as e:
        logging.error(f"Error generating recovery playlist parameters: {str(e)}")
        return {
            'name': 'Recovery Playlist',
            'description': 'Soothing music for recovery',
            'seed_genres': ['ambient', 'classical', 'chill'],
            'target_energy': 0.3,
            'target_valence': 0.5,
            'min_tempo': 60,
            'max_tempo': 80
        }

def create_workout_playlist(spotify, workout_type, intensity=7, duration_minutes=30, custom_name=None):
    """
    Create a Spotify playlist based on workout type and intensity
    
    Args:
        spotify: Authenticated Spotify client
        workout_type: Type of workout
        intensity: Intensity level (1-10)
        duration_minutes: Workout duration in minutes
        custom_name: Optional custom name for the playlist
        
    Returns:
        String with result message
    """
    try:
        # Get playlist parameters based on workout
        params = get_workout_playlist_params(workout_type, intensity, duration_minutes)
        
        # Update name if provided
        if custom_name:
            params['name'] = custom_name
            
        # Import here to avoid circular imports
        from utils.spotify_helper import create_recommendations_playlist
        
        # Create the playlist
        playlist_result = create_recommendations_playlist(
            spotify, 
            params['name'], 
            f"Workout: {workout_type} (Intensity: {intensity}/10)", 
            limit=params.get('track_count', 15),
            audio_features=params
        )
        
        return f"🏋️ Created workout playlist for {workout_type} ({duration_minutes} minutes)\n{playlist_result}"
    
    except Exception as e:
        logging.error(f"Error creating workout playlist: {str(e)}")
        return f"❌ Error creating workout playlist: {str(e)}"

def create_recovery_playlist(spotify, recovery_type, pain_level=0, custom_name=None):
    """
    Create a Spotify playlist for recovery or pain management
    
    Args:
        spotify: Authenticated Spotify client
        recovery_type: Type of recovery
        pain_level: Pain level (0-10)
        custom_name: Optional custom name for the playlist
        
    Returns:
        String with result message
    """
    try:
        # Get playlist parameters based on recovery type
        params = get_recovery_playlist_params(recovery_type, pain_level)
        
        # Update name if provided
        if custom_name:
            params['name'] = custom_name
            
        # Import here to avoid circular imports
        from utils.spotify_helper import create_recommendations_playlist
        
        # Create the playlist
        pain_info = f" (Pain Level: {pain_level}/10)" if pain_level > 0 else ""
        playlist_result = create_recommendations_playlist(
            spotify, 
            params['name'], 
            f"Recovery: {recovery_type}{pain_info}", 
            limit=20,
            audio_features=params
        )
        
        return f"🧘 Created recovery playlist for {recovery_type}\n{playlist_result}"
    
    except Exception as e:
        logging.error(f"Error creating recovery playlist: {str(e)}")
        return f"❌ Error creating recovery playlist: {str(e)}"

def generate_weekly_health_music_plan(spotify, health_data):
    """
    Generate a weekly music plan based on health data
    
    Args:
        spotify: Authenticated Spotify client
        health_data: Dictionary with health metrics
        
    Returns:
        String with weekly plan
    """
    try:
        if not health_data:
            return "Health data not available to generate a music plan."
        
        # Extract health metrics
        workouts = health_data.get('workouts', [])
        sleep_quality = health_data.get('sleep_quality', 5)  # 1-10 scale
        stress_level = health_data.get('stress_level', 5)  # 1-10 scale
        pain_level = health_data.get('pain_level', 0)  # 0-10 scale
        
        today = datetime.now()
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        plan = "📅 Your Personal Health Music Plan for This Week:\n\n"
        
        # Generate plan for each day
        for i in range(7):
            day = (today + timedelta(days=i)).weekday()
            day_name = days_of_week[day]
            
            # Determine if this is a workout day
            is_workout_day = False
            workout_type = None
            
            for workout in workouts:
                if workout.get('day_of_week', -1) == day:
                    is_workout_day = True
                    workout_type = workout.get('type', 'general')
                    break
            
            plan += f"🔹 {day_name}:\n"
            
            if is_workout_day:
                intensity = workout.get('intensity', 7)
                duration = workout.get('duration_minutes', 30)
                workout_params = get_workout_playlist_params(workout_type, intensity, duration)
                
                plan += f"   🏋️ Workout: {workout_type.title()} ({duration} min)\n"
                plan += f"   🎵 Suggested playlist: \"{workout_params['name']}\"\n"
                
                # Add recovery for harder workouts
                if intensity > 7:
                    recovery_params = get_recovery_playlist_params('muscle recovery')
                    plan += f"   🧘 Post-workout: \"{recovery_params['name']}\"\n"
            else:
                # Non-workout day suggestions
                if day in [5, 6]:  # Weekend
                    from utils.spotify_calendar_integration import get_time_based_playlist_params
                    time_params = get_time_based_playlist_params()
                    plan += f"   🎧 Relaxation: \"{time_params['playlist_params']['name']}\"\n"
                else:  # Weekday
                    from utils.spotify_weather_integration import get_mood_based_on_weather
                    mood, _ = get_mood_based_on_weather()
                    plan += f"   🌤️ Mood suggestion: Music for \"{mood}\" listening\n"
            
            # Add evening recommendation based on sleep quality
            if sleep_quality < 5:
                sleep_params = get_recovery_playlist_params('sleep')
                plan += f"   😴 Evening: \"{sleep_params['name']}\"\n"
            
            # Add stress management if needed
            if stress_level > 7:
                stress_params = get_recovery_playlist_params('stress')
                plan += f"   😌 Stress relief: \"{stress_params['name']}\"\n"
                
            # Add pain management if needed
            if pain_level > 5:
                pain_params = get_recovery_playlist_params('pain', pain_level)
                plan += f"   🩹 Pain management: \"{pain_params['name']}\"\n"
                
            plan += "\n"
        
        # Add general tips
        plan += "💡 Tips for using music for health:\n"
        plan += "• Morning: Energizing music to get your day started\n"
        plan += "• Workouts: Match tempo with your activity intensity\n"
        plan += "• Recovery: Slower tempos help reduce heart rate\n"
        plan += "• Sleep: Listen to calming music 30 minutes before bed\n\n"
        
        plan += "To create any of these playlists, use commands like:\n"
        plan += "• workout playlist [type] - [intensity] - [duration]\n"
        plan += "• recovery playlist [type] - [pain level]\n"
        plan += "• sleep playlist\n"
        
        return plan
    
    except Exception as e:
        logging.error(f"Error generating health music plan: {str(e)}")
        return f"❌ Error generating health music plan: {str(e)}"