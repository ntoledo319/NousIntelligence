import logging
import json
import random
import os
from datetime import datetime

# Get API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def analyze_text_for_music_parameters(text_input):
    """
    Analyze text input to determine music parameters using OpenAI
    
    Args:
        text_input: User's text input about their mood, preferences, etc.
        
    Returns:
        Dictionary with music parameters
    """
    try:
        if not OPENAI_API_KEY:
            logging.warning("OpenAI API key not available for music analysis")
            return default_music_parameters(text_input)
            
        # Import OpenAI here to avoid circular imports
        from openai import OpenAI
        
        # Initialize OpenAI client
        openai = OpenAI(api_key=OPENAI_API_KEY)
        
        # Prompt to analyze text for music features
        prompt = f"""
        Analyze the following text and extract music parameters that would match the mood, context, or request.
        Input text: "{text_input}"
        
        Return a JSON object with these parameters:
        - name: A creative and personalized playlist name
        - description: A brief description of the playlist
        - seed_genres: An array of 1-5 music genres that would match (use exact Spotify genre names)
        - target_energy: A value from 0.0 to 1.0 representing the energy level
        - target_valence: A value from 0.0 to 1.0 representing the musical positivity
        - target_danceability: A value from 0.0 to 1.0 representing how danceable
        - mood_keywords: An array of 3-5 mood keywords extracted from the text
        - min_tempo: A minimum tempo (BPM) value appropriate for the mood
        - max_tempo: A maximum tempo (BPM) value appropriate for the mood
        - musical_attributes: A short text describing what musical qualities should be present
        
        Ensure all numeric values are appropriate for the expressed mood or context.
        """
        
        # Call OpenAI API
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a musical analysis expert that helps translate human emotions and contexts into Spotify musical parameters."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        # Process response
        result = json.loads(response.choices[0].message.content)
        
        # Ensure all expected fields are present with reasonable values
        validated_result = {
            'name': result.get('name', f"Playlist for: {text_input[:30]}..."),
            'description': result.get('description', f"Music based on: {text_input[:50]}..."),
            'seed_genres': result.get('seed_genres', ['pop', 'rock']),
            'target_energy': max(0.0, min(1.0, result.get('target_energy', 0.5))),
            'target_valence': max(0.0, min(1.0, result.get('target_valence', 0.5))),
            'target_danceability': max(0.0, min(1.0, result.get('target_danceability', 0.5))),
            'mood_keywords': result.get('mood_keywords', ['balanced', 'neutral']),
            'min_tempo': max(40, min(200, result.get('min_tempo', 90))),
            'max_tempo': max(40, min(200, max(result.get('min_tempo', 90) + 10, result.get('max_tempo', 130)))),
            'musical_attributes': result.get('musical_attributes', 'Balanced mix of different musical elements'),
        }
        
        return validated_result
        
    except Exception as e:
        logging.error(f"Error analyzing text for music parameters: {str(e)}")
        return default_music_parameters(text_input)

