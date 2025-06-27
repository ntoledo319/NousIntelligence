"""
Text-to-Speech Module

This module provides text-to-speech functionality for the NOUS personal assistant
using Piper TTS with a fallback to gTTS (Google Text-to-Speech) when local processing is unavailable.
"""

import os
import logging
import tempfile
import subprocess
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import pygame
from gtts import gTTS

# Configure logging
logger = logging.getLogger(__name__)

class TextToSpeech:
    """
    Text-to-Speech processor that converts text to speech audio.
    Uses local Piper TTS when available, with fallback to gTTS.
    """
    
    def __init__(self, piper_path: Optional[str] = None, voice_model_path: Optional[str] = None):
        """
        Initialize the text-to-speech processor.
        
        Args:
            piper_path: Path to Piper binary (if using local processing)
            voice_model_path: Path to voice model file (if using local processing)
        """
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Default paths
        self.piper_path = piper_path or os.path.expanduser("~/piper/piper")
        self.voice_model_path = voice_model_path or os.path.expanduser("~/piper/voices/en_US-lessac-medium.onnx")
        
        # Check if Piper binary and voice model exist
        self.has_piper = os.path.exists(self.piper_path) and os.path.exists(self.voice_model_path)
        
        if self.has_piper:
            logger.info("Piper TTS found at %s with voice model %s", 
                       self.piper_path, self.voice_model_path)
        else:
            logger.warning("Piper TTS not found. Will use gTTS as fallback.")
    
    def synthesize_with_piper(self, text: str, output_file: str) -> bool:
        """
        Synthesize speech using local Piper TTS.
        
        Args:
            text: Text to synthesize
            output_file: Path to output audio file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If synthesis fails
        """
        if not self.has_piper:
            raise RuntimeError("Piper TTS not available")
        
        try:
            # Create a temporary file for the input text
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(text)
                text_path = temp_file.name
            
            cmd = [
                self.piper_path,
                "--model", self.voice_model_path,
                "--output_file", output_file,
                "--output-raw",  # Raw PCM output for better quality
                "--json-input",  # Use JSON input format
            ]
            
            # Run Piper with input from the temporary file
            with open(text_path, 'r') as f_in, open(output_file, 'wb') as f_out:
                process = subprocess.run(
                    cmd,
                    stdin=f_in,
                    stdout=f_out,
                    stderr=subprocess.PIPE,
                    check=True
                )
            
            # Clean up temporary file
            os.unlink(text_path)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error("Piper TTS synthesis failed: %s", e.stderr.decode())
            raise RuntimeError(f"Piper synthesis failed: {e.stderr.decode()}")
    
    def synthesize_with_gtts(self, text: str, output_file: str, lang: str = 'en') -> bool:
        """
        Synthesize speech using Google Text-to-Speech.
        
        Args:
            text: Text to synthesize
            output_file: Path to output audio file
            lang: Language code
            
        Returns:
            True if successful, False otherwise
        """
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_file)
            return True
        except Exception as e:
            logger.error("gTTS synthesis failed: %s", str(e))
            return False
    
    def synthesize_speech(self, text: str, output_file: Optional[str] = None, 
                          play_audio: bool = True) -> Dict[str, Any]:
        """
        Synthesize text to speech using available methods.
        
        Args:
            text: Text to synthesize
            output_file: Path to output audio file (or None for temporary file)
            play_audio: Whether to play the audio immediately
            
        Returns:
            Dictionary containing synthesis results and metadata
        """
        result = {
            "success": False,
            "output_file": output_file,
            "error": None,
            "method": None,
            "temporary_file": False
        }
        
        # Create a temporary file if output_file is not provided
        if output_file is None:
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            output_file = temp_file.name
            temp_file.close()
            result["output_file"] = output_file
            result["temporary_file"] = True
        
        try:
            # Try using Piper TTS first if available
            if self.has_piper:
                self.synthesize_with_piper(text, output_file)
                result["method"] = "piper-local"
                result["success"] = True
            
            # Fall back to gTTS if Piper failed or is unavailable
            if not result["success"]:
                self.synthesize_with_gtts(text, output_file)
                result["method"] = "google-tts"
                result["success"] = True
            
            # Play the audio if requested and synthesis was successful
            if play_audio and result["success"]:
                self.play_audio(output_file)
                
        except Exception as e:
            result["error"] = str(e)
            logger.error("Speech synthesis failed: %s", str(e))
        
        return result
    
    def play_audio(self, audio_file: str) -> None:
        """
        Play audio file.
        
        Args:
            audio_file: Path to audio file
        """
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            logger.error("Audio playback failed: %s", str(e))
    
    def cleanup_temporary_files(self, result: Dict[str, Any]) -> None:
        """
        Clean up temporary files created during synthesis.
        
        Args:
            result: Result dictionary from synthesize_speech
        """
        if result.get("temporary_file") and result.get("output_file"):
            try:
                output_file = result.get("output_file")
                if os.path.exists(output_file):
                    os.unlink(output_file)
            except Exception as e:
                logger.error("Failed to clean up temporary file: %s", str(e))