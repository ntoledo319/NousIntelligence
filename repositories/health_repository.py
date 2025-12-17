"""
Health Repository - Data access layer for health-related operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from models.database import db
from models.health_models import (
    DBTSkillRecommendation, DBTSkillLog, DBTDiaryCard,
    DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack,
    AAAchievement, AABigBook
)

class HealthRepository:
    """Repository for health-related data access operations"""

    # DBT Skill methods
    @staticmethod
    def create_dbt_skill_log(user_id: str, skill_data: Dict[str, Any]) -> DBTSkillLog:
        """Create a new DBT skill log entry"""
        skill_log = DBTSkillLog(user_id=user_id, **skill_data)
        db.session.add(skill_log)
        db.session.commit()
        return skill_log

    @staticmethod
    def get_user_dbt_skills(user_id: str, limit: Optional[int] = None) -> List[DBTSkillLog]:
        """Get DBT skills for a user"""
        query = DBTSkillLog.query.filter_by(user_id=user_id).order_by(DBTSkillLog.timestamp.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_dbt_skill_recommendations(situation_type: Optional[str] = None, limit: int = 10) -> List[DBTSkillRecommendation]:
        """Get DBT skill recommendations"""
        query = DBTSkillRecommendation.query
        if situation_type:
            query = query.filter_by(situation_type=situation_type)
        return query.order_by(DBTSkillRecommendation.effectiveness_score.desc()).limit(limit).all()

    # DBT Diary Card methods
    @staticmethod
    def create_diary_card(user_id: str, diary_data: Dict[str, Any]) -> DBTDiaryCard:
        """Create a new diary card entry"""
        diary_card = DBTDiaryCard(user_id=user_id, **diary_data)
        db.session.add(diary_card)
        db.session.commit()
        return diary_card

    @staticmethod
    def get_user_diary_cards(user_id: str, limit: Optional[int] = None) -> List[DBTDiaryCard]:
        """Get diary cards for a user"""
        query = DBTDiaryCard.query.filter_by(user_id=user_id).order_by(DBTDiaryCard.date.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    # Emotion tracking methods
    @staticmethod
    def create_emotion_track(user_id: str, emotion_data: Dict[str, Any]) -> DBTEmotionTrack:
        """Create a new emotion tracking entry"""
        emotion_track = DBTEmotionTrack(user_id=user_id, **emotion_data)
        db.session.add(emotion_track)
        db.session.commit()
        return emotion_track

    @staticmethod
    def get_user_emotion_tracks(user_id: str, limit: Optional[int] = None) -> List[DBTEmotionTrack]:
        """Get emotion tracks for a user"""
        query = DBTEmotionTrack.query.filter_by(user_id=user_id).order_by(DBTEmotionTrack.timestamp.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    # AA Big Book methods
    @staticmethod
    def search_aa_content(query: str, limit: int = 10) -> List[AABigBook]:
        """Search AA Big Book content"""
        return AABigBook.search_content(query, limit)

    @staticmethod
    def get_aa_chapter(chapter_number: int) -> List[AABigBook]:
        """Get content from specific AA chapter"""
        return AABigBook.query.filter_by(chapter_number=chapter_number).all()

    @staticmethod
    def create_aa_content(content_data: Dict[str, Any]) -> AABigBook:
        """Create new AA content entry"""
        aa_content = AABigBook(**content_data)
        db.session.add(aa_content)
        db.session.commit()
        return aa_content

    # Crisis resources methods
    @staticmethod
    def get_crisis_resources(location: Optional[str] = None) -> List[DBTCrisisResource]:
        """Get crisis resources, optionally filtered by location"""
        query = DBTCrisisResource.query
        if location:
            query = query.filter(DBTCrisisResource.location.ilike(f"%{location}%"))
        return query.all()

    @staticmethod
    def create_crisis_resource(resource_data: Dict[str, Any]) -> DBTCrisisResource:
        """Create a new crisis resource"""
        resource = DBTCrisisResource(**resource_data)
        db.session.add(resource)
        db.session.commit()
        return resource