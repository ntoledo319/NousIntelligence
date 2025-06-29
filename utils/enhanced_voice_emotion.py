"""
Enhanced Voice Emotion Detection - Real AI-Powered Analysis
Implements actual emotion detection using HuggingFace and fallback systems
"""

import os
import json
import logging
import requests
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class EnhancedVoiceEmotion:
    """Real AI-powered voice emotion detection system"""
    
    def __init__(self):
        self.huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")
        self.cache_db_path = "voice_emotion_cache.db"
        self.init_cache_database()
        
        # Emotion models (HuggingFace)
        self.text_emotion_model = "j-hartmann/emotion-english-distilroberta-base"
        self.audio_emotion_model = "superb/wav2vec2-base-superb-er"
        
        # Usage tracking
        self.daily_requests = 0
        self.monthly_cost = 0.0
        
        logger.info("Enhanced Voice Emotion system initialized")

    def init_cache_database(self):
        """Initialize emotion analysis cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS emotion_cache (
                    id INTEGER PRIMARY KEY,
                    input_hash TEXT UNIQUE,
                    input_type TEXT,
                    emotions TEXT,
                    confidence REAL,
                    provider TEXT,
                    created_at TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize emotion cache: {e}")

    def analyze_text_emotion(self, text: str) -> Dict[str, Any]:
        """Analyze emotion from text using AI"""
        
        # Check cache first
        cached_result = self._get_cached_emotion(text, "text")
        if cached_result:
            return cached_result
        
        try:
            if self.huggingface_key and self.daily_requests < 900:  # Stay under free limit
                result = self._huggingface_text_emotion(text)
                self.daily_requests += 1
            else:
                result = self._fallback_text_emotion(text)
            
            # Cache the result
            self._cache_emotion_result(text, "text", result)
            return result
            
        except Exception as e:
            logger.error(f"Text emotion analysis error: {e}")
            return self._fallback_text_emotion(text)

    def analyze_voice_emotion(self, audio_data: bytes = None, text_fallback: str = None) -> Dict[str, Any]:
        """Analyze emotion from voice/audio data"""
        
        if audio_data:
            # Check cache
            audio_hash = hashlib.sha256(audio_data).hexdigest()[:16]
            cached_result = self._get_cached_emotion(audio_hash, "audio")
            if cached_result:
                return cached_result
        
        try:
            if audio_data and self.huggingface_key and self.daily_requests < 900:
                result = self._huggingface_audio_emotion(audio_data)
                self.daily_requests += 1
                if audio_data:
                    self._cache_emotion_result(audio_hash, "audio", result)
            elif text_fallback:
                # Use text analysis as fallback
                result = self.analyze_text_emotion(text_fallback)
                result["method"] = "text_fallback"
            else:
                result = self._fallback_voice_emotion()
            
            return result
            
        except Exception as e:
            logger.error(f"Voice emotion analysis error: {e}")
            return self._fallback_voice_emotion()

    def _huggingface_text_emotion(self, text: str) -> Dict[str, Any]:
        """HuggingFace text emotion analysis"""
        headers = {"Authorization": f"Bearer {self.huggingface_key}"}
        
        api_url = f"https://api-inference.huggingface.co/models/{self.text_emotion_model}"
        
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": text},
            timeout=30
        )
        
        if response.status_code == 200:
            emotions = response.json()
            
            # Process HuggingFace response
            if isinstance(emotions, list) and len(emotions) > 0:
                emotion_scores = emotions[0]
                
                # Get top emotion
                top_emotion = max(emotion_scores, key=lambda x: x['score'])
                
                return {
                    "primary_emotion": top_emotion['label'].lower(),
                    "confidence": top_emotion['score'],
                    "all_emotions": {e['label'].lower(): e['score'] for e in emotion_scores},
                    "provider": "huggingface",
                    "method": "text_ai",
                    "intensity": self._calculate_intensity(top_emotion['score']),
                    "success": True
                }
        
        raise Exception(f"HuggingFace API error: {response.status_code}")

    def _huggingface_audio_emotion(self, audio_data: bytes) -> Dict[str, Any]:
        """HuggingFace audio emotion analysis"""
        headers = {"Authorization": f"Bearer {self.huggingface_key}"}
        
        api_url = f"https://api-inference.huggingface.co/models/{self.audio_emotion_model}"
        
        response = requests.post(
            api_url,
            headers=headers,
            data=audio_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            return {
                "primary_emotion": result.get("label", "neutral").lower(),
                "confidence": result.get("score", 0.5),
                "provider": "huggingface",
                "method": "audio_ai",
                "intensity": self._calculate_intensity(result.get("score", 0.5)),
                "success": True
            }
        
        raise Exception(f"HuggingFace Audio API error: {response.status_code}")

    def _fallback_text_emotion(self, text: str) -> Dict[str, Any]:
        """Enhanced fallback text emotion analysis"""
        text_lower = text.lower()
        
        # Enhanced emotion keywords
        emotion_patterns = {
            "joy": ["happy", "joyful", "excited", "thrilled", "elated", "cheerful", "delighted", "pleased"],
            "sadness": ["sad", "depressed", "unhappy", "miserable", "heartbroken", "melancholy", "down"],
            "anger": ["angry", "furious", "mad", "irritated", "annoyed", "rage", "frustrated", "livid"],
            "fear": ["scared", "afraid", "terrified", "anxious", "worried", "nervous", "panic", "frightened"],
            "surprise": ["surprised", "amazed", "shocked", "astonished", "startled", "unexpected"],
            "disgust": ["disgusted", "revolted", "sick", "nauseous", "repulsed", "appalled"],
            "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil", "composed", "zen"],
            "neutral": ["okay", "fine", "normal", "regular", "standard", "typical"]
        }
        
        emotion_scores = {}
        
        for emotion, keywords in emotion_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = min(1.0, score / len(keywords) * 3)  # Scale score
        
        if not emotion_scores:
            primary_emotion = "neutral"
            confidence = 0.5
        else:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[primary_emotion]
        
        return {
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "all_emotions": emotion_scores,
            "provider": "local_analysis",
            "method": "keyword_matching",
            "intensity": self._calculate_intensity(confidence),
            "success": True
        }

    def _fallback_voice_emotion(self) -> Dict[str, Any]:
        """Fallback when voice analysis isn't available"""
        return {
            "primary_emotion": "neutral",
            "confidence": 0.3,
            "provider": "fallback",
            "method": "unavailable",
            "intensity": "low",
            "message": "Voice emotion analysis requires audio data or HuggingFace API key",
            "success": False
        }

    def _calculate_intensity(self, confidence: float) -> str:
        """Calculate emotion intensity based on confidence"""
        if confidence >= 0.8:
            return "very_high"
        elif confidence >= 0.6:
            return "high"
        elif confidence >= 0.4:
            return "medium"
        elif confidence >= 0.2:
            return "low"
        else:
            return "very_low"

    def _get_cached_emotion(self, input_data: str, input_type: str) -> Optional[Dict[str, Any]]:
        """Get cached emotion analysis"""
        try:
            input_hash = hashlib.sha256(f"{input_data}_{input_type}".encode()).hexdigest()
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT emotions, confidence, provider 
                FROM emotion_cache 
                WHERE input_hash = ? AND input_type = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (input_hash, input_type))
            
            result = cursor.fetchone()
            
            if result:
                cursor.execute('''
                    UPDATE emotion_cache 
                    SET use_count = use_count + 1 
                    WHERE input_hash = ?
                ''', (input_hash,))
                conn.commit()
                
                emotions_data = json.loads(result[0])
                emotions_data["cached"] = True
                conn.close()
                return emotions_data
                
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    def _cache_emotion_result(self, input_data: str, input_type: str, result: Dict[str, Any]):
        """Cache emotion analysis result"""
        try:
            input_hash = hashlib.sha256(f"{input_data}_{input_type}".encode()).hexdigest()
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO emotion_cache 
                (input_hash, input_type, emotions, confidence, provider, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                input_hash,
                input_type,
                json.dumps(result),
                result.get("confidence", 0.5),
                result.get("provider", "unknown"),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    def get_emotion_insights(self, emotion_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from emotion history"""
        if not emotion_history:
            return {"insights": "No emotion data available"}
        
        # Analyze patterns
        emotions = [e.get("primary_emotion", "neutral") for e in emotion_history]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        most_common = max(emotion_counts, key=emotion_counts.get)
        avg_confidence = sum(e.get("confidence", 0.5) for e in emotion_history) / len(emotion_history)
        
        return {
            "most_common_emotion": most_common,
            "emotion_distribution": emotion_counts,
            "average_confidence": avg_confidence,
            "total_analyses": len(emotion_history),
            "insights": f"Most frequent emotion: {most_common}. Average confidence: {avg_confidence:.2f}",
            "recommendations": self._get_emotion_recommendations(most_common, avg_confidence)
        }

    def _get_emotion_recommendations(self, primary_emotion: str, confidence: float) -> List[str]:
        """Get recommendations based on emotion analysis"""
        recommendations = {
            "sadness": [
                "Consider practicing mindfulness or meditation",
                "Reach out to friends or family for support",
                "Engage in physical activity or exercise",
                "Consider speaking with a mental health professional"
            ],
            "anger": [
                "Try deep breathing exercises",
                "Take a short break or walk",
                "Practice progressive muscle relaxation",
                "Consider the source of frustration and address it constructively"
            ],
            "anxiety": [
                "Use grounding techniques (5-4-3-2-1 method)",
                "Practice controlled breathing",
                "Challenge negative thought patterns",
                "Consider anxiety management techniques"
            ],
            "fear": [
                "Identify the source of fear",
                "Practice gradual exposure if appropriate",
                "Use relaxation techniques",
                "Seek support if fear is overwhelming"
            ],
            "joy": [
                "Savor this positive moment",
                "Share your happiness with others",
                "Use this energy for productive activities",
                "Practice gratitude for positive experiences"
            ]
        }
        
        return recommendations.get(primary_emotion, [
            "Continue monitoring your emotional well-being",
            "Practice regular self-care",
            "Maintain healthy communication with others"
        ])

# Global instance
enhanced_voice_emotion = EnhancedVoiceEmotion()

# Convenience functions
def analyze_text_emotion(text: str) -> Dict[str, Any]:
    """Analyze emotion from text"""
    return enhanced_voice_emotion.analyze_text_emotion(text)

def analyze_voice_emotion(audio_data: bytes = None, text_fallback: str = None) -> Dict[str, Any]:
    """Analyze emotion from voice"""
    return enhanced_voice_emotion.analyze_voice_emotion(audio_data, text_fallback)

def get_emotion_insights(emotion_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get emotion insights from history"""
    return enhanced_voice_emotion.get_emotion_insights(emotion_history)