def default_music_parameters(text_input):
    """
    Generate default music parameters based on simple keyword matching
    when AI analysis is not available
    
    Args:
        text_input: User's text input
        
    Returns:
        Dictionary with default music parameters
    """
    # Convert input to lowercase for easier matching
    text = text_input.lower()
    
    # Default parameters
    params = {
        'name': f"Playlist for: {text_input[:30]}...",
        'description': f"Music based on your mood and preferences",
        'seed_genres': ['pop', 'rock'],
        'target_energy': 0.6,
        'target_valence': 0.6,
        'target_danceability': 0.5,
        'mood_keywords': ['balanced', 'neutral'],
        'min_tempo': 90,
        'max_tempo': 130,
        'musical_attributes': 'Balanced mix of different musical elements',
    }
    
    # Check for happy/positive keywords
    if any(word in text for word in ['happy', 'joy', 'excited', 'upbeat', 'energetic', 'positive']):
        params['name'] = "Happy Vibes"
        params['description'] = "Upbeat and joyful tracks to boost your mood"
        params['seed_genres'] = ['happy', 'pop', 'dance']
        params['target_energy'] = 0.8
        params['target_valence'] = 0.8
        params['target_danceability'] = 0.7
        params['mood_keywords'] = ['happy', 'joyful', 'upbeat', 'energetic', 'positive']
        params['min_tempo'] = 110
        params['max_tempo'] = 140
        params['musical_attributes'] = 'Bright major keys, upbeat rhythms, cheerful melodies'
    
    # Check for sad/melancholy keywords
    elif any(word in text for word in ['sad', 'melancholy', 'depressed', 'heartbreak', 'lonely', 'blue']):
        params['name'] = "Melancholy Moments"
        params['description'] = "Reflective tracks for when you're feeling down"
        params['seed_genres'] = ['sad', 'indie', 'acoustic']
        params['target_energy'] = 0.4
        params['target_valence'] = 0.3
        params['target_danceability'] = 0.4
        params['mood_keywords'] = ['sad', 'melancholy', 'reflective', 'emotional', 'pensive']
        params['min_tempo'] = 60
        params['max_tempo'] = 100
        params['musical_attributes'] = 'Minor keys, emotional vocals, introspective lyrics'
    
    # Check for relaxed/chill keywords
    elif any(word in text for word in ['relax', 'chill', 'calm', 'peace', 'tranquil', 'mellow']):
        params['name'] = "Chill Session"
        params['description'] = "Relaxing tracks to help you unwind"
        params['seed_genres'] = ['chill', 'ambient', 'study']
        params['target_energy'] = 0.3
        params['target_valence'] = 0.5
        params['target_danceability'] = 0.3
        params['mood_keywords'] = ['relaxed', 'calm', 'chill', 'peaceful', 'tranquil']
        params['min_tempo'] = 60
        params['max_tempo'] = 90
        params['musical_attributes'] = 'Soft instrumentation, gentle rhythms, atmospheric sounds'
    
    # Check for focused/productive keywords
    elif any(word in text for word in ['focus', 'concentrate', 'study', 'work', 'productive']):
        params['name'] = "Deep Focus"
        params['description'] = "Music to help you concentrate and be productive"
        params['seed_genres'] = ['focus', 'study', 'ambient']
        params['target_energy'] = 0.5
        params['target_valence'] = 0.5
        params['target_danceability'] = 0.2
        params['target_instrumentalness'] = 0.7
        params['mood_keywords'] = ['focused', 'concentration', 'productive', 'flow', 'clarity']
        params['min_tempo'] = 70
        params['max_tempo'] = 110
        params['musical_attributes'] = 'Minimal distractions, consistent rhythms, often instrumental'
    
    # Check for party/dance keywords
    elif any(word in text for word in ['party', 'dance', 'club', 'fun', 'celebration']):
        params['name'] = "Party Time"
        params['description'] = "High-energy tracks to get the party started"
        params['seed_genres'] = ['party', 'dance', 'electronic']
        params['target_energy'] = 0.9
        params['target_valence'] = 0.7
        params['target_danceability'] = 0.8
        params['mood_keywords'] = ['party', 'dance', 'energetic', 'celebration', 'fun']
        params['min_tempo'] = 115
        params['max_tempo'] = 160
        params['musical_attributes'] = 'Strong beats, catchy hooks, driving rhythms'
    
    # Check for workout/exercise keywords
    elif any(word in text for word in ['workout', 'exercise', 'gym', 'run', 'fitness']):
        params['name'] = "Workout Power"
        params['description'] = "Energizing tracks to power your exercise session"
        params['seed_genres'] = ['workout', 'electronic', 'rock']
        params['target_energy'] = 0.9
        params['target_valence'] = 0.6
        params['target_danceability'] = 0.7
        params['mood_keywords'] = ['energetic', 'powerful', 'motivating', 'intense', 'driving']
        params['min_tempo'] = 120
        params['max_tempo'] = 160
        params['musical_attributes'] = 'Strong beats, motivational, high intensity'
    
    # Check for romantic/love keywords
    elif any(word in text for word in ['love', 'romantic', 'romance', 'date', 'intimate']):
        params['name'] = "Romantic Moments"
        params['description'] = "Intimate and romantic tracks for special moments"
        params['seed_genres'] = ['romance', 'r-n-b', 'jazz']
        params['target_energy'] = 0.5
        params['target_valence'] = 0.6
        params['target_danceability'] = 0.5
        params['mood_keywords'] = ['romantic', 'intimate', 'emotional', 'love', 'passionate']
        params['min_tempo'] = 70
        params['max_tempo'] = 110
        params['musical_attributes'] = 'Emotional vocals, intimate instrumentation, romantic themes'
    
    return params

