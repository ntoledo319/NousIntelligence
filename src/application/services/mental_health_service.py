from typing import Dict, Any, List
from src.application.services.mood_entry_service import MoodEntryService
from src.application.services.thought_record_service import ThoughtRecordService
import logging

logger = logging.getLogger(__name__)

class MentalHealthService:
    def __init__(self, mood_service: MoodEntryService, thought_service: ThoughtRecordService):
        self.mood_service = mood_service
        self.thought_service = thought_service
    
    def analyze_mood_patterns(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze mood patterns over time"""
        moods = self.mood_service.get_recent(user_id, days)
        # Analysis logic here
        return {
            'average_mood': self._calculate_average_mood(moods),
            'mood_trend': self._calculate_trend(moods),
            'recommendations': self._get_recommendations(moods)
        }
    
    def get_therapeutic_insights(self, user_id: str) -> Dict[str, Any]:
        """Get therapeutic insights"""
        thoughts = self.thought_service.get_recent(user_id, 7)
        moods = self.mood_service.get_recent(user_id, 7)
        
        return {
            'common_triggers': self._identify_triggers(thoughts),
            'cognitive_patterns': self._analyze_patterns(thoughts),
            'mood_correlation': self._correlate_mood_thoughts(moods, thoughts)
        }
    
    def _calculate_average_mood(self, moods):
        if not moods:
            return 5.0
        return sum(mood.get('rating', 5) for mood in moods) / len(moods)
    
    def _calculate_trend(self, moods):
        # Simple trend calculation
        if len(moods) < 2:
            return 'stable'
        recent = moods[-5:]
        older = moods[-10:-5] if len(moods) >= 10 else moods[:-5]
        
        if not older:
            return 'stable'
            
        recent_avg = sum(m.get('rating', 5) for m in recent) / len(recent)
        older_avg = sum(m.get('rating', 5) for m in older) / len(older)
        
        if recent_avg > older_avg + 0.5:
            return 'improving'
        elif recent_avg < older_avg - 0.5:
            return 'declining'
        return 'stable'
    
    def _get_recommendations(self, moods):
        return [
            "Continue tracking your mood daily",
            "Consider exploring coping skills",
            "Practice mindfulness exercises"
        ]
