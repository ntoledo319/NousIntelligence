"""
Voice-guided mindfulness exercises utility

This module provides functions for generating and delivering
voice-guided mindfulness exercises using the system's text-to-speech capabilities.
"""

import os
import logging
import json
import random
from datetime import datetime

# Import OpenAI for generating personalized exercises
from openai import OpenAI

# Constants
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

# Pre-defined mindfulness exercise templates
MINDFULNESS_EXERCISES = [
    {
        "name": "Body Scan",
        "duration": 5,  # minutes
        "description": "A guided body scan meditation focusing on each part of the body.",
        "script": "Find a comfortable position and close your eyes. Take three deep breaths. Now, bring your attention to your feet and notice any sensations there. [pause] Gradually move your awareness up through your legs, [pause] your torso, [pause] your arms, [pause] and finally to your head. Notice any areas of tension and allow them to relax with each breath. [pause] When you're ready, slowly open your eyes."
    },
    {
        "name": "Breath Awareness",
        "duration": 3,
        "description": "A simple meditation focusing on the breath.",
        "script": "Sit comfortably and close your eyes. Bring your attention to your breathing. Notice the sensation of air flowing in and out of your nostrils. [pause] Follow each breath from start to finish. [pause] If your mind wanders, gently bring it back to your breath. [pause] Continue for a few more breaths. [pause] When you're ready, slowly open your eyes."
    },
    {
        "name": "5-4-3-2-1 Grounding",
        "duration": 2,
        "description": "A grounding exercise using all five senses.",
        "script": "Look around and name 5 things you can see. [pause] Now, notice 4 things you can touch or feel. [pause] Listen for 3 sounds in your environment. [pause] Notice 2 things you can smell. [pause] Finally, notice 1 thing you can taste. [pause] Take a deep breath and notice how you feel now."
    },
    {
        "name": "Loving-Kindness",
        "duration": 4,
        "description": "A meditation to develop compassion for self and others.",
        "script": "Close your eyes and bring to mind someone you care about. Silently repeat: May you be happy. May you be healthy. May you be safe. May you live with ease. [pause] Now, direct these wishes to yourself: May I be happy. May I be healthy. May I be safe. May I live with ease. [pause] Finally, extend these wishes to all beings everywhere: May all beings be happy. May all beings be healthy. May all beings be safe. May all beings live with ease. [pause] When you're ready, slowly open your eyes."
    }
]

def get_exercise_by_name(name):
    """Get a mindfulness exercise by name"""
    for exercise in MINDFULNESS_EXERCISES:
        if exercise["name"].lower() == name.lower():
            return exercise
    return None

def get_random_exercise():
    """Get a random mindfulness exercise"""
    return random.choice(MINDFULNESS_EXERCISES)

def get_exercise_by_duration(max_duration):
    """Get an exercise that fits within the specified duration"""
    suitable_exercises = [ex for ex in MINDFULNESS_EXERCISES if ex["duration"] <= max_duration]
    if suitable_exercises:
        return random.choice(suitable_exercises)
    return get_random_exercise()  # Fallback to random if no suitable duration found

def generate_personalized_exercise(user_id, mood=None, situation=None, duration=5):
    """
    Generate a personalized mindfulness exercise using AI
    
    Args:
        user_id: The user's ID
        mood: Optional current mood
        situation: Optional current situation
        duration: Desired duration in minutes
        
    Returns:
        A mindfulness exercise object
    """
    try:
        if not OPENAI_API_KEY:
            logging.warning("No OpenAI API key found, returning pre-defined exercise")
            return get_exercise_by_duration(duration)
            
        # Create a prompt for the AI to generate a personalized exercise
        prompt = f"Create a {duration}-minute mindfulness meditation script"
        if mood:
            prompt += f" for someone feeling {mood}"
        if situation:
            prompt += f" who is dealing with {situation}"
            
        prompt += ". The script should be calm, supportive, and include [pause] indicators where appropriate."
        
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a skilled mindfulness meditation guide."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
        )
        
        try:
            script = response.choices[0].message.content
            if script is None:
                script = "Take a deep breath in. Hold for a moment. Now exhale slowly. Continue breathing deeply for a few minutes, focusing on each breath."
            else:
                script = script.strip()
        except (AttributeError, IndexError):
            script = "Take a deep breath in. Hold for a moment. Now exhale slowly. Continue breathing deeply for a few minutes, focusing on each breath."
        
        # Create a name for this exercise
        name_prompt = "Give this mindfulness meditation a short, descriptive title (5 words or less)."
        name_response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You generate short, descriptive titles."},
                {"role": "user", "content": f"Meditation script: {script}\n\n{name_prompt}"}
            ],
            max_tokens=20,
        )
        
        try:
            name = name_response.choices[0].message.content
            if name is None:
                name = "Calming Breath Meditation"
            else:
                name = name.strip().replace('"', '')
        except (AttributeError, IndexError):
            name = "Calming Breath Meditation"
        
        return {
            "name": name,
            "duration": duration,
            "description": f"Personalized mindfulness exercise based on your current situation.",
            "script": script,
            "personalized": True
        }
        
    except Exception as e:
        logging.error(f"Error generating personalized exercise: {str(e)}")
        # Fallback to pre-defined exercise
        return get_exercise_by_duration(duration)

def log_exercise_completion(user_id, exercise_name, rating=None):
    """
    Log the completion of a mindfulness exercise
    
    Args:
        user_id: The user's ID
        exercise_name: The name of the completed exercise
        rating: Optional rating (1-5) provided by the user
    """
    # This function would typically save to a database
    # For now, we'll just log it
    logging.info(f"User {user_id} completed '{exercise_name}' exercise with rating: {rating}")
    # In a real implementation, this would save to the database
    return True

def prepare_exercise_for_tts(exercise):
    """
    Prepare a mindfulness exercise for text-to-speech playback
    
    Args:
        exercise: The exercise object
        
    Returns:
        A formatted script with appropriate pauses and pacing for TTS
    """
    script = exercise["script"]
    
    # Replace [pause] indicators with actual pauses for TTS
    # Speech Synthesis Markup Language (SSML) pause: <break time="2s"/>
    script = script.replace("[pause]", '<break time="2s"/>')
    
    # Wrap in SSML format for better TTS quality
    ssml_script = f"""
    <speak>
    <prosody rate="slow" pitch="-2st">
    {script}
    </prosody>
    </speak>
    """
    
    return {
        "name": exercise["name"],
        "duration": exercise["duration"],
        "description": exercise["description"],
        "script": script,
        "ssml_script": ssml_script
    }