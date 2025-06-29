"""
Voice Interface Package

This package provides voice interface capabilities for the NOUS personal assistant.
It includes modules for speech-to-text and text-to-speech functionality.
"""

# Try to import voice interface components with fallback handling
try:
    from .speech_to_text import SpeechToText
    speech_to_text_available = True
except ImportError as e:
    print(f"Warning: Speech-to-text not available: {e}")
    speech_to_text_available = False
    
    # Create fallback class
    class SpeechToText:
        def __init__(self, *args, **kwargs):
            print("Warning: SpeechToText fallback - limited functionality")
        
        def transcribe_audio(self, audio_data=None, duration=5):
            return {
                "success": False,
                "text": "",
                "error": "Speech recognition not available - please install speech-recognition package",
                "method": "fallback"
            }

try:
    from .text_to_speech import TextToSpeech
    text_to_speech_available = True
except ImportError as e:
    print(f"Warning: Text-to-speech not available: {e}")
    text_to_speech_available = False
    
    # Create fallback class
    class TextToSpeech:
        def __init__(self, *args, **kwargs):
            print("Warning: TextToSpeech fallback - limited functionality")
        
        def speak(self, text):
            return {
                "success": False,
                "error": "Text-to-speech not available",
                "method": "fallback"
            }

__all__ = ['SpeechToText', 'TextToSpeech', 'speech_to_text_available', 'text_to_speech_available']