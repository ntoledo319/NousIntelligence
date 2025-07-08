"""
Voice-Guided Mindfulness Exercises Routes

This module provides web routes for the Mindfulness Voice Assistant feature.
It includes a dashboard, exercise details, personalized exercise generation,
and logging of completed sessions.

@ai_prompt: When modifying these routes, consider the data flow from the
user (e.g., personalization form) to the `utils.voice_mindfulness` logic
and back to the template.

@context_boundary: This is the web layer for the mindfulness feature. It
relies on `utils.voice_mindfulness` for content and logic, and interacts
with templates in the `templates/voice_mindfulness/` directory.
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

# Import our voice mindfulness utility
from utils.voice_mindfulness import (
    get_random_exercise,
    get_exercise_by_name,
    get_exercise_by_duration,
    generate_personalized_exercise,
    log_exercise_completion,
    prepare_exercise_for_tts
)
# Import the text_to_speech function
from utils.voice_interaction import text_to_speech

voice_mindfulness_bp = Blueprint('voice_mindfulness', __name__, url_prefix='/voice-mindfulness')

# Helper to get user_id from current_user
def get_user_id():
    return str(get_current_user().get("id") if get_current_user() else None) if is_authenticated() else None

@voice_mindfulness_bp.route('/')
@login_required
def index():
    """
    Renders the voice mindfulness exercises dashboard.

    Displays a list of available pre-defined exercises.
    """
    user_id = get_user_id()

    # Get a list of pre-defined exercises
    from utils.voice_mindfulness import MINDFULNESS_EXERCISES
    exercises = MINDFULNESS_EXERCISES

    return render_template(
        'voice_mindfulness/index.html',
        exercises=exercises
    )

@voice_mindfulness_bp.route('/exercise/<exercise_name>')
@login_required
def exercise_detail(exercise_name):
    """
    Shows detail for a specific mindfulness exercise.

    Prepares the exercise script for Text-to-Speech (TTS) before rendering.

    Args:
        exercise_name: The name of the exercise from the URL.
    """
    user_id = get_user_id()

    # Get the exercise by name
    exercise = get_exercise_by_name(exercise_name)
    if not exercise:
        flash(f"Exercise '{exercise_name}' not found", "error")
        return redirect(url_for('voice_mindfulness.index'))

    # Prepare the exercise for TTS
    prepared_exercise = prepare_exercise_for_tts(exercise)

    # Generate the audio for the exercise
    tts_result = text_to_speech(prepared_exercise['tts_script'], user_id)
    audio_base64 = tts_result.get('audio_base64') if tts_result.get('success') else None

    return render_template(
        'voice_mindfulness/exercise.html',
        exercise=prepared_exercise,
        audio_base64=audio_base64
    )

@voice_mindfulness_bp.route('/random')
@login_required
def random_exercise():
    """
    Shows a random mindfulness exercise, optionally filtered by duration.

    Picks a random exercise and prepares it for TTS.
    """
    # Get duration from query param, default to 5 minutes
    try:
        duration = int(request.args.get('duration', 5))
    except ValueError:
        duration = 5

    # Get a random exercise within duration constraint
    exercise = get_exercise_by_duration(duration)

    # Prepare the exercise for TTS
    prepared_exercise = prepare_exercise_for_tts(exercise)

    # Generate the audio for the exercise
    user_id = get_user_id()
    tts_result = text_to_speech(prepared_exercise['tts_script'], user_id)
    audio_base64 = tts_result.get('audio_base64') if tts_result.get('success') else None

    return render_template(
        'voice_mindfulness/exercise.html',
        exercise=prepared_exercise,
        audio_base64=audio_base64
    )

@voice_mindfulness_bp.route('/personalized', methods=['GET', 'POST'])
@login_required
def personalized_exercise():
    """
    Generates and shows a personalized mindfulness exercise.

    On GET, displays a form for the user to input their mood and situation.
    On POST, generates a personalized exercise using the AI helper and
    prepares it for TTS.
    """
    user_id = get_user_id()

    if request.method == 'POST':
        # Get parameters from form
        mood = request.form.get('mood', '')
        situation = request.form.get('situation', '')
        try:
            duration = int(request.form.get('duration', 5))
        except ValueError:
            duration = 5

        # Generate a personalized exercise
        exercise = generate_personalized_exercise(user_id, mood, situation, duration)

        # Prepare the exercise for TTS
        prepared_exercise = prepare_exercise_for_tts(exercise)

        # Generate the audio for the exercise
        tts_result = text_to_speech(prepared_exercise['tts_script'], user_id)
        audio_base64 = tts_result.get('audio_base64') if tts_result.get('success') else None

        return render_template(
            'voice_mindfulness/exercise.html',
            exercise=prepared_exercise,
            personalized=True,
            audio_base64=audio_base64
        )

    # GET request - show the form to create a personalized exercise
    return render_template('voice_mindfulness/personalize.html')

@voice_mindfulness_bp.route('/log-completion', methods=['POST'])
@login_required
def log_completion():
    """
    Logs the completion of a mindfulness exercise from a form submission.
    """
    user_id = get_user_id()

    # Get parameters from form
    exercise_name = request.form.get('exercise_name', '')
    try:
        rating = int(request.form.get('rating', 0))
        if rating < 1 or rating > 5:
            rating = None
    except ValueError:
        rating = None

    # Log the completion
    success = log_exercise_completion(user_id, exercise_name, rating)

    if success:
        flash(f"Exercise '{exercise_name}' completed successfully", "success")
    else:
        flash("Failed to log exercise completion", "error")

    return redirect(url_for('voice_mindfulness.index'))