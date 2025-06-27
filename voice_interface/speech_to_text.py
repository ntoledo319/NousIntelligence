"""
Speech-to-Text Module

This module provides speech-to-text functionality for the NOUS personal assistant
using Python's speech_recognition library with a fallback to local Whisper model
when available.
"""

import os
import logging
import tempfile
import subprocess
from typing import Optional, Dict, Any, List, Tuple
import speech_recognition as sr

# Configure logging
logger = logging.getLogger(__name__)

class SpeechToText:
    """
    Speech-to-Text processor that converts audio input to text.
    Uses local Whisper.cpp when available, with fallback to Google Web Speech API.
    """
    
    def __init__(self, whisper_model_path: Optional[str] = None):
        """
        Initialize the speech-to-text processor.
        
        Args:
            whisper_model_path: Path to Whisper model file (if using local processing)
        """
        self.recognizer = sr.Recognizer()
        self.whisper_model_path = whisper_model_path
        self.whisper_binary_path = os.path.expanduser("~/whisper.cpp/main")
        
        # Check if Whisper binary exists
        self.has_whisper = os.path.exists(self.whisper_binary_path)
        if self.has_whisper:
            logger.info("Whisper.cpp binary found at %s", self.whisper_binary_path)
        else:
            logger.warning("Whisper.cpp binary not found. Will use alternative methods.")
    
    def record_audio(self, duration: int = 5) -> sr.AudioData:
        """
        Record audio from microphone for specified duration.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            AudioData object containing the recorded audio
            
        Raises:
            RuntimeError: If microphone access fails
        """
        logger.info("Recording audio for %d seconds", duration)
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            return self.recognizer.record(source, duration=duration)
    
    def save_audio_data(self, audio_data: sr.AudioData, file_path: str) -> None:
        """
        Save AudioData to WAV file.
        
        Args:
            audio_data: AudioData object to save
            file_path: Path where to save the WAV file
        """
        with open(file_path, "wb") as f:
            f.write(audio_data.get_wav_data())
        logger.debug("Audio saved to %s", file_path)
    
    def transcribe_with_whisper(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using local Whisper.cpp.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
            
        Raises:
            RuntimeError: If transcription fails
        """
        if not self.has_whisper:
            raise RuntimeError("Whisper.cpp binary not available")
        
        model_path = self.whisper_model_path or os.path.expanduser("~/whisper.cpp/models/tiny.en.bin")
        
        try:
            cmd = [
                self.whisper_binary_path,
                "-m", model_path,
                "-f", audio_file_path,
                "-nt"  # No timestamps in output
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Extract transcription (skip any timestamp prefixes)
            text = result.stdout.strip()
            lines = [line for line in text.split('\n') if not line.startswith('[')]
            return ' '.join(lines)
            
        except subprocess.CalledProcessError as e:
            logger.error("Whisper.cpp transcription failed: %s", e.stderr)
            raise RuntimeError(f"Whisper transcription failed: {e.stderr}")
    
    def transcribe_with_google(self, audio_data: sr.AudioData) -> str:
        """
        Transcribe audio using Google Web Speech API.
        
        Args:
            audio_data: AudioData object to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            sr.UnknownValueError: If speech is unintelligible
            sr.RequestError: If API request fails
        """
        return self.recognizer.recognize_google(audio_data)
    
    def transcribe_audio(self, audio_data: Optional[sr.AudioData] = None, 
                         duration: int = 5) -> Dict[str, Any]:
        """
        Transcribe audio to text using available methods.
        
        Args:
            audio_data: AudioData object to transcribe (or None to record new audio)
            duration: Recording duration in seconds (if recording new audio)
            
        Returns:
            Dictionary containing transcription results and metadata
        """
        result = {
            "success": False,
            "text": "",
            "error": None,
            "method": None
        }
        
        try:
            # Record audio if not provided
            if audio_data is None:
                audio_data = self.record_audio(duration=duration)
            
            # Try using Whisper.cpp first if available
            if self.has_whisper:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                
                try:
                    self.save_audio_data(audio_data, temp_path)
                    result["text"] = self.transcribe_with_whisper(temp_path)
                    result["method"] = "whisper-local"
                    result["success"] = True
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
            
            # Fall back to Google Web Speech API if Whisper failed or is unavailable
            if not result["success"]:
                result["text"] = self.transcribe_with_google(audio_data)
                result["method"] = "google-web-speech"
                result["success"] = True
                
        except sr.UnknownValueError:
            result["error"] = "Speech was unintelligible"
        except sr.RequestError as e:
            result["error"] = f"API request failed: {e}"
        except RuntimeError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
        
        return result