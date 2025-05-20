"""
Voice Interface Module

This module provides the core functionality for the voice interface of NOUS.
It integrates local speech-to-text (Whisper.cpp) and text-to-speech (Piper) capabilities
without requiring external API calls.

The module handles:
1. Audio processing from browser/frontend
2. Transcription of speech using Whisper.cpp
3. Text-to-speech generation using Piper
4. Audio format conversion and processing
"""

import os
import tempfile
import logging
import base64
import subprocess
import json
from typing import Dict, Any, Optional, Union, Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Constants for the voice interface
WHISPER_DIR = os.path.expanduser("~/whisper.cpp")
WHISPER_MODEL = os.path.join(WHISPER_DIR, "models/tiny.en.bin")
PIPER_DIR = os.path.expanduser("~/piper")
PIPER_MODEL = os.path.join(PIPER_DIR, "en_US-lessac-medium.onnx")

class VoiceInterface:
    """Main class for Voice Interface functionality"""
    
    def __init__(self):
        """Initialize the voice interface"""
        self.whisper_available = os.path.exists(WHISPER_DIR) and os.path.exists(WHISPER_MODEL)
        self.piper_available = os.path.exists(PIPER_DIR) and os.path.exists(PIPER_MODEL)
        
        if not self.whisper_available:
            logger.warning("Whisper.cpp not found or model missing. Speech-to-text will use browser fallback.")
        
        if not self.piper_available:
            logger.warning("Piper not found or model missing. Text-to-speech will use browser fallback.")
    
    def transcribe_audio(self, audio_data: str) -> Dict[str, Any]:
        """
        Transcribe speech from base64-encoded audio data using Whisper.cpp
        
        Args:
            audio_data: Base64-encoded audio data
            
        Returns:
            Dict containing transcription result
        """
        if not self.whisper_available:
            return {"error": "Whisper.cpp not available"}
            
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            # Run whisper.cpp on the audio file
            whisper_cmd = [
                os.path.join(WHISPER_DIR, "main"),
                "-m", WHISPER_MODEL,
                "-f", temp_audio_path,
                "-t", "4",
                "--no-progress"
            ]
            
            result = subprocess.run(
                whisper_cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Clean up the temporary file
            os.unlink(temp_audio_path)
            
            # Parse the result
            transcript = result.stdout.strip()
            
            return {
                "success": True,
                "transcript": transcript
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_speech(self, text: str) -> Dict[str, Any]:
        """
        Generate speech using Piper TTS
        
        Args:
            text: The text to convert to speech
            
        Returns:
            Dict containing the generated speech as base64-encoded audio
        """
        if not self.piper_available:
            return {"error": "Piper not available"}
            
        try:
            # Create a temporary file for the output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            # Run piper to generate speech
            piper_cmd = [
                os.path.join(PIPER_DIR, "piper"),
                "--model", PIPER_MODEL,
                "--output_file", temp_audio_path
            ]
            
            process = subprocess.Popen(
                piper_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send the text to piper
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                raise Exception(f"Piper error: {stderr}")
            
            # Read the generated audio
            with open(temp_audio_path, "rb") as f:
                audio_data = f.read()
            
            # Clean up the temporary file
            os.unlink(temp_audio_path)
            
            # Return base64-encoded audio
            return {
                "success": True,
                "audio": base64.b64encode(audio_data).decode('utf-8')
            }
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Create a singleton instance
_voice_interface = None

def get_voice_interface() -> VoiceInterface:
    """Get or create the VoiceInterface instance"""
    global _voice_interface
    if _voice_interface is None:
        _voice_interface = VoiceInterface()
    return _voice_interface