def generate_ai_playlist(spotify, user_input, custom_name=None):
    """
    Create a Spotify playlist based on AI analysis of user text input
    
    Args:
        spotify: Authenticated Spotify client
        user_input: User's text describing their mood, preferences, etc.
        custom_name: Optional custom name for the playlist
        
    Returns:
        String with result message
    """
    try:
        # Get music parameters based on text analysis
        params = analyze_text_for_music_parameters(user_input)
        
        # Update name if provided
        if custom_name:
            params['name'] = custom_name
            
        # Import here to avoid circular imports
        from utils.spotify_helper import create_recommendations_playlist
        
        # Extract seed genres (max 5 for Spotify API)
        seed_genres = params.get('seed_genres', ['pop'])[:5]
        
        # Extract other parameters as audio features
        audio_features = {
            'target_energy': params.get('target_energy', 0.5),
            'target_valence': params.get('target_valence', 0.5),
            'target_danceability': params.get('target_danceability', 0.5),
            'min_tempo': params.get('min_tempo', 90),
            'max_tempo': params.get('max_tempo', 130)
        }
        
        # If any other target features are specified, add them
        for key, value in params.items():
            if key.startswith('target_') and key not in audio_features:
                audio_features[key] = value
        
        # Create the playlist
        playlist_result = create_recommendations_playlist(
            spotify, 
            params['name'], 
            f"AI-generated based on: {user_input[:50]}...", 
            limit=25,
            seed_genres=seed_genres,
            audio_features=audio_features
        )
        
        mood_keywords = ", ".join(params.get('mood_keywords', ['balanced']))
        attributes = params.get('musical_attributes', 'Balanced music')
        
        return f"🎵 Created AI-generated playlist based on your input\n\n"\
               f"Mood detected: {mood_keywords}\n"\
               f"Musical qualities: {attributes}\n\n"\
               f"{playlist_result}"
    
    except Exception as e:
        logging.error(f"Error creating AI-generated playlist: {str(e)}")
        return f"❌ Error creating AI-generated playlist: {str(e)}"

def analyze_listening_history(spotify, time_range='medium_term'):
    """
    Analyze user's listening history to generate insights and recommendations
    
    Args:
        spotify: Authenticated Spotify client
        time_range: Time range to analyze ('short_term', 'medium_term', 'long_term')
        
    Returns:
        Dictionary with analysis results
    """
    try:
        results = {
            'top_genres': [],
            'audio_feature_averages': {},
            'listening_personality': '',
            'recommendations': []
        }
        
        # 1. Get top artists and extract genres
        top_artists = spotify.current_user_top_artists(limit=50, time_range=time_range)
        
        all_genres = []
        for artist in top_artists['items']:
            all_genres.extend(artist.get('genres', []))
            
        # Count genres and get top ones
        from collections import Counter
        genre_counts = Counter(all_genres)
        results['top_genres'] = [genre for genre, _ in genre_counts.most_common(10)]
        
        # 2. Get top tracks and analyze audio features
        top_tracks = spotify.current_user_top_tracks(limit=50, time_range=time_range)
        if not top_tracks['items']:
            return results
            
        # Extract track IDs
        track_ids = [track['id'] for track in top_tracks['items']]
        
        # Get audio features in batches (Spotify API limit)
        all_features = []
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            features = spotify.audio_features(batch)
            all_features.extend([f for f in features if f])
        
        if not all_features:
            return results
            
        # Calculate averages for key audio features
        feature_keys = ['danceability', 'energy', 'valence', 'tempo', 
                        'acousticness', 'instrumentalness', 'liveness']
        
        for key in feature_keys:
            values = [track[key] for track in all_features if key in track]
            if values:
                results['audio_feature_averages'][key] = sum(values) / len(values)
        
        # 3. Determine listening personality based on features
        try:
            energy = results['audio_feature_averages'].get('energy', 0.5)
            valence = results['audio_feature_averages'].get('valence', 0.5)
            danceability = results['audio_feature_averages'].get('danceability', 0.5)
            acousticness = results['audio_feature_averages'].get('acousticness', 0.5)
            
            personality_traits = []
            
            if energy > 0.7:
                personality_traits.append("Energetic Listener")
            elif energy < 0.4:
                personality_traits.append("Relaxed Listener")
                
            if valence > 0.7:
                personality_traits.append("Positive Mood Seeker")
            elif valence < 0.4:
                personality_traits.append("Emotional Depth Explorer")
                
            if danceability > 0.7:
                personality_traits.append("Rhythm Enthusiast")
                
            if acousticness > 0.7:
                personality_traits.append("Acoustic Appreciator")
            elif acousticness < 0.3:
                personality_traits.append("Electronic Music Fan")
                
            # Main personality type
            if energy > 0.65 and valence > 0.65:
                main_type = "The Energizer"
            elif energy > 0.65 and valence < 0.4:
                main_type = "The Intense Explorer"
            elif energy < 0.4 and valence > 0.6:
                main_type = "The Gentle Optimist"
            elif energy < 0.4 and valence < 0.4:
                main_type = "The Deep Thinker"
            elif danceability > 0.7:
                main_type = "The Dance Enthusiast"
            elif acousticness > 0.7:
                main_type = "The Acoustic Soul"
            else:
                main_type = "The Balanced Listener"
                
            results['listening_personality'] = {
                'main_type': main_type,
                'traits': personality_traits
            }
            
        except Exception as e:
            logging.error(f"Error determining listening personality: {str(e)}")
            results['listening_personality'] = {
                'main_type': "The Eclectic Listener",
                'traits': ["Diverse Tastes"]
            }
        
        # 4. Generate genre recommendations based on current preferences
        try:
            if OPENAI_API_KEY and results['top_genres']:
                # Import OpenAI here to avoid circular imports
                from openai import OpenAI
                
                # Initialize OpenAI client
                openai = OpenAI(api_key=OPENAI_API_KEY)
                
                # Prepare top genres string
                top_genres_str = ", ".join(results['top_genres'][:5])
                
                # Create prompt for recommendations
                prompt = f"""
                Based on these favorite music genres: {top_genres_str}
                
                Please recommend:
                1. 3 similar genres the person might enjoy
                2. 3 slightly different genres to expand their tastes
                3. 2 completely different genres they might find interesting as a stretch
                
                Format your response as a JSON object with these arrays:
                - similar_genres
                - expanding_genres
                - discovery_genres
                
                Use actual Spotify genre names only.
                """
                
                # Call OpenAI API
                # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a music recommendation expert who understands genre relationships and similarities."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=500
                )
                
                # Process response
                rec_result = json.loads(response.choices[0].message.content)
                
                results['recommendations'] = {
                    'similar': rec_result.get('similar_genres', []),
                    'expanding': rec_result.get('expanding_genres', []),
                    'discovery': rec_result.get('discovery_genres', [])
                }
            else:
                # Fallback if OpenAI is not available
                results['recommendations'] = {
                    'similar': ['pop', 'rock', 'indie'],
                    'expanding': ['jazz', 'classical', 'electronic'],
                    'discovery': ['world', 'funk']
                }
        
        except Exception as e:
            logging.error(f"Error generating genre recommendations: {str(e)}")
            results['recommendations'] = {
                'similar': ['pop', 'rock', 'indie'],
                'expanding': ['jazz', 'classical', 'electronic'],
                'discovery': ['world', 'funk']
            }
        
        return results
        
    except Exception as e:
        logging.error(f"Error analyzing listening history: {str(e)}")
        return {
            'top_genres': ['pop', 'rock'],
            'audio_feature_averages': {},
            'listening_personality': {
                'main_type': "The Listener",
                'traits': ["Music Fan"]
            },
            'recommendations': {
                'similar': ['pop', 'rock'],
                'expanding': ['jazz', 'classical'],
                'discovery': ['world']
            }
        }

