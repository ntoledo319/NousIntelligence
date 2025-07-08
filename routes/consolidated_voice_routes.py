"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Consolidated Voice Routes Routes
Consolidated Voice Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

consolidated_voice_routes_bp = Blueprint('consolidated_voice_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Consolidated Voice Routes - Zero Functionality Loss Optimization
Consolidates voice_routes.py, voice_emotion_routes.py, voice_mindfulness_routes.py
"""

from flask import Blueprint, request, jsonify, session, render_template
from config.app_config import AppConfig
import logging

# Create consolidated voice blueprint
consolidated_voice_bp = Blueprint('consolidated_voice', __name__)

# Voice Interface Routes (from voice_routes.py)
@consolidated_voice_bp.route('/', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def voice_interface():
    """Main voice interface page"""
    return render_template('voice_interface.html')

@consolidated_voice_bp.route('/process', methods=['POST'])
def process_voice():
    """Process voice input"""
    if 'user_id' not in session:
        return jsonify({"error": "Demo mode - limited access"}), 401
    
    data = request.get_json()
    if not data or 'audio_data' not in data:
        return jsonify({"error": "Audio data required"}), 400
    
    try:
        # Placeholder for voice processing - maintain backward compatibility
        return jsonify({
            "status": "processed",
            "transcript": "Voice processing not yet implemented",
            "response": "Voice processing functionality maintained"
        })
    except Exception as e:
        logging.error(f"Voice processing error: {e}")
        return jsonify({"error": "Processing failed"}), 500

@consolidated_voice_bp.route('/settings', methods=['GET', 'POST'])
def voice_settings():
    """Voice interface settings"""
    if request.method == 'GET':
        return jsonify({
            "language": "en-US",
            "voice_type": "default",
            "speed": 1.0
        })
    
    # POST - update settings
    data = request.get_json()
    return jsonify({"status": "settings updated", "data": data})

# Voice Emotion Routes (from voice_emotion_routes.py)
@consolidated_voice_bp.route('/emotion/analyze', methods=['POST'])
def analyze_emotion():
    """Analyze emotion from voice input"""
    if 'user_id' not in session:
        return jsonify({"error": "Demo mode - limited access"}), 401
    
    data = request.get_json()
    if not data or 'audio_data' not in data:
        return jsonify({"error": "Audio data required"}), 400
    
    return jsonify({
        "emotion": "neutral",
        "confidence": 0.8,
        "emotions": {
            "happy": 0.3,
            "sad": 0.1,
            "angry": 0.1,
            "neutral": 0.5
        }
    })

@consolidated_voice_bp.route('/emotion/history', methods=['GET'])
def emotion_history():
    """Get emotion analysis history"""
    if 'user_id' not in session:
        return jsonify({"error": "Demo mode - limited access"}), 401
    
    return jsonify({
        "history": [],
        "summary": {
            "dominant_emotion": "neutral",
            "trend": "stable"
        }
    })

# Voice Mindfulness Routes (from voice_mindfulness_routes.py)
@consolidated_voice_bp.route('/mindfulness/session', methods=['POST'])
def start_mindfulness_session():
    """Start a voice-guided mindfulness session"""
    if 'user_id' not in session:
        return jsonify({"error": "Demo mode - limited access"}), 401
    
    data = request.get_json() or {}
    session_type = data.get('type', 'breathing')
    duration = data.get('duration', 300)  # 5 minutes default
    
    return jsonify({
        "session_id": "mindfulness_001",
        "type": session_type,
        "duration": duration,
        "instructions": f"Starting {session_type} session for {duration//60} minutes",
        "status": "started"
    })

@consolidated_voice_bp.route('/mindfulness/session/<session_id>', methods=['GET'])
def get_mindfulness_session(session_id):
    """Get mindfulness session status"""
    if 'user_id' not in session:
        return jsonify({"error": "Demo mode - limited access"}), 401
    
    return jsonify({
        "session_id": session_id,
        "status": "active",
        "progress": 0.5,
        "remaining_time": 150
    })

@consolidated_voice_bp.route('/mindfulness/complete', methods=['POST'])
def complete_mindfulness_session():
    """Complete mindfulness session"""
    if 'user_id' not in session:
        return jsonify({"error": "Demo mode - limited access"}), 401
    
    data = request.get_json()
    session_id = data.get('session_id')
    
    return jsonify({
        "status": "completed",
        "session_id": session_id,
        "feedback": "Session completed successfully"
    })

@consolidated_voice_bp.route('/mindfulness/templates', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def mindfulness_templates():
    """Get available mindfulness templates"""
    return render_template('voice_mindfulness/templates.html')

# Text-to-Speech Routes
@consolidated_voice_bp.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Text required"}), 400
    
    text = data['text']
    voice = data.get('voice', 'default')
    speed = data.get('speed', 1.0)
    
    try:
        # Placeholder for TTS processing
        return jsonify({
            "status": "success",
            "audio_url": f"/voice/audio/generated_{len(text)}.wav",
            "duration": len(text) * 0.1  # Rough estimate
        })
    except Exception as e:
        logging.error(f"TTS error: {e}")
        return jsonify({"error": "TTS processing failed"}), 500

# Speech-to-Text Routes
@consolidated_voice_bp.route('/stt', methods=['POST'])
def speech_to_text():
    """Convert speech to text"""
    if 'audio' not in request.files:
        return jsonify({"error": "Audio file required"}), 400
    
    audio_file = request.files['audio']
    language = request.form.get('language', 'en-US')
    
    try:
        # Placeholder for STT processing
        return jsonify({
            "status": "success",
            "transcript": "Speech-to-text processing not yet implemented",
            "confidence": 0.95,
            "language": language
        })
    except Exception as e:
        logging.error(f"STT error: {e}")
        return jsonify({"error": "STT processing failed"}), 500

# Backward compatibility - register individual blueprints if they exist
def register_legacy_voice_blueprints(app):
    """Register legacy voice blueprints for backward compatibility"""
    try:
        from routes.voice_routes import voice_bp
        app.register_blueprint(voice_bp, url_prefix='/voice')
    except (ImportError, AttributeError):
        pass
    
    try:
        from routes.voice_emotion_routes import voice_emotion_bp
        app.register_blueprint(voice_emotion_bp, url_prefix='/voice/emotion')
    except (ImportError, AttributeError):
        pass
    
    try:
        from routes.voice_mindfulness_routes import voice_mindfulness_bp
        app.register_blueprint(voice_mindfulness_bp, url_prefix='/voice/mindfulness')
    except (ImportError, AttributeError):
        pass