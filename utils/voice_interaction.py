"""
Voice interaction module for processing speech input and providing voice responses.
This module handles speech recognition, speech synthesis, and voice emotion detection.
"""

import base64
import io
import json
import logging
import os
import tempfile
from typing import Dict, Optional, Tuple, Any

# Try to import the OpenAI client for Whisper and TTS
try:
    from utils.ai_helper import client as openai_client
    OPENAI_AVAILABLE = True
except (ImportError, AttributeError):
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI client not available for voice processing")

# Try to import emotion detection
try:
    from utils.emotion_detection import process_user_message, analyze_voice_audio
    EMOTION_DETECTION_AVAILABLE = True
except ImportError:
    EMOTION_DETECTION_AVAILABLE = False
    logging.warning("Emotion detection not available for voice processing")

    # Define dummy functions when emotion detection is not available
    def process_user_message(user_id, message, is_voice=False):
        """Fallback function when emotion detection is not available"""
        return {
            "emotion": "neutral",
            "confidence": 0.5,
            "source": "fallback"
        }

    def analyze_voice_audio(audio_data, user_id):
        """Fallback function when emotion detection is not available"""
        return {
            "emotion": "neutral",
            "confidence": 0.5,
            "energy": 0.5,
            "pitch_variation": 0.5
        }

# Try to import character customization for voice style
try:
    from utils.character_customization import get_character_settings
    CHARACTER_CUSTOMIZATION_AVAILABLE = True
except ImportError:
    CHARACTER_CUSTOMIZATION_AVAILABLE = False
    logging.warning("Character customization not available for voice processing")

    # Define a dummy function if the import fails
    def get_character_settings():
        """Fallback function when character customization is not available"""
        return {
            "ai_name": "NOUS",
            "ai_personality": "helpful",
            "ai_voice_type": "neutral",
            "ai_formality": "casual",
            "ai_verbosity": "balanced",
            "ai_enthusiasm": "moderate",
            "ai_emoji_usage": "occasional",
            "ai_backstory": ""
        }

def transcribe_audio(audio_data: bytes, user_id: str) -> Dict[str, Any]:
    """
    Transcribe audio data to text using OpenAI Whisper

    Args:
        audio_data: Raw audio data as bytes
        user_id: User ID for tracking and personalization

    Returns:
        Dict containing transcription result and metadata
    """
    if not OPENAI_AVAILABLE or not openai_client:
        return {
            "success": False,
            "error": "OpenAI client not available",
            "text": "",
            "metadata": {}
        }

    try:
        # Save audio data to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        # Transcribe the audio file
        with open(temp_file_path, "rb") as audio_file:
            response = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Clean up the temporary file
        os.unlink(temp_file_path)

        transcribed_text = response.text

        # Process for emotional content
        emotion_data = {}
        if EMOTION_DETECTION_AVAILABLE and transcribed_text:
            # Analyze text for emotions
            emotion_result = process_user_message(user_id, transcribed_text, is_voice=True)

            # Also analyze audio for voice characteristics
            audio_emotion = analyze_voice_audio(audio_data, user_id)

            # Combine results - text-based emotion with voice characteristics
            emotion_data = {
                "detected_emotion": emotion_result["emotion"],
                "confidence": emotion_result["confidence"],
                "voice_characteristics": audio_emotion.get("audio_features", {})
            }

        return {
            "success": True,
            "text": transcribed_text,
            "metadata": {
                "emotion_data": emotion_data
            }
        }

    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "text": "",
            "metadata": {}
        }

def text_to_speech(text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert text to speech using OpenAI TTS

    Args:
        text: Text to convert to speech
        user_id: Optional user ID for personalization

    Returns:
        Dict containing speech data and metadata
    """
    if not OPENAI_AVAILABLE or not openai_client:
        return {
            "success": False,
            "error": "OpenAI client not available",
            "audio_base64": None,
            "metadata": {}
        }

    try:
        # Determine voice settings based on character customization and user preferences
        voice_settings = {}
        if CHARACTER_CUSTOMIZATION_AVAILABLE and user_id:
            character_settings = get_character_settings()

            # Map voice type to OpenAI voice options
            voice_mapping = {
                "neutral": "nova",
                "calm": "alloy",
                "energetic": "shimmer",
                "authoritative": "onyx",
                "warm": "echo"
            }

            # Get voice type from character settings
            voice_type = character_settings.get("ai_voice_type", "neutral")
            openai_voice = voice_mapping.get(voice_type, "nova")

            voice_settings["voice"] = openai_voice

            # Adjust speed based on emotion and character
            if EMOTION_DETECTION_AVAILABLE:
                from utils.emotion_detection import get_recent_emotions

                # Get most recent emotion
                recent_emotions = get_recent_emotions(user_id, limit=1)
                if recent_emotions:
                    recent_emotion = recent_emotions[0]["emotion"]

                    # Adjust speed slightly based on emotion
                    speed_adjustments = {
                        "happiness": 1.1,  # Slightly faster
                        "sadness": 0.9,    # Slightly slower
                        "anger": 1.15,     # Faster
                        "fear": 1.05,      # Slightly faster
                        "surprise": 1.1,   # Slightly faster
                        "confusion": 0.95, # Slightly slower
                        "neutral": 1.0     # Normal speed
                    }

                    speed = speed_adjustments.get(recent_emotion, 1.0)
                    voice_settings["speed"] = speed
        else:
            # Default voice settings
            voice_settings = {
                "voice": "nova",  # Balanced, versatile voice
                "speed": 1.0
            }

        # Generate speech using OpenAI TTS
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice=voice_settings.get("voice", "nova"),
            input=text,
            speed=voice_settings.get("speed", 1.0)
        )

        # Get audio data as byte stream
        audio_data = io.BytesIO()
        for chunk in response.iter_bytes(chunk_size=4096):
            audio_data.write(chunk)
        audio_data.seek(0)

        # Convert to base64 for web transmission
        audio_base64 = base64.b64encode(audio_data.read()).decode('utf-8')

        return {
            "success": True,
            "audio_base64": audio_base64,
            "metadata": {
                "voice_settings": voice_settings
            }
        }

    except Exception as e:
        logging.error(f"Error generating speech: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "audio_base64": None,
            "metadata": {}
        }

def process_voice_command(audio_data: bytes, user_id: str) -> Dict[str, Any]:
    """
    Process a voice command from start to finish

    Args:
        audio_data: Raw audio data from client
        user_id: User ID for personalization

    Returns:
        Dict with command processing results
    """
    # First transcribe the audio to text
    transcription = transcribe_audio(audio_data, user_id)

    if not transcription["success"]:
        return {
            "success": False,
            "error": transcription.get("error", "Failed to transcribe audio"),
            "response": None
        }

    command_text = transcription["text"]

    # Process the command through the AI assistant
    from utils.ai_helper import handle_conversation

    # Include emotion data as context
    emotion_context = transcription.get("metadata", {}).get("emotion_data", {})

    # Process the command
    response_text = handle_conversation(user_id, command_text, {"emotion": emotion_context})

    # Convert the response to speech if needed
    speech_response = text_to_speech(response_text, user_id)

    return {
        "success": True,
        "command": command_text,
        "response_text": response_text,
        "voice_response": speech_response if speech_response["success"] else None,
        "emotion_detected": emotion_context.get("detected_emotion", "neutral")
    }