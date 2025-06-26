"""
Voice Interface Package

This package provides voice interface capabilities for the NOUS personal assistant.
It includes modules for speech-to-text and text-to-speech functionality.
"""

from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech

__all__ = ['SpeechToText', 'TextToSpeech']