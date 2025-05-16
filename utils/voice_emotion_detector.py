"""
Voice Tone and Emotion Detection Module
Uses free Hugging Face models to detect emotions and tone from audio
"""

import os
import io
import logging
import tempfile
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import librosa
import soundfile as sf

# Import environment variables and models config
from utils.key_config import HF_ACCESS_TOKEN
from utils.models_config import get_model_for_task

# Optional imports for caching
try:
    from utils.cache_helper import cache_result
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logging.warning("Cache helper not available for voice emotion detection")

# Define emotion categories
EMOTION_CATEGORIES = [
    "angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"
]

class VoiceEmotionDetector:
    """Main class for detecting emotions from voice audio"""
    
    def __init__(self, use_huggingface=True):
        """Initialize the detector with appropriate models"""
        self.hf_token = HF_ACCESS_TOKEN
        self.use_huggingface = use_huggingface and self.hf_token
        
        if self.use_huggingface:
            logging.info("Initializing voice emotion detector with Hugging Face models")
        else:
            logging.warning("Hugging Face token not available, using local fallback for voice emotion detection")
    
    def detect_emotion_from_audio(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Detect emotion from raw audio data
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Sample rate of the audio
            
        Returns:
            Dict containing emotion detection results
        """
        # Convert bytes to audio array for processing
        try:
            # Create a temporary file to save the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_path = temp_audio.name
                temp_audio.write(audio_data)
                
            # Try to use the cached version if available
            if CACHE_AVAILABLE:
                # Generate a hash of the audio data for caching
                import hashlib
                audio_hash = hashlib.md5(audio_data).hexdigest()
                return self._detect_emotion_cached(temp_path, audio_hash)
            else:
                # Direct detection without caching
                return self._detect_emotion_direct(temp_path)
                
        except Exception as e:
            logging.error(f"Error detecting emotion from audio: {str(e)}")
            return self._fallback_emotion_result()
        finally:
            # Clean up the temporary file
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logging.error(f"Error deleting temporary audio file: {str(e)}")
    
    @cache_result(ttl_seconds=3600) if CACHE_AVAILABLE else lambda f: f
    def _detect_emotion_cached(self, audio_path: str, audio_hash: str) -> Dict[str, Any]:
        """Cached version of emotion detection for efficiency"""
        return self._detect_emotion_direct(audio_path)
    
    def _detect_emotion_direct(self, audio_path: str) -> Dict[str, Any]:
        """Core emotion detection logic"""
        # If Hugging Face is available, use it for emotion detection
        if self.use_huggingface:
            try:
                # Get the appropriate model for emotion detection
                provider, model = get_model_for_task("audio_emotion")
                
                # If not explicitly defined in models_config, use a good default model
                if model == "fallback":
                    model = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
                
                result = self._detect_with_huggingface(audio_path, model)
                if result:
                    return result
            except Exception as e:
                logging.error(f"Error using Hugging Face for emotion detection: {str(e)}")
                # Will fall back to local detection
        
        # If Hugging Face fails or isn't available, use local feature extraction
        return self._detect_with_local_features(audio_path)
    
    def _detect_with_huggingface(self, audio_path: str, model: str) -> Dict[str, Any]:
        """Use Hugging Face for emotion detection"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}"
        }
        
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        try:
            # Load and potentially preprocess the audio file
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            
            # Send to Hugging Face API
            response = requests.post(
                api_url,
                headers=headers,
                data=audio_bytes
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Format the results based on the model's output structure
                if isinstance(result, list) and len(result) > 0:
                    # Some models return a list of emotions with confidence
                    emotions = {}
                    for item in result:
                        if isinstance(item, dict) and "label" in item and "score" in item:
                            emotions[item["label"]] = item["score"]
                    
                    if emotions:
                        # Find the top emotion
                        top_emotion = max(emotions.items(), key=lambda x: x[1])
                        return {
                            "emotion": top_emotion[0],
                            "confidence": top_emotion[1],
                            "all_emotions": emotions,
                            "source": "huggingface",
                            "audio_features": self._extract_audio_features(audio_path)
                        }
                
                # Some models return a single object
                elif isinstance(result, dict) and "label" in result:
                    return {
                        "emotion": result["label"],
                        "confidence": result.get("score", 0.8),
                        "all_emotions": {result["label"]: result.get("score", 0.8)},
                        "source": "huggingface",
                        "audio_features": self._extract_audio_features(audio_path)
                    }
                
                # If the format is not recognized, log it for debugging
                logging.warning(f"Unexpected Hugging Face response format: {result}")
            else:
                logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            
            # If we reach here, something went wrong with the HF API call
            return None
            
        except Exception as e:
            logging.error(f"Error in Hugging Face emotion detection: {str(e)}")
            return None
    
    def _detect_with_local_features(self, audio_path: str) -> Dict[str, Any]:
        """Use local feature extraction for emotion detection"""
        # Extract audio features
        features = self._extract_audio_features(audio_path)
        
        # Use simple rule-based classification based on audio features
        # This is a fallback when ML models aren't available
        
        # Approximate mapping from features to emotions
        energy = features.get("energy", 0.5)
        pitch_mean = features.get("pitch_mean", 0.5)
        speech_rate = features.get("speech_rate", 0.5)
        pitch_variance = features.get("pitch_variance", 0.5)
        
        # Simple rule-based classification
        emotions = {
            "angry": 0.1,
            "disgust": 0.1,
            "fear": 0.1,
            "happy": 0.1,
            "neutral": 0.5,  # Default to neutral
            "sad": 0.1,
            "surprise": 0.1
        }
        
        # High energy often correlates with anger or happiness
        if energy > 0.7:
            emotions["angry"] += 0.3
            emotions["happy"] += 0.3
            emotions["surprise"] += 0.2
            emotions["neutral"] -= 0.2
        
        # Low energy often correlates with sadness
        if energy < 0.3:
            emotions["sad"] += 0.3
            emotions["disgust"] += 0.1
            emotions["fear"] += 0.1
            emotions["neutral"] -= 0.1
        
        # High pitch variance often indicates happiness or surprise
        if pitch_variance > 0.7:
            emotions["happy"] += 0.2
            emotions["surprise"] += 0.3
            emotions["neutral"] -= 0.2
        
        # Low pitch and low energy often indicate sadness
        if pitch_mean < 0.3 and energy < 0.4:
            emotions["sad"] += 0.3
            emotions["neutral"] -= 0.1
        
        # Fast speech rate might indicate excitement or anger
        if speech_rate > 0.7:
            emotions["angry"] += 0.1
            emotions["happy"] += 0.2
            emotions["surprise"] += 0.2
        
        # Find the highest emotion
        top_emotion = max(emotions.items(), key=lambda x: x[1])
        
        return {
            "emotion": top_emotion[0],
            "confidence": top_emotion[1],
            "all_emotions": emotions,
            "source": "local_features",
            "audio_features": features
        }
    
    def _extract_audio_features(self, audio_path: str) -> Dict[str, float]:
        """Extract acoustic features related to emotion from audio file"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Energy (volume)
            energy = np.mean(librosa.feature.rms(y=y)[0])
            energy_normalized = min(1.0, energy * 10)  # Normalize to 0-1 scale
            
            # Pitch features
            pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
            pitch_mean = 0.5  # Default
            pitch_variance = 0.5  # Default
            
            if magnitudes.size > 0:  # Check if we have valid pitch data
                # Get pitches with highest magnitude
                pitch_indices = np.argmax(magnitudes, axis=0)
                valid_pitches = []
                
                # Get valid pitches with significant magnitude
                for i, p_idx in enumerate(pitch_indices):
                    if magnitudes[p_idx, i] > 0.1:  # Only consider strong enough pitches
                        valid_pitches.append(pitches[p_idx, i])
                
                if valid_pitches:
                    pitch_mean = np.mean(valid_pitches) / 500.0  # Normalize to ~0-1 scale
                    pitch_mean = min(1.0, max(0.0, pitch_mean))  # Clamp to 0-1
                    
                    pitch_variance = np.std(valid_pitches) / 100.0  # Normalize
                    pitch_variance = min(1.0, max(0.0, pitch_variance))  # Clamp to 0-1
            
            # Speech rate estimation based on energy fluctuations
            # Count number of energy peaks as proxy for syllables
            energy_env = librosa.onset.onset_strength(y=y, sr=sr)
            peaks = librosa.util.peak_pick(energy_env, 3, 3, 3, 5, 0.5, 10)
            duration = len(y) / sr  # in seconds
            
            # Rough speech rate (syllables per second)
            speech_rate = len(peaks) / duration if duration > 0 else 0
            speech_rate_normalized = min(1.0, speech_rate / 5.0)  # Normalize (5 syllables/sec is normal)
            
            # Jitter (pitch variations)
            jitter = pitch_variance
            
            # Format all features to a 0-1 scale for easier interpretation
            return {
                "energy": float(energy_normalized),
                "pitch_mean": float(pitch_mean),
                "pitch_variance": float(pitch_variance),
                "speech_rate": float(speech_rate_normalized),
                "jitter": float(jitter)
            }
            
        except Exception as e:
            logging.error(f"Error extracting audio features: {str(e)}")
            return {
                "energy": 0.5,
                "pitch_mean": 0.5,
                "pitch_variance": 0.5,
                "speech_rate": 0.5,
                "jitter": 0.5
            }
    
    def _fallback_emotion_result(self) -> Dict[str, Any]:
        """Return a default/fallback emotion result when detection fails"""
        return {
            "emotion": "neutral",
            "confidence": 0.7,
            "all_emotions": {emotion: 0.1 for emotion in EMOTION_CATEGORIES},
            "source": "fallback",
            "audio_features": {
                "energy": 0.5,
                "pitch_mean": 0.5,
                "pitch_variance": 0.5,
                "speech_rate": 0.5,
                "jitter": 0.5
            }
        }
    
    def get_emotion_description(self, emotion: str) -> str:
        """
        Get a human-readable description of an emotion
        
        Args:
            emotion: The emotion label
            
        Returns:
            str: A description of the emotion
        """
        descriptions = {
            "angry": "expressing strong displeasure, hostility or aggression",
            "disgust": "showing a feeling of revulsion or strong disapproval",
            "fear": "expressing concern, anxiety or being afraid of something",
            "happy": "showing joy, pleasure, contentment or excitement",
            "neutral": "showing neither positive nor negative emotion, calm and balanced",
            "sad": "expressing unhappiness, sorrow, grief or disappointment",
            "surprise": "expressing being taken aback or astonished by something unexpected"
        }
        
        return descriptions.get(emotion.lower(), "unknown emotional state")
    
    def get_tone_feedback(self, emotion_result: Dict[str, Any]) -> str:
        """
        Generate feedback about the detected voice tone
        
        Args:
            emotion_result: The result from emotion detection
            
        Returns:
            str: Human-readable feedback about the voice tone
        """
        emotion = emotion_result.get("emotion", "neutral")
        confidence = emotion_result.get("confidence", 0.5)
        features = emotion_result.get("audio_features", {})
        
        energy = features.get("energy", 0.5)
        pitch = features.get("pitch_mean", 0.5)
        speech_rate = features.get("speech_rate", 0.5)
        pitch_variance = features.get("pitch_variance", 0.5)
        
        feedback = [f"Your voice sounds {emotion} with {int(confidence*100)}% confidence."]
        
        # Add details about vocal characteristics
        if energy > 0.7:
            feedback.append("Your voice is energetic and projecting strongly.")
        elif energy < 0.3:
            feedback.append("Your voice is quiet and soft.")
        
        if pitch > 0.7:
            feedback.append("Your tone is higher-pitched than average.")
        elif pitch < 0.3:
            feedback.append("Your tone is lower-pitched than average.")
        
        if speech_rate > 0.7:
            feedback.append("You're speaking quite rapidly.")
        elif speech_rate < 0.3:
            feedback.append("You're speaking slowly and deliberately.")
        
        if pitch_variance > 0.7:
            feedback.append("Your voice has expressive pitch variations.")
        elif pitch_variance < 0.3:
            feedback.append("Your voice has minimal pitch variation (monotone).")
        
        return " ".join(feedback)


# Create a singleton instance
detector = VoiceEmotionDetector()

def detect_emotion_from_audio(audio_data: bytes) -> Dict[str, Any]:
    """
    Wrapper function to detect emotion from audio using the detector
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Dict with emotion detection results
    """
    return detector.detect_emotion_from_audio(audio_data)

def get_tone_feedback(emotion_result: Dict[str, Any]) -> str:
    """
    Generate human-readable feedback about detected voice tone
    
    Args:
        emotion_result: Result from emotion detection
        
    Returns:
        str: Feedback about the voice tone
    """
    return detector.get_tone_feedback(emotion_result)