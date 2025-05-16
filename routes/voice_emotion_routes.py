"""
Routes for voice emotion analysis feature.
"""

import io
import json
import logging
from flask import Blueprint, render_template, request, jsonify, current_app, session
from flask_login import login_required, current_user

from utils.emotion_detection import analyze_voice_audio, log_emotion
from utils.key_config import get_huggingface_token

# Get the Hugging Face access token
HF_ACCESS_TOKEN = get_huggingface_token()

voice_emotion_bp = Blueprint('voice_emotion', __name__)

@voice_emotion_bp.route('/voice/emotion', methods=['GET'])
@login_required
def voice_emotion_analysis():
    """Display the voice emotion analysis page"""
    
    # Check if we have Hugging Face access
    if not HF_ACCESS_TOKEN:
        return render_template('errors/feature_unavailable.html', 
                              message="Voice emotion analysis requires Hugging Face API access. Please contact support.")
    
    return render_template('voice_emotion.html')

@voice_emotion_bp.route('/voice/analyze_emotion', methods=['POST'])
@login_required
def analyze_voice_emotion():
    """Process a voice audio file for emotion analysis"""
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400
    
    try:
        audio_file = request.files['audio']
        audio_bytes = audio_file.read()
        
        if not audio_bytes:
            return jsonify({'success': False, 'error': 'Empty audio file'}), 400
        
        # Get the user ID if a user is logged in
        user_id = str(current_user.id) if current_user.is_authenticated else None
        
        # Analyze the audio for emotions
        result = analyze_voice_audio(audio_bytes, user_id)
        
        # Log the detected emotion
        if user_id and 'emotion' in result and 'confidence' in result:
            log_emotion(
                user_id=user_id,
                emotion=result['emotion'],
                confidence=result['confidence'],
                source='voice',
                details=f"Voice analysis - {result.get('source', 'unknown source')}"
            )
        
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