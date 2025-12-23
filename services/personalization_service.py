"""
Personalization Service

Manages user context, sentiment analysis, and adaptive profiling to
tailor the therapeutic experience.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from models.database import db
from models.therapeutic import MoodLog, TherapyProfile
from models.user import User

# Try to import textblob for sentiment, else fallback
try:
    from textblob import TextBlob
    _HAS_TEXTBLOB = True
except ImportError:
    _HAS_TEXTBLOB = False

logger = logging.getLogger(__name__)

class PersonalizationService:
    def __init__(self):
        pass

    def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """
        Aggregates relevant user data for the Dialogue Manager / LLM.
        """
        user = User.query.get(user_id)
        if not user:
            return {}

        profile = TherapyProfile.query.filter_by(user_id=user_id).first()
        recent_moods = MoodLog.query.filter_by(user_id=user_id)\
            .order_by(MoodLog.timestamp.desc()).limit(3).all()

        context = {
            'username': user.username,
            'preferences': {},
            'goals': [],
            'recent_mood_trend': []
        }

        if profile:
            context['preferences'] = {
                'style': profile.communication_style,
                'dislikes': profile.disliked_exercises
            }
            context['goals'] = profile.goals

        if recent_moods:
            context['recent_mood_trend'] = [m.mood_label for m in recent_moods]

        return context

    def update_profile(self, user_id: int, data: Dict[str, Any]) -> None:
        """
        Updates the user's therapy profile based on interaction data.
        e.g., User says "I hate meditation" -> add to dislikes.
        """
        profile = TherapyProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = TherapyProfile(user_id=user_id)
            db.session.add(profile)

        # Example: Update dislikes
        if 'dislike' in data:
            current_dislikes = list(profile.disliked_exercises or [])
            if data['dislike'] not in current_dislikes:
                current_dislikes.append(data['dislike'])
                profile.disliked_exercises = current_dislikes

        # Example: Update goals
        if 'new_goal' in data:
            current_goals = list(profile.goals or [])
            current_goals.append(data['new_goal'])
            profile.goals = current_goals

        db.session.commit()

    def log_mood(self, user_id: int, mood: str, intensity: int, note: str = None) -> None:
        """Logs a mood entry."""
        log = MoodLog(
            user_id=user_id,
            mood_label=mood,
            intensity=intensity,
            note=note,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

    def detect_sentiment(self, text: str) -> Dict[str, float]:
        """
        Returns sentiment polarity (-1.0 to 1.0) and subjectivity (0.0 to 1.0).
        """
        if not _HAS_TEXTBLOB:
            return {'polarity': 0.0, 'subjectivity': 0.0}

        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
