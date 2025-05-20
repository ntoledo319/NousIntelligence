"""
Voice Interface Routes

This module provides routes for voice interface functionality.
It handles audio recording, speech recognition, and text-to-speech synthesis.
"""

import os
import json
import logging
import tempfile
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# Create blueprint
voice_bp = Blueprint('voice', __name__, url_prefix='/voice')

# Set up logger
logger = logging.getLogger(__name__)

# Define upload folder for audio files
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'voice')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@voice_bp.route('/')
def index():
    """Voice interface homepage"""
    return render_template('voice_interface.html')

@voice_bp.route('/upload-audio', methods=['POST'])
def upload_audio():
    """
    Handle audio file upload for transcription
    
    Accepts WAV, MP3, or OGG audio files and transcribes them to text
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not supported. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    try:
        # Save the file with a timestamp in the filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = secure_filename(f"{timestamp}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Import here to avoid circular imports
        from voice_interface.speech_to_text import SpeechToText
        
        # Create speech-to-text processor
        stt = SpeechToText()
        
        # Process the audio file (this would typically use whisper.cpp)
        # For now, we're using a placeholder as we haven't fully integrated whisper.cpp
        result = {
            "success": True,
            "text": "This is a placeholder transcription. Speech-to-text will be fully integrated with Whisper.cpp.",
            "method": "placeholder"
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """
    Synthesize text to speech
    
    Accepts text input and returns an audio file of the synthesized speech
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        # Import here to avoid circular imports
        from voice_interface.text_to_speech import TextToSpeech
        
        # Create text-to-speech processor
        tts = TextToSpeech()
        
        # Generate a temporary file to store the audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            output_file = temp_file.name
        
        # Synthesize speech (placeholder response until fully integrated with Piper)
        result = {
            "success": True,
            "output_file": output_file,
            "method": "placeholder"
        }
        
        # In a real implementation, we would generate the audio file here
        # For now, we'll return a placeholder message
        return jsonify({
            "success": True,
            "message": "Text-to-speech synthesis will be fully integrated with Piper."
        })
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/process-voice-command', methods=['POST'])
def process_voice_command():
    """
    Process a voice command
    
    1. Transcribes audio to text
    2. Processes the command
    3. Returns a text response
    4. Optionally synthesizes speech from the response
    """
    try:
        # Check if request contains audio file
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not supported. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save the audio file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = secure_filename(f"{timestamp}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Placeholder for speech-to-text processing
        transcription = "This is a placeholder transcription for voice command processing."
        
        # Placeholder for command processing logic
        # In a real implementation, this would integrate with the NOUS assistant's AI/NLP features
        response_text = "I've received your voice command and I'm processing it."
        
        # Return response
        result = {
            "success": True,
            "transcription": transcription,
            "response": response_text
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing voice command: {str(e)}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/continuous-listening', methods=['GET'])
def continuous_listening():
    """Page for continuous listening mode"""
    return render_template('continuous_listening.html')

@voice_bp.route('/test-whisper', methods=['GET'])
def test_whisper():
    """Test Whisper.cpp integration"""
    try:
        # Try to run whisper.cpp to test if it's working
        import subprocess
        import os
        
        whisper_path = os.path.expanduser("~/whisper.cpp/main")
        model_path = os.path.expanduser("~/whisper.cpp/models/tiny.en.bin")
        
        if not os.path.exists(whisper_path):
            return jsonify({"status": "error", "message": "Whisper.cpp binary not found"})
            
        if not os.path.exists(model_path):
            return jsonify({"status": "error", "message": "Whisper model not found"})
        
        # Run a simple test
        cmd = [whisper_path, "--version"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return jsonify({
            "status": "success",
            "message": "Whisper.cpp is installed",
            "output": result.stdout,
            "binary_path": whisper_path,
            "model_path": model_path
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@voice_bp.route('/test-piper', methods=['GET'])
def test_piper():
    """Test Piper TTS integration"""
    try:
        # Try to run piper to test if it's working
        import subprocess
        import os
        
        piper_path = os.path.expanduser("~/piper/piper")
        model_path = os.path.expanduser("~/piper/voices/en_US-lessac-medium.onnx")
        
        if not os.path.exists(piper_path):
            return jsonify({"status": "error", "message": "Piper binary not found"})
            
        if not os.path.exists(model_path):
            return jsonify({"status": "error", "message": "Piper voice model not found"})
        
        # Run a simple test
        cmd = [piper_path, "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return jsonify({
            "status": "success",
            "message": "Piper is installed",
            "output": result.stdout,
            "binary_path": piper_path,
            "model_path": model_path
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})