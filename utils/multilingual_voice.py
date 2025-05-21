"""
Multilingual Voice Interface Utilities

This module provides text-to-speech and speech-to-text functions for multiple languages,
optimized for language learning applications.
"""

import os
import logging
import base64
import io
import json
from typing import Dict, Any, Optional, List

import openai
from flask import current_app

# Configure logging
logger = logging.getLogger(__name__)

# Language code mappings
LANGUAGE_CODES = {
    'en-US': 'English (US)',
    'en-GB': 'English (UK)',
    'es-ES': 'Spanish (Spain)',
    'es-MX': 'Spanish (Mexico)',
    'fr-FR': 'French',
    'de-DE': 'German',
    'it-IT': 'Italian',
    'ja-JP': 'Japanese',
    'ko-KR': 'Korean',
    'zh-CN': 'Chinese (Simplified)',
    'pt-BR': 'Portuguese (Brazil)'
}

# TTS voice mappings by language
TTS_VOICES = {
    'en-US': 'nova',    # English - female voice
    'en-GB': 'fable',   # English - male voice with British accent
    'es-ES': 'nova',    # Spanish - using standard voice
    'es-MX': 'alloy',   # Spanish (Mexico) - using alternative voice
    'fr-FR': 'alloy',   # French - using alternative voice
    'de-DE': 'onyx',    # German - using alternative voice
    'it-IT': 'shimmer', # Italian
    'ja-JP': 'nova',    # Japanese
    'ko-KR': 'alloy',   # Korean
    'zh-CN': 'onyx',    # Chinese
    'pt-BR': 'shimmer'  # Portuguese
}

# Speech recognition language options
STT_LANGUAGES = {
    'en-US': 'English (United States)',
    'en-GB': 'English (United Kingdom)',
    'es-ES': 'Spanish (Spain)',
    'es-MX': 'Spanish (Mexico)', 
    'fr-FR': 'French',
    'de-DE': 'German',
    'it-IT': 'Italian',
    'ja-JP': 'Japanese',
    'ko-KR': 'Korean',
    'zh-CN': 'Chinese (Simplified)',
    'pt-BR': 'Portuguese (Brazil)'
}


def generate_speech(text: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate speech from text using OpenAI TTS
    
    Args:
        text: Text to convert to speech
        options: Dictionary of options including:
            - voice: Voice to use (default: nova)
            - speed: Speed of speech (default: 1.0)
            - language: Language code (used for logging/tracking)
            
    Returns:
        Dictionary with speech data and metadata
    """
    try:
        if not text:
            return {
                "success": False,
                "error": "No text provided",
                "audio_base64": None
            }
            
        # Set default options
        if options is None:
            options = {}
            
        voice = options.get("voice", "nova")
        speed = options.get("speed", 1.0)
        language = options.get("language", "en-US")
        
        # Get API key 
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "OpenAI API key not available",
                "audio_base64": None
            }
            
        # Initialize client
        client = openai.OpenAI(api_key=api_key)
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=speed
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
                "language": language,
                "language_name": LANGUAGE_CODES.get(language, language),
                "voice": voice,
                "speed": speed,
                "text_length": len(text)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "audio_base64": None
        }


def transcribe_speech(audio_data: bytes, language: str = "en") -> Dict[str, Any]:
    """
    Transcribe speech to text using OpenAI Whisper
    
    Args:
        audio_data: Audio data as bytes
        language: Language code (e.g., 'en', 'es', 'fr')
        
    Returns:
        Dictionary with transcription results
    """
    try:
        # Get API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "OpenAI API key not available",
                "text": None
            }
            
        # Initialize client
        client = openai.OpenAI(api_key=api_key)
        
        # Create a temporary file for the audio
        with io.BytesIO(audio_data) as audio_file:
            # Transcribe the audio
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        
        # Extract the transcription text
        text = response.text
        
        return {
            "success": True,
            "text": text,
            "metadata": {
                "language": language,
                "language_name": LANGUAGE_CODES.get(language, language),
                "confidence": 0.9  # Whisper API doesn't provide confidence scores
            }
        }
        
    except Exception as e:
        logger.error(f"Error transcribing speech: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "text": None
        }


def get_pronunciation_feedback(audio_data: bytes, text: str, language: str) -> Dict[str, Any]:
    """
    Analyze pronunciation and provide feedback
    
    Args:
        audio_data: Audio recording of user speaking
        text: Expected text that user was trying to say
        language: Language code
        
    Returns:
        Dictionary with pronunciation feedback
    """
    try:
        # Get API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "OpenAI API key not available",
                "feedback": None
            }
            
        # First, transcribe the audio
        transcription_result = transcribe_speech(audio_data, language)
        if not transcription_result.get("success", False):
            return {
                "success": False,
                "error": transcription_result.get("error", "Transcription failed"),
                "feedback": None
            }
            
        actual_text = transcription_result.get("text", "")
        
        # Initialize client for analysis
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare prompt for pronunciation analysis
        language_name = LANGUAGE_CODES.get(language, language)
        prompt = f"""
        I'm learning {language_name} and practicing pronunciation.
        
        Expected text: "{text}"
        What I said: "{actual_text}"
        
        Please analyze my pronunciation and provide feedback in these categories:
        1. Accuracy (how close was I to saying the correct words)
        2. Specific sound or word issues
        3. Tips for improvement
        
        Format as a JSON object with: accuracy_score (0-100), issues (array), tips (array), and overall_feedback (string).
        """
        
        # Get AI feedback
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a {language_name} language teacher specializing in pronunciation."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        if response.choices and response.choices[0].message.content:
            feedback = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "transcribed_text": actual_text,
                "expected_text": text,
                "feedback": feedback,
                "metadata": {
                    "language": language,
                    "language_name": language_name
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to generate pronunciation feedback",
                "feedback": None
            }
            
    except Exception as e:
        logger.error(f"Error generating pronunciation feedback: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "feedback": None
        }


def get_available_languages() -> List[Dict[str, str]]:
    """
    Get list of available languages for voice interface
    
    Returns:
        List of dictionaries with language code and name
    """
    languages = []
    
    for code, name in LANGUAGE_CODES.items():
        languages.append({
            "code": code,
            "name": name,
            "tts_available": code in TTS_VOICES,
            "stt_available": code in STT_LANGUAGES
        })
    
    return languages