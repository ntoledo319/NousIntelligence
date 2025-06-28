"""
Emotion Detection Utility
Simple emotion detection from text content for enhanced voice interface
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EmotionDetector:
    """Basic emotion detection from text patterns"""
    
    def __init__(self):
        """Initialize emotion detector with keyword patterns"""
        self.emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 'excellent', 'love', 'smile'],
            'sad': ['sad', 'unhappy', 'depressed', 'down', 'blue', 'upset', 'disappointed', 'cry', 'tears'],
            'angry': ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed', 'frustrated', 'irritated'],
            'anxious': ['anxious', 'worried', 'nervous', 'stress', 'concern', 'afraid', 'fear', 'panic'],
            'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'content'],
            'surprised': ['surprised', 'shock', 'amazed', 'astonished', 'wow'],
            'confused': ['confused', 'puzzled', 'uncertain', 'unclear', 'lost', 'unsure']
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            'very': 1.5,
            'extremely': 2.0,
            'really': 1.3,
            'quite': 1.2,
            'somewhat': 0.8,
            'a bit': 0.7,
            'slightly': 0.6
        }
        
    def analyze_text_emotion(self, text: str) -> Dict[str, Any]:
        """Analyze emotion from text content"""
        if not text:
            return {'emotion': 'neutral', 'confidence': 0.0}
        
        text_lower = text.lower()
        emotion_scores = {}
        
        # Calculate emotion scores based on keyword matches
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    base_score = 1.0
                    
                    # Check for intensity modifiers
                    for modifier, multiplier in self.intensity_modifiers.items():
                        if modifier in text_lower and text_lower.find(modifier) < text_lower.find(keyword):
                            base_score *= multiplier
                            break
                    
                    score += base_score
            
            emotion_scores[emotion] = score
        
        # Find dominant emotion
        if not emotion_scores or max(emotion_scores.values()) == 0:
            return {'emotion': 'neutral', 'confidence': 0.5}
        
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        emotion = dominant_emotion[0]
        raw_score = dominant_emotion[1]
        
        # Normalize confidence (simple approach)
        confidence = min(1.0, raw_score / 3.0)  # Assume max 3 emotion words for 100% confidence
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'all_scores': emotion_scores
        }