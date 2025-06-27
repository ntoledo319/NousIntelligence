"""
Mindfulness Voice Assistant Utilities

This module contains the core logic for the voice-guided mindfulness feature.
It manages a library of pre-defined exercises, generates personalized sessions
using AI, and handles logging user progress.

@ai_prompt: This is the primary logic module for the mindfulness feature.
To add new exercises, modify the `MINDFULNESS_EXERCISES` list. To change
the AI generation prompt, see `generate_personalized_exercise`.

@context_boundary: This module uses `utils.ai_service_manager` to interact
with AI models for personalized content. It is called by the routes in
`routes.voice_mindfulness_routes`. It also interacts with the `MindfulnessLog`
model in the database.
"""

# AI-GENERATED [2024-07-29]
# HUMAN-VALIDATED [2024-07-29]

import os
import logging
import json
import random
from datetime import datetime
from typing import Dict, Any, Optional

# Import cost-optimized AI for generating personalized exercises
from utils.cost_optimized_ai import get_cost_optimized_ai, TaskComplexity

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

def generate_personalized_exercise(user_id: str, mood: str, situation: str, duration: int) -> Dict[str, Any]:
    """
    Generates a personalized mindfulness exercise using an AI model.

    Constructs a detailed prompt based on the user's input and sends it
    to the AI service manager to get a custom exercise script.

    Args:
        user_id: The ID of the user requesting the exercise.
        mood: The user's current mood (e.g., 'stressed', 'anxious').
        situation: The user's current situation (e.g., 'at work', 'before bed').
        duration: The desired duration of the exercise in minutes.

    Returns:
        A dictionary representing the AI-generated exercise.
    """
    try:
        ai_client = get_cost_optimized_ai()

        # Create a prompt for the AI to generate a personalized exercise
        prompt = f"Create a {duration}-minute mindfulness meditation script"
        if mood:
            prompt += f" for someone feeling {mood}"
        if situation:
            prompt += f" who is dealing with {situation}"

        prompt += ". The script should be calm, supportive, and include [pause] indicators where appropriate."

        messages = [
            {"role": "system", "content": "You are a skilled mindfulness meditation guide."},
            {"role": "user", "content": prompt}
        ]

        # Use standard complexity for meditation content
        result = ai_client.chat_completion(messages, max_tokens=500, complexity=TaskComplexity.STANDARD)

        if result.get("success"):
            script = result.get("response", "Take a deep breath in. Hold for a moment. Now exhale slowly. Continue breathing deeply for a few minutes, focusing on each breath.")
        else:
            script = "Take a deep breath in. Hold for a moment. Now exhale slowly. Continue breathing deeply for a few minutes, focusing on each breath."

        # Create a name for this exercise
        name_prompt = "Give this mindfulness meditation a short, descriptive title (5 words or less)."
        name_messages = [
            {"role": "system", "content": "You generate short, descriptive titles."},
            {"role": "user", "content": f"Meditation script: {script}\n\n{name_prompt}"}
        ]

        name_result = ai_client.chat_completion(name_messages, max_tokens=20, complexity=TaskComplexity.BASIC)

        if name_result.get("success"):
            name = name_result.get("response", "Calming Breath Meditation").strip().replace('"', '')
        else:
            name = "Calming Breath Meditation"

        return {
            "name": name,
            "duration": duration,
            "description": f"Personalized mindfulness exercise based on your current situation.",
            "script": script,
            "personalized": True,
            "cost": result.get("cost", 0.0) + name_result.get("cost", 0.0)
        }

    except Exception as e:
        logging.error(f"Error generating personalized exercise: {str(e)}")
        # Fallback to pre-defined exercise
        return get_exercise_by_duration(duration)

def log_exercise_completion(user_id: str, exercise_name: str, rating: Optional[int]) -> bool:
    """
    Logs the completion of a mindfulness exercise to the database.

    Args:
        user_id: The ID of the user who completed the exercise.
        exercise_name: The name of the completed exercise.
        rating: An optional user-provided rating from 1 to 5.

    Returns:
        True if logging was successful, False otherwise.
    """
    try:
        log_entry = MindfulnessLog(
            user_id=user_id,
            exercise_name=exercise_name,
            rating=rating
        )
        log_entry.save()
        return True
    except Exception as e:
        logging.error(f"Error logging exercise completion: {str(e)}")
        return False

def prepare_exercise_for_tts(exercise: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepares an exercise script for Text-to-Speech (TTS) processing.

    This function formats the exercise script by replacing [pause] markers
    with a consistent, speakable representation that the TTS can interpret
    as a pause.

    Args:
        exercise: The exercise dictionary.

    Returns:
        The exercise dictionary with a `tts_script` field added.
    """
    script = exercise.get('script', "")
    
    # Replace [pause] with a consistent pause phrase for the TTS
    # A simple but effective way to create pauses in many TTS systems.
    tts_script = script.replace("[pause]", "...")
    
    exercise['tts_script'] = tts_script
    return exercise