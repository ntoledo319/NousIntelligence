"""
Voice Emotion Analysis Routes

This module provides the web routes for the Voice Emotion Analysis feature.
It handles rendering the analysis page and processing audio file uploads
for emotion detection.

@ai_prompt: When making changes to the voice analysis workflow, consider
both the frontend interaction (file upload) and the backend processing
pipeline in `utils.emotion_detection`.

@context_boundary: This module is the web layer for the emotion detection
feature. It depends on `utils.emotion_detection` for the core logic and
`models.EmotionLog` for data persistence.
"""

# AI-GENERATED [2024-07-29]
# HUMAN-VALIDATED [2024-07-29]

import io
import json
import logging
from flask import Blueprint, render_template, request, jsonify, current_app, session
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

from utils.emotion_detection import analyze_voice_audio
from utils.settings import get_setting

voice_emotion_bp = Blueprint('voice_emotion', __name__)

@voice_emotion_bp.route('/voice/emotion', methods=['GET'])
@login_required
def voice_emotion_analysis():
    """
    Renders the voice emotion analysis page.

    Checks if the HuggingFace integration is enabled before rendering.
    """
    # Check if we have Hugging Face access
    if not get_setting('enable_huggingface_api', True):
        return render_template('errors/feature_unavailable.html',
                               message="Voice emotion analysis requires Hugging Face API access. Please contact support.")

    return render_template('voice_emotion.html')

@voice_emotion_bp.route('/voice/analyze_emotion', methods=['POST'])
@login_required
def analyze_voice_emotion():
    """
    Processes a voice audio file for emotion analysis.

    This endpoint expects a POST request with an 'audio' file. It uses
    the `analyze_voice_audio` utility to process the file and returns
    a JSON response with the detected emotion and other analysis details.

    Returns:
        JSON response with analysis results or an error message.
    """

    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400

    try:
        audio_file = request.files['audio']
        audio_bytes = audio_file.read()

        if not audio_bytes:
            return jsonify({'success': False, 'error': 'Empty audio file'}), 400

        # Get the user ID if a user is logged in
        user_id = str(get_current_user().get("id") if get_current_user() else None) if is_authenticated() else None

        # Analyze the audio for emotions
        result = analyze_voice_audio(audio_bytes, user_id)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        logging.error(f"Error analyzing voice emotion: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error analyzing voice: {str(e)}"
        }), 500