def generate_listening_report(spotify, time_range='medium_term'):
    """
    Generate a detailed report on user's listening habits with AI insights
    
    Args:
        spotify: Authenticated Spotify client
        time_range: Time range to analyze
        
    Returns:
        String with formatted report
    """
    try:
        # Analyze listening history
        analysis = analyze_listening_history(spotify, time_range)
        
        # Format time range for display
        time_labels = {
            'short_term': 'the past month',
            'medium_term': 'the past 6 months',
            'long_term': 'all time'
        }
        time_display = time_labels.get(time_range, 'recent history')
        
        # Start building the report
        report = f"🎧 YOUR SPOTIFY LISTENING REPORT ({time_display.upper()})\n\n"
        
        # Add personality section
        personality = analysis.get('listening_personality', {})
        main_type = personality.get('main_type', 'Music Listener')
        traits = personality.get('traits', [])
        
        report += f"🧠 LISTENING PERSONALITY: {main_type.upper()}\n"
        if traits:
            report += "Your listening traits:\n"
            for trait in traits:
                report += f"• {trait}\n"
        report += "\n"
        
        # Add top genres section
        top_genres = analysis.get('top_genres', [])
        if top_genres:
            report += "🎸 YOUR TOP GENRES:\n"
            for i, genre in enumerate(top_genres[:7], 1):
                report += f"{i}. {genre.title()}\n"
            report += "\n"
        
        # Add audio features section
        features = analysis.get('audio_feature_averages', {})
        if features:
            report += "🔊 YOUR MUSIC PREFERENCES:\n"
            
            if 'energy' in features:
                energy_pct = int(features['energy'] * 100)
                report += f"• Energy: {energy_pct}% ({self_categorize(features['energy'], 'energy')})\n"
                
            if 'valence' in features:
                valence_pct = int(features['valence'] * 100)
                report += f"• Mood/Positivity: {valence_pct}% ({self_categorize(features['valence'], 'valence')})\n"
                
            if 'danceability' in features:
                dance_pct = int(features['danceability'] * 100)
                report += f"• Danceability: {dance_pct}% ({self_categorize(features['danceability'], 'danceability')})\n"
                
            if 'acousticness' in features:
                acoustic_pct = int(features['acousticness'] * 100)
                report += f"• Acoustic vs. Electronic: {acoustic_pct}% acoustic\n"
                
            if 'tempo' in features:
                tempo = int(features['tempo'])
                report += f"• Average Tempo: {tempo} BPM ({self_categorize(features['tempo'], 'tempo')})\n"
                
            report += "\n"
        
        # Add recommendations section
        recommendations = analysis.get('recommendations', {})
        if recommendations:
            report += "✨ RECOMMENDED GENRE EXPLORATIONS:\n"
            
            similar = recommendations.get('similar', [])
            if similar:
                report += "If you like what you already listen to:\n"
                for genre in similar:
                    report += f"• {genre.title()}\n"
                report += "\n"
                
            expanding = recommendations.get('expanding', [])
            if expanding:
                report += "To expand your horizons a bit:\n"
                for genre in expanding:
                    report += f"• {genre.title()}\n"
                report += "\n"
                
            discovery = recommendations.get('discovery', [])
            if discovery:
                report += "For a completely new experience:\n"
                for genre in discovery:
                    report += f"• {genre.title()}\n"
                report += "\n"
        
        # Add personalized playlist suggestions
        report += "🎵 PERSONALIZED PLAYLIST IDEAS:\n"
        
        if personality.get('main_type') == "The Energizer":
            report += "• \"Peak Energy Mix\" - Your ultimate high-energy favorites\n"
            report += "• \"Good Vibes Only\" - Positive, uplifting tracks matching your taste\n"
        elif personality.get('main_type') == "The Deep Thinker":
            report += "• \"Introspection\" - Thoughtful tracks for contemplative moments\n"
            report += "• \"Emotional Journey\" - Music that resonates with deeper feelings\n"
        elif personality.get('main_type') == "The Intense Explorer":
            report += "• \"Intensity Session\" - High-energy tracks with emotional depth\n"
            report += "• \"Focused Power\" - Driving, forceful music for when you need motivation\n"
        elif personality.get('main_type') == "The Gentle Optimist":
            report += "• \"Calm Positivity\" - Relaxing tracks with uplifting energy\n"
            report += "• \"Peaceful Joy\" - Gentle music that brings happiness\n"
        elif personality.get('main_type') == "The Dance Enthusiast":
            report += "• \"Rhythm & Groove\" - Your ultimate dance collection\n"
            report += "• \"Movement Mix\" - Tracks that keep you moving\n"
        elif personality.get('main_type') == "The Acoustic Soul":
            report += "• \"Unplugged Favorites\" - Your top acoustic tracks\n"
            report += "• \"Natural Sound\" - Music with organic instrumentation\n"
        else:
            report += "• \"Your Eclectic Mix\" - A diverse playlist based on your varied tastes\n"
            report += "• \"Mood Versatility\" - Music for all your different moods\n"
            
        report += "\n"
        
        # Add instructions for creating AI playlists
        report += "🤖 CREATE AN AI PLAYLIST:\n"
        report += "Use the command: 'ai playlist [description of your mood or what you want]'\n"
        report += "Example: 'ai playlist I'm feeling relaxed but need some gentle motivation'\n\n"
        
        report += "Report generated on " + datetime.now().strftime("%B %d, %Y at %H:%M")
        
        return report
        
    except Exception as e:
        logging.error(f"Error generating listening report: {str(e)}")
        return f"❌ Error generating listening report: {str(e)}"

def self_categorize(value, feature_type):
    """Helper function to categorize audio feature values"""
    if feature_type == 'energy':
        if value < 0.33:
            return "relaxed/calm"
        elif value < 0.66:
            return "moderate energy"
        else:
            return "high energy"
    elif feature_type == 'valence':
        if value < 0.33:
            return "melancholic/serious"
        elif value < 0.66:
            return "balanced mood"
        else:
            return "positive/upbeat"
    elif feature_type == 'danceability':
        if value < 0.33:
            return "less danceable"
        elif value < 0.66:
            return "moderately rhythmic"
        else:
            return "highly danceable"
    elif feature_type == 'tempo':
        if value < 90:
            return "slower paced"
        elif value < 120:
            return "moderate tempo"
        elif value < 150:
            return "upbeat"
        else:
            return "very fast"
    return "moderate"