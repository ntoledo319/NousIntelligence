"""
Voice-guided mindfulness exercises routes
All routes are prefixed with /voice-mindfulness
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user

# Import our voice mindfulness utility
from utils.voice_mindfulness import (
    get_random_exercise,
    get_exercise_by_name,
    get_exercise_by_duration,
    generate_personalized_exercise,
    log_exercise_completion,
    prepare_exercise_for_tts
)

voice_mindfulness_bp = Blueprint('voice_mindfulness', __name__, url_prefix='/voice-mindfulness')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

@voice_mindfulness_bp.route('/')
@login_required
def index():
    """Voice mindfulness exercises dashboard"""
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
    """Show detail for a specific mindfulness exercise"""
    user_id = get_user_id()
    
    # Get the exercise by name
    exercise = get_exercise_by_name(exercise_name)
    if not exercise:
        flash(f"Exercise '{exercise_name}' not found", "error")
        return redirect(url_for('voice_mindfulness.index'))
    
    # Prepare the exercise for TTS
    prepared_exercise = prepare_exercise_for_tts(exercise)
    
    return render_template(
        'voice_mindfulness/exercise.html',
        exercise=prepared_exercise
    )

@voice_mindfulness_bp.route('/random')
@login_required
def random_exercise():
    """Show a random mindfulness exercise"""
    # Get duration from query param, default to 5 minutes
    try:
        duration = int(request.args.get('duration', 5))
    except ValueError:
        duration = 5
        
    # Get a random exercise within duration constraint
    exercise = get_exercise_by_duration(duration)
    
    # Prepare the exercise for TTS
    prepared_exercise = prepare_exercise_for_tts(exercise)
    
    return render_template(
        'voice_mindfulness/exercise.html',
        exercise=prepared_exercise
    )

@voice_mindfulness_bp.route('/personalized', methods=['GET', 'POST'])
@login_required
def personalized_exercise():
    """Generate and show a personalized mindfulness exercise"""
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
        
        return render_template(
            'voice_mindfulness/exercise.html',
            exercise=prepared_exercise,
            personalized=True
        )
        
    # GET request - show the form to create a personalized exercise
    return render_template('voice_mindfulness/personalize.html')

@voice_mindfulness_bp.route('/log-completion', methods=['POST'])
@login_required
def log_completion():
    """Log the completion of a mindfulness exercise"""
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