"""
Therapeutic Repository
Data access layer for CBT, DBT, and AA features
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from models.database import db
from models.health_models import (
    DBTSkillLog, DBTSkillRecommendation, DBTCrisisResource,
    DBTSkillCategory, AAAchievement, DBTDiaryCard
)
import logging

logger = logging.getLogger(__name__)


class TherapeuticRepository:
    """Repository for all therapeutic data access"""
    
    # ===== DBT SKILL LOGS =====
    
    @staticmethod
    def create_skill_log(user_id: int, skill_name: str, category: str,
                        situation: str = '', effectiveness: int = 5,
                        notes: str = '') -> Optional[DBTSkillLog]:
        """Create a new DBT skill log entry"""
        try:
            log = DBTSkillLog(
                user_id=user_id,
                skill_name=skill_name,
                category=category,
                situation=situation,
                effectiveness=effectiveness,
                notes=notes
            )
            db.session.add(log)
            db.session.commit()
            logger.info(f"Created skill log for user {user_id}: {skill_name}")
            return log
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating skill log: {e}")
            return None
    
    @staticmethod
    def get_user_skill_logs(user_id: int, limit: int = 50) -> List[DBTSkillLog]:
        """Get recent skill logs for a user"""
        try:
            return DBTSkillLog.query.filter_by(user_id=user_id)\
                .order_by(desc(DBTSkillLog.timestamp))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting skill logs: {e}")
            return []
    
    @staticmethod
    def get_skill_effectiveness(user_id: int, skill_name: str) -> Optional[float]:
        """Calculate average effectiveness for a specific skill"""
        try:
            result = db.session.query(func.avg(DBTSkillLog.effectiveness))\
                .filter_by(user_id=user_id, skill_name=skill_name)\
                .scalar()
            return float(result) if result else None
        except Exception as e:
            logger.error(f"Error calculating effectiveness: {e}")
            return None
    
    @staticmethod
    def get_skill_usage_stats(user_id: int, days: int = 30) -> Dict[str, int]:
        """Get skill usage statistics for the past N days"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            results = db.session.query(
                DBTSkillLog.skill_name,
                func.count(DBTSkillLog.id)
            ).filter(
                DBTSkillLog.user_id == user_id,
                DBTSkillLog.timestamp >= cutoff
            ).group_by(DBTSkillLog.skill_name).all()
            
            return {skill: count for skill, count in results}
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {}
    
    # ===== DBT SKILL RECOMMENDATIONS =====
    
    @staticmethod
    def get_recommendations(user_id: int, situation_type: str = None) -> List[DBTSkillRecommendation]:
        """Get skill recommendations, optionally filtered by situation"""
        try:
            query = DBTSkillRecommendation.query.filter_by(user_id=user_id)
            if situation_type:
                query = query.filter_by(situation_type=situation_type)
            return query.order_by(desc(DBTSkillRecommendation.effectiveness_score)).all()
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    @staticmethod
    def update_recommendation_effectiveness(recommendation_id: int, 
                                          effectiveness: float) -> bool:
        """Update effectiveness score for a recommendation"""
        try:
            rec = DBTSkillRecommendation.query.get(recommendation_id)
            if rec:
                # Running average
                total = rec.effectiveness_score * rec.usage_count
                rec.usage_count += 1
                rec.effectiveness_score = (total + effectiveness) / rec.usage_count
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating recommendation: {e}")
            return False
    
    # ===== CRISIS RESOURCES =====
    
    @staticmethod
    def get_crisis_resources(user_id: int, emergency_only: bool = False) -> List[DBTCrisisResource]:
        """Get crisis resources for a user"""
        try:
            query = DBTCrisisResource.query.filter_by(user_id=user_id)
            if emergency_only:
                query = query.filter_by(is_emergency=True)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting crisis resources: {e}")
            return []
    
    @staticmethod
    def add_crisis_resource(user_id: int, name: str, contact_info: str,
                          resource_type: str, is_emergency: bool = False,
                          notes: str = '') -> Optional[DBTCrisisResource]:
        """Add a new crisis resource"""
        try:
            resource = DBTCrisisResource(
                user_id=user_id,
                name=name,
                contact_info=contact_info,
                resource_type=resource_type,
                is_emergency=is_emergency,
                notes=notes
            )
            db.session.add(resource)
            db.session.commit()
            return resource
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding crisis resource: {e}")
            return None
    
    # ===== DBT DIARY CARDS =====
    
    @staticmethod
    def create_diary_card(user_id: int, date: datetime, emotions: Dict,
                         urges: Dict, skills_used: List[str],
                         notes: str = '') -> Optional[DBTDiaryCard]:
        """Create a DBT diary card entry"""
        try:
            card = DBTDiaryCard(
                user_id=user_id,
                date=date,
                emotions=emotions,
                urges=urges,
                skills_used=skills_used,
                notes=notes
            )
            db.session.add(card)
            db.session.commit()
            return card
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating diary card: {e}")
            return None
    
    @staticmethod
    def get_diary_cards(user_id: int, start_date: datetime = None,
                       end_date: datetime = None) -> List[DBTDiaryCard]:
        """Get diary cards for a user within a date range"""
        try:
            query = DBTDiaryCard.query.filter_by(user_id=user_id)
            if start_date:
                query = query.filter(DBTDiaryCard.date >= start_date)
            if end_date:
                query = query.filter(DBTDiaryCard.date <= end_date)
            return query.order_by(desc(DBTDiaryCard.date)).all()
        except Exception as e:
            logger.error(f"Error getting diary cards: {e}")
            return []
    
    # ===== AA ACHIEVEMENTS =====
    
    @staticmethod
    def award_achievement(user_id: int, achievement_type: str,
                         title: str, description: str,
                         points: int = 0) -> Optional[AAAchievement]:
        """Award an AA achievement"""
        try:
            achievement = AAAchievement(
                user_id=user_id,
                achievement_type=achievement_type,
                title=title,
                description=description,
                points=points
            )
            db.session.add(achievement)
            db.session.commit()
            logger.info(f"Awarded achievement to user {user_id}: {title}")
            return achievement
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error awarding achievement: {e}")
            return None
    
    @staticmethod
    def get_user_achievements(user_id: int) -> List[AAAchievement]:
        """Get all achievements for a user"""
        try:
            return AAAchievement.query.filter_by(user_id=user_id)\
                .order_by(desc(AAAchievement.earned_at))\
                .all()
        except Exception as e:
            logger.error(f"Error getting achievements: {e}")
            return []
    
    @staticmethod
    def get_total_points(user_id: int) -> int:
        """Calculate total achievement points for a user"""
        try:
            result = db.session.query(func.sum(AAAchievement.points))\
                .filter_by(user_id=user_id)\
                .scalar()
            return int(result) if result else 0
        except Exception as e:
            logger.error(f"Error calculating total points: {e}")
            return 0
