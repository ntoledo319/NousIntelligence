"""
AI Fallback Service
Provides fallback implementations when AI services are unavailable
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AIFallbackService:
    """Fallback service for AI operations"""
    
    def __init__(self):
        self.fallback_responses = {
            'general': "I understand you're looking for assistance. While the AI service is temporarily unavailable, please try again in a moment.",
            'code': "Code assistance is temporarily unavailable. Please refer to documentation or try again later.",
            'analysis': "Analysis capabilities are temporarily unavailable. Please try again later."
        }
    
    def get_fallback_response(self, prompt: str, response_type: str = 'general') -> Dict[str, Any]:
        """Get appropriate fallback response"""
        return {
            'response': self.fallback_responses.get(response_type, self.fallback_responses['general']),
            'provider': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'fallback': True
        }
    
    def detect_emotion_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback emotion detection"""
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'fallback': True
        }
    
    def analyze_sentiment_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis"""
        return {
            'sentiment': 'neutral',
            'score': 0.0,
            'fallback': True
        }

# Global fallback instance
ai_fallback_service = AIFallbackService()
