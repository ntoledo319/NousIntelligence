"""
Enhanced Voice Service - Advanced Voice Processing and Recognition
Handles speech-to-text, text-to-speech, emotion detection, and voice commands
"""

import logging
import os
import tempfile
import wave
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone
import io

logger = logging.getLogger(__name__)

# Try to import voice processing libraries with fallbacks
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    logger.warning("SpeechRecognition not available - voice input disabled")
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    logger.warning("pyttsx3 not available - using fallback TTS")
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    logger.warning("NumPy not available - advanced audio processing disabled")
    NUMPY_AVAILABLE = False
    np = None


class VoiceProcessor:
    """Core voice processing functionality"""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.supported_formats = ['wav', 'mp3', 'flac', 'ogg']
        
        self._initialize_speech_recognition()
        self._initialize_tts()
    
    def _initialize_speech_recognition(self):
        """Initialize speech recognition"""
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                
                logger.info("Speech recognition initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize speech recognition: {str(e)}")
                self.recognizer = None
                self.microphone = None
        else:
            logger.warning("Speech recognition not available")
    
    def _initialize_tts(self):
        """Initialize text-to-speech"""
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS settings
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                
                # Set speaking rate and volume
                self.tts_engine.setProperty('rate', 200)  # Speed of speech
                self.tts_engine.setProperty('volume', 0.8)  # Volume level
                
                logger.info("Text-to-speech initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize TTS: {str(e)}")
                self.tts_engine = None
        else:
            logger.warning("Text-to-speech not available")
    
    def transcribe_audio(self, audio_data: Union[bytes, str], language: str = 'en-US') -> Dict[str, Any]:
        """Transcribe audio to text"""
        try:
            if not self.recognizer:
                return {
                    'success': False,
                    'error': 'Speech recognition not available',
                    'text': '',
                    'confidence': 0.0
                }
            
            # Handle different input types
            if isinstance(audio_data, str):
                # File path
                with sr.AudioFile(audio_data) as source:
                    audio = self.recognizer.record(source)
            elif isinstance(audio_data, bytes):
                # Raw audio bytes
                audio_file = io.BytesIO(audio_data)
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
            else:
                return {
                    'success': False,
                    'error': 'Invalid audio data format',
                    'text': '',
                    'confidence': 0.0
                }
            
            # Try multiple recognition services
            results = []
            
            # Google Speech Recognition (free tier)
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                results.append({
                    'service': 'google',
                    'text': text,
                    'confidence': 0.8  # Estimated confidence
                })
            except sr.UnknownValueError:
                logger.debug("Google could not understand audio")
            except sr.RequestError as e:
                logger.debug(f"Google service error: {str(e)}")
            
            # Sphinx (offline fallback)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                results.append({
                    'service': 'sphinx',
                    'text': text,
                    'confidence': 0.6  # Lower confidence for offline
                })
            except sr.UnknownValueError:
                logger.debug("Sphinx could not understand audio")
            except sr.RequestError as e:
                logger.debug(f"Sphinx service error: {str(e)}")
            
            if results:
                # Return best result (highest confidence)
                best_result = max(results, key=lambda x: x['confidence'])
                return {
                    'success': True,
                    'text': best_result['text'],
                    'confidence': best_result['confidence'],
                    'service': best_result['service'],
                    'alternatives': results
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not transcribe audio',
                    'text': '',
                    'confidence': 0.0
                }
        
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def text_to_speech(self, text: str, output_file: Optional[str] = None, 
                      voice_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert text to speech"""
        try:
            if not self.tts_engine:
                return {
                    'success': False,
                    'error': 'Text-to-speech not available',
                    'audio_file': None
                }
            
            # Apply voice settings if provided
            if voice_settings:
                if 'rate' in voice_settings:
                    self.tts_engine.setProperty('rate', voice_settings['rate'])
                if 'volume' in voice_settings:
                    self.tts_engine.setProperty('volume', voice_settings['volume'])
                if 'voice' in voice_settings:
                    voices = self.tts_engine.getProperty('voices')
                    for voice in voices:
                        if voice_settings['voice'].lower() in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
            
            # Generate speech
            if output_file:
                self.tts_engine.save_to_file(text, output_file)
                self.tts_engine.runAndWait()
                
                return {
                    'success': True,
                    'audio_file': output_file,
                    'text': text
                }
            else:
                # Play directly
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
                return {
                    'success': True,
                    'audio_file': None,
                    'text': text
                }
        
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'audio_file': None
            }
    
    def record_audio(self, duration: int = 5, timeout: int = 1) -> Dict[str, Any]:
        """Record audio from microphone"""
        try:
            if not self.recognizer or not self.microphone:
                return {
                    'success': False,
                    'error': 'Audio recording not available',
                    'audio_data': None
                }
            
            with self.microphone as source:
                logger.info(f"Recording audio for {duration} seconds...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=duration)
                
                return {
                    'success': True,
                    'audio_data': audio,
                    'duration': duration
                }
        
        except sr.WaitTimeoutError:
            return {
                'success': False,
                'error': 'Recording timeout - no audio detected',
                'audio_data': None
            }
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'audio_data': None
            }


class EmotionDetector:
    """Detect emotions from voice characteristics"""
    
    def __init__(self):
        self.emotion_keywords = {
            'happy': ['great', 'awesome', 'wonderful', 'excited', 'good', 'yes'],
            'sad': ['bad', 'terrible', 'awful', 'disappointed', 'no', 'upset'],
            'frustrated': ['annoying', 'stupid', 'hate', 'angry', 'mad'],
            'confused': ['what', 'how', 'confused', 'understand', 'unclear'],
            'curious': ['why', 'how', 'what', 'interesting', 'tell me'],
            'neutral': []
        }
    
    def detect_emotion_from_text(self, text: str) -> Dict[str, Any]:
        """Detect emotion from transcribed text"""
        try:
            text_lower = text.lower()
            emotion_scores = {}
            
            for emotion, keywords in self.emotion_keywords.items():
                if emotion == 'neutral':
                    continue
                
                score = 0
                for keyword in keywords:
                    if keyword in text_lower:
                        score += 1
                
                if score > 0:
                    emotion_scores[emotion] = score / len(keywords)
            
            if emotion_scores:
                detected_emotion = max(emotion_scores.items(), key=lambda x: x[1])
                return {
                    'emotion': detected_emotion[0],
                    'confidence': detected_emotion[1],
                    'all_scores': emotion_scores
                }
            else:
                return {
                    'emotion': 'neutral',
                    'confidence': 0.5,
                    'all_scores': {}
                }
        
        except Exception as e:
            logger.error(f"Error detecting emotion: {str(e)}")
            return {
                'emotion': 'neutral',
                'confidence': 0.0,
                'all_scores': {}
            }
    
    def detect_emotion_from_audio(self, audio_data: Any) -> Dict[str, Any]:
        """Detect emotion from audio characteristics (advanced feature)"""
        # This would require more advanced ML models for audio analysis
        # For now, return neutral emotion
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'features': {
                'pitch': 'unknown',
                'energy': 'unknown',
                'tempo': 'unknown'
            }
        }


class VoiceCommandProcessor:
    """Process voice commands and intents"""
    
    def __init__(self):
        self.command_patterns = {
            'create_task': ['create task', 'add task', 'new task', 'remind me to'],
            'create_event': ['create event', 'schedule', 'add to calendar'],
            'get_weather': ['weather', 'forecast', 'temperature'],
            'play_music': ['play music', 'play song', 'start music'],
            'stop_music': ['stop music', 'pause music', 'stop playing'],
            'set_timer': ['set timer', 'timer for', 'countdown'],
            'get_time': ['what time', 'current time', 'time is'],
            'get_date': ['what date', 'today date', 'current date'],
            'search': ['search for', 'look up', 'find information'],
            'help': ['help', 'what can you do', 'commands']
        }
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """Process voice command and extract intent"""
        try:
            text_lower = text.lower()
            
            # Check for command patterns
            for intent, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        return {
                            'intent': intent,
                            'text': text,
                            'confidence': 0.8,
                            'parameters': self._extract_parameters(text, intent)
                        }
            
            # If no specific command detected, treat as general query
            return {
                'intent': 'general_query',
                'text': text,
                'confidence': 0.5,
                'parameters': {}
            }
        
        except Exception as e:
            logger.error(f"Error processing voice command: {str(e)}")
            return {
                'intent': 'unknown',
                'text': text,
                'confidence': 0.0,
                'parameters': {}
            }
    
    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from command text"""
        parameters = {}
        text_lower = text.lower()
        
        try:
            if intent == 'create_task':
                # Extract task description
                for pattern in ['remind me to ', 'create task ', 'add task ', 'new task ']:
                    if pattern in text_lower:
                        task_desc = text_lower.split(pattern, 1)[1].strip()
                        parameters['description'] = task_desc
                        break
            
            elif intent == 'create_event':
                # Extract event details (basic implementation)
                parameters['title'] = text
                # More sophisticated parsing would extract date/time
            
            elif intent == 'set_timer':
                # Extract duration
                import re
                duration_match = re.search(r'(\d+)\s*(minute|second|hour)', text_lower)
                if duration_match:
                    value = int(duration_match.group(1))
                    unit = duration_match.group(2)
                    parameters['duration'] = value
                    parameters['unit'] = unit
            
            elif intent == 'search':
                # Extract search query
                for pattern in ['search for ', 'look up ', 'find information about ']:
                    if pattern in text_lower:
                        query = text_lower.split(pattern, 1)[1].strip()
                        parameters['query'] = query
                        break
        
        except Exception as e:
            logger.debug(f"Error extracting parameters: {str(e)}")
        
        return parameters


class EnhancedVoiceService:
    """Main enhanced voice service"""
    
    def __init__(self):
        self.processor = VoiceProcessor()
        self.emotion_detector = EmotionDetector()
        self.command_processor = VoiceCommandProcessor()
        self.conversation_history = []
    
    def process_voice_input(self, audio_data: Union[bytes, str], 
                          language: str = 'en-US') -> Dict[str, Any]:
        """Complete voice input processing pipeline"""
        try:
            # Step 1: Transcribe audio
            transcription = self.processor.transcribe_audio(audio_data, language)
            
            if not transcription['success']:
                return {
                    'success': False,
                    'error': transcription['error'],
                    'transcription': None,
                    'emotion': None,
                    'command': None
                }
            
            text = transcription['text']
            
            # Step 2: Detect emotion
            emotion = self.emotion_detector.detect_emotion_from_text(text)
            
            # Step 3: Process command
            command = self.command_processor.process_command(text)
            
            # Step 4: Store in conversation history
            conversation_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'text': text,
                'emotion': emotion['emotion'],
                'intent': command['intent'],
                'confidence': transcription['confidence']
            }
            self.conversation_history.append(conversation_entry)
            
            # Keep only last 50 entries
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-50:]
            
            return {
                'success': True,
                'transcription': transcription,
                'emotion': emotion,
                'command': command,
                'conversation_id': len(self.conversation_history)
            }
        
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transcription': None,
                'emotion': None,
                'command': None
            }
    
    def generate_voice_response(self, text: str, emotion_context: Optional[str] = None,
                              voice_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate appropriate voice response"""
        try:
            # Adjust response based on emotion context
            if emotion_context:
                text = self._adjust_response_for_emotion(text, emotion_context)
            
            # Generate speech
            tts_result = self.processor.text_to_speech(text, voice_settings=voice_settings)
            
            return {
                'success': tts_result['success'],
                'text': text,
                'audio_file': tts_result.get('audio_file'),
                'emotion_context': emotion_context
            }
        
        except Exception as e:
            logger.error(f"Error generating voice response: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,
                'audio_file': None
            }
    
    def _adjust_response_for_emotion(self, text: str, emotion: str) -> str:
        """Adjust response tone based on detected emotion"""
        emotion_prefixes = {
            'sad': "I understand you're feeling down. ",
            'frustrated': "I can hear you're frustrated. Let me help. ",
            'happy': "I'm glad to hear you're in good spirits! ",
            'confused': "No worries, let me clarify that for you. ",
            'curious': "Great question! "
        }
        
        prefix = emotion_prefixes.get(emotion, "")
        return prefix + text
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of recent voice conversations"""
        if not self.conversation_history:
            return {
                'total_interactions': 0,
                'recent_emotions': [],
                'common_intents': [],
                'average_confidence': 0.0
            }
        
        recent_emotions = [entry['emotion'] for entry in self.conversation_history[-10:]]
        all_intents = [entry['intent'] for entry in self.conversation_history]
        confidences = [entry['confidence'] for entry in self.conversation_history]
        
        # Count intent frequency
        intent_counts = {}
        for intent in all_intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        common_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_interactions': len(self.conversation_history),
            'recent_emotions': recent_emotions,
            'common_intents': common_intents,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'latest_interaction': self.conversation_history[-1] if self.conversation_history else None
        }


# Global enhanced voice service instance
enhanced_voice_service = EnhancedVoiceService()


# Helper functions for backward compatibility
def transcribe_voice(audio_data, language='en-US'):
    """Transcribe voice to text"""
    return enhanced_voice_service.processor.transcribe_audio(audio_data, language)


def speak_text(text, **kwargs):
    """Convert text to speech"""
    return enhanced_voice_service.processor.text_to_speech(text, **kwargs)


def process_voice_command(audio_data):
    """Process complete voice command"""
    return enhanced_voice_service.process_voice_input(audio_data)


def detect_emotion(text):
    """Detect emotion from text"""
    return enhanced_voice_service.emotion_detector.detect_emotion_from_text(text)


class EnhancedVoice:
    """Legacy compatibility class"""
    
    def __init__(self):
        self.service = enhanced_voice_service
    
    def __getattr__(self, name):
        return getattr(self.service, name)