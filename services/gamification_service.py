"""
Gamification Service

This service handles gamification features including achievements, badges,
points, streaks, challenges, and leaderboards.

@module services.gamification_service  
@context_boundary Gamification System
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import and_, or_, func
from database import db
from models.gamification_models import (
    Achievement, UserAchievement, WellnessStreak, UserPoints,
    PointTransaction, Leaderboard, Challenge, ChallengeParticipation
)
from models.user import User
from utils.notification_service import NotificationService

logger = logging.getLogger(__name__)


class GamificationService:
    """Service for managing gamification and engagement features"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.point_values = {
            'mood_log': 5,
            'dbt_skill': 10,
            'cbt_exercise': 10,
            'meditation': 15,
            'journal_entry': 10,
            'support_given': 5,
            'goal_completed': 20,
            'daily_check_in': 5,
            'habit_completed': 5
        }
        logger.info("Gamification Service initialized")
    
    # === Achievement Methods ===
    
    def check_and_award_achievements(self, user_id: str, action_type: str, 
                                   action_value: int = 1) -> List[Achievement]:
        """
        Check if user has earned any achievements based on their action
        
        @ai_prompt Call this after any user action to check for new achievements
        """
        try:
            earned_achievements = []
            
            # Get all active achievements for this action type
            relevant_achievements = Achievement.query.filter_by(
                criteria_metric=action_type,
                is_active=True
            ).all()
            
            for achievement in relevant_achievements:
                # Check if already earned
                existing = UserAchievement.query.filter_by(
                    user_id=user_id,
                    achievement_id=achievement.id
                ).first()
                
                if existing:
                    continue
                
                # Check if criteria met
                if self._check_achievement_criteria(user_id, achievement, action_value):
                    # Award achievement
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id
                    )
                    db.session.add(user_achievement)
                    
                    # Award points
                    self.add_points(user_id, achievement.points, 'achievement', 
                                  f"Earned: {achievement.name}")
                    
                    earned_achievements.append(achievement)
                    
                    # Notify user
                    self.notification_service.send_notification(
                        user_id,
                        'achievement_earned',
                        f'🏆 Achievement Unlocked: {achievement.name}!'
                    )
            
            if earned_achievements:
                db.session.commit()
                logger.info(f"User {user_id} earned {len(earned_achievements)} achievements")
            
            return earned_achievements
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            db.session.rollback()
            return []
    
    def _check_achievement_criteria(self, user_id: str, achievement: Achievement, 
                                  current_value: int) -> bool:
        """Check if achievement criteria is met"""
        if achievement.criteria_type == 'count':
            # Check total count of actions
            # This would need to query the relevant model based on criteria_metric
            return current_value >= achievement.criteria_value
        elif achievement.criteria_type == 'streak':
            # Check streak length
            streak = self.get_user_streak(user_id, achievement.criteria_metric)
            return streak and streak.current_streak >= achievement.criteria_value
        elif achievement.criteria_type == 'milestone':
            # Check specific milestone
            return current_value == achievement.criteria_value
        
        return False
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all achievements for a user"""
        try:
            user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
            
            achievements = []
            for ua in user_achievements:
                achievement_dict = ua.achievement.to_dict()
                achievement_dict['earned_at'] = ua.earned_at.isoformat()
                achievement_dict['progress'] = ua.progress
                achievements.append(achievement_dict)
            
            return achievements
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return []
    
    # === Points and Levels Methods ===
    
    def add_points(self, user_id: str, points: int, category: str = 'general', 
                  reason: str = '') -> Optional[int]:
        """
        Add points to user and return new level if leveled up
        
        ## Concept: Point System
        Users earn points for positive actions and level up
        """
        try:
            # Get or create user points record
            user_points = UserPoints.query.filter_by(user_id=user_id).first()
            if not user_points:
                user_points = UserPoints(user_id=user_id)
                db.session.add(user_points)
            
            old_level = user_points.current_level
            new_level = user_points.add_points(points, category)
            
            # Record transaction
            transaction = PointTransaction(
                user_id=user_id,
                points=points,
                transaction_type='earned',
                reason=reason,
                category=category
            )
            db.session.add(transaction)
            db.session.commit()
            
            # Check if leveled up
            if new_level > old_level:
                self.notification_service.send_notification(
                    user_id,
                    'level_up',
                    f'🎉 Level Up! You reached level {new_level}!'
                )
                return new_level
            
            return None
            
        except Exception as e:
            logger.error(f"Error adding points: {e}")
            db.session.rollback()
            return None
    
    def get_user_points_summary(self, user_id: str) -> Dict[str, Any]:
        """Get user's points and level information"""
        try:
            user_points = UserPoints.query.filter_by(user_id=user_id).first()
            if not user_points:
                return {
                    'total_points': 0,
                    'current_level': 1,
                    'points_to_next_level': 100,
                    'category_breakdown': {}
                }
            
            return {
                'total_points': user_points.total_points,
                'current_level': user_points.current_level,
                'points_to_next_level': user_points.points_to_next_level - user_points.total_points,
                'category_breakdown': {
                    'wellness': user_points.wellness_points,
                    'social': user_points.social_points,
                    'learning': user_points.learning_points,
                    'consistency': user_points.consistency_points
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting points summary: {e}")
            return {}
    
    # === Streak Methods ===
    
    def update_streak(self, user_id: str, streak_type: str) -> Optional[WellnessStreak]:
        """Update a user's streak for a specific activity"""
        try:
            streak = WellnessStreak.query.filter_by(
                user_id=user_id,
                streak_type=streak_type
            ).first()
            
            if not streak:
                streak = WellnessStreak(
                    user_id=user_id,
                    streak_type=streak_type
                )
                db.session.add(streak)
            
            old_streak = streak.current_streak
            new_streak = streak.check_and_update()
            
            db.session.commit()
            
            # Check for streak milestones
            if new_streak in [7, 30, 100, 365]:
                self.check_and_award_achievements(user_id, f'{streak_type}_streak', new_streak)
            
            # Award bonus points for maintaining streaks
            if new_streak > old_streak and new_streak > 1:
                bonus_points = min(new_streak, 20)  # Cap at 20 points
                self.add_points(user_id, bonus_points, 'consistency', 
                              f'{streak_type} streak: {new_streak} days')
            
            return streak
            
        except Exception as e:
            logger.error(f"Error updating streak: {e}")
            db.session.rollback()
            return None
    
    def get_user_streak(self, user_id: str, streak_type: str) -> Optional[WellnessStreak]:
        """Get a specific streak for a user"""
        try:
            return WellnessStreak.query.filter_by(
                user_id=user_id,
                streak_type=streak_type
            ).first()
        except Exception as e:
            logger.error(f"Error getting streak: {e}")
            return None
    
    def get_all_user_streaks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all streaks for a user"""
        try:
            streaks = WellnessStreak.query.filter_by(user_id=user_id).all()
            
            return [{
                'streak_type': s.streak_type,
                'current_streak': s.current_streak,
                'longest_streak': s.longest_streak,
                'last_activity': s.last_activity_date.isoformat() if s.last_activity_date else None
            } for s in streaks]
            
        except Exception as e:
            logger.error(f"Error getting all streaks: {e}")
            return []
    
    # === Leaderboard Methods ===
    
    def update_leaderboards(self) -> None:
        """Update all leaderboards (should be run periodically)"""
        try:
            # Update weekly leaderboard
            self._update_leaderboard_period('weekly', 
                                          datetime.utcnow().date() - timedelta(days=7),
                                          datetime.utcnow().date())
            
            # Update monthly leaderboard
            first_day = datetime.utcnow().date().replace(day=1)
            self._update_leaderboard_period('monthly', first_day, datetime.utcnow().date())
            
            logger.info("Leaderboards updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating leaderboards: {e}")
    
    def _update_leaderboard_period(self, period_type: str, start_date: date, end_date: date):
        """Update leaderboard for a specific period"""
        # Get all users with points in this period
        user_scores = db.session.query(
            PointTransaction.user_id,
            func.sum(PointTransaction.points).label('total_points')
        ).filter(
            PointTransaction.created_at >= start_date,
            PointTransaction.created_at <= end_date,
            PointTransaction.transaction_type == 'earned'
        ).group_by(PointTransaction.user_id).all()
        
        # Clear existing entries for this period
        Leaderboard.query.filter_by(
            leaderboard_type=period_type,
            period_start=start_date,
            period_end=end_date
        ).delete()
        
        # Create new entries
        for rank, (user_id, score) in enumerate(sorted(user_scores, 
                                                      key=lambda x: x[1], 
                                                      reverse=True), 1):
            entry = Leaderboard(
                user_id=user_id,
                leaderboard_type=period_type,
                category='overall',
                score=score,
                rank=rank,
                period_start=start_date,
                period_end=end_date
            )
            db.session.add(entry)
        
        db.session.commit()
    
    def get_leaderboard(self, period_type: str = 'weekly', 
                       category: str = 'overall', limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard entries"""
        try:
            # Get most recent period
            latest_entry = Leaderboard.query.filter_by(
                leaderboard_type=period_type,
                category=category
            ).order_by(Leaderboard.period_end.desc()).first()
            
            if not latest_entry:
                return []
            
            entries = Leaderboard.query.filter_by(
                leaderboard_type=period_type,
                category=category,
                period_start=latest_entry.period_start,
                period_end=latest_entry.period_end
            ).order_by(Leaderboard.rank).limit(limit).all()
            
            leaderboard = []
            for entry in entries:
                user = User.query.get(entry.user_id)
                if user:
                    leaderboard.append({
                        'rank': entry.rank,
                        'user_id': entry.user_id,
                        'username': user.username,
                        'score': entry.score,
                        'period': f"{entry.period_start} to {entry.period_end}"
                    })
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    # === Challenge Methods ===
    
    def create_challenge(self, name: str, description: str, challenge_type: str,
                        category: str, start_date: datetime, end_date: datetime,
                        points_reward: int = 50) -> Optional[Challenge]:
        """Create a new challenge"""
        try:
            challenge = Challenge(
                name=name,
                description=description,
                challenge_type=challenge_type,
                category=category,
                start_date=start_date,
                end_date=end_date,
                points_reward=points_reward
            )
            db.session.add(challenge)
            db.session.commit()
            
            logger.info(f"Challenge '{name}' created")
            return challenge
            
        except Exception as e:
            logger.error(f"Error creating challenge: {e}")
            db.session.rollback()
            return None
    
    def join_challenge(self, user_id: str, challenge_id: int) -> bool:
        """Join a challenge"""
        try:
            challenge = Challenge.query.get(challenge_id)
            if not challenge or not challenge.is_active:
                return False
            
            # Check if already participating
            existing = ChallengeParticipation.query.filter_by(
                user_id=user_id,
                challenge_id=challenge_id
            ).first()
            
            if existing:
                return True
            
            participation = ChallengeParticipation(
                user_id=user_id,
                challenge_id=challenge_id
            )
            db.session.add(participation)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error joining challenge: {e}")
            db.session.rollback()
            return False
    
    def get_active_challenges(self) -> List[Challenge]:
        """Get all active challenges"""
        try:
            return Challenge.query.filter(
                Challenge.is_active == True,
                Challenge.start_date <= datetime.utcnow(),
                Challenge.end_date >= datetime.utcnow()
            ).all()
        except Exception as e:
            logger.error(f"Error getting active challenges: {e}")
            return []


# AI-GENERATED [2024-12-01]
# TRAINING_DATA: Gamification best practices from successful wellness apps
# @see models.gamification_models for database schema 