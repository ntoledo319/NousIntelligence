"""
Personal Growth Service

This service handles personal development features including goal setting,
habit tracking, journaling, and vision boards.

@module services.personal_growth_service
@context_boundary Personal Development
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import and_, or_, func
from database import db
from models.personal_growth_models import (
    Goal, GoalMilestone, Habit, HabitEntry, JournalEntry,
    JournalAttachment, VisionBoard, VisionBoardItem, ReflectionPrompt
)
from services.gamification_service import GamificationService
from utils.notification_service import NotificationService

logger = logging.getLogger(__name__)


class PersonalGrowthService:
    """Service for managing personal growth and development features"""
    
    def __init__(self):
        self.gamification_service = GamificationService()
        self.notification_service = NotificationService()
        logger.info("Personal Growth Service initialized")
    
    # === Goal Methods ===
    
    def create_goal(self, user_id: str, title: str, description: str,
                   category: str, goal_type: str = 'long_term',
                   time_bound: Optional[date] = None,
                   parent_goal_id: Optional[int] = None) -> Optional[Goal]:
        """
        Create a new goal
        
        @ai_prompt Use this to help users set SMART goals
        """
        try:
            goal = Goal(
                user_id=user_id,
                title=title,
                description=description,
                category=category,
                goal_type=goal_type,
                time_bound=time_bound,
                parent_goal_id=parent_goal_id
            )
            db.session.add(goal)
            db.session.commit()
            
            # Award points for goal setting
            self.gamification_service.add_points(
                user_id, 10, 'learning', f'Created goal: {title}'
            )
            
            logger.info(f"Goal '{title}' created for user {user_id}")
            return goal
            
        except Exception as e:
            logger.error(f"Error creating goal: {e}")
            db.session.rollback()
            return None
    
    def update_goal_progress(self, user_id: str, goal_id: int, 
                           progress: float) -> bool:
        """Update goal progress"""
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return False
            
            old_progress = goal.progress
            goal.progress = min(progress, 100.0)
            
            # Check if goal completed
            if goal.progress >= 100.0 and old_progress < 100.0:
                goal.status = 'completed'
                goal.completed_date = date.today()
                
                # Award completion points
                self.gamification_service.add_points(
                    user_id, 50, 'learning', f'Completed goal: {goal.title}'
                )
                
                # Check achievements
                self.gamification_service.check_and_award_achievements(
                    user_id, 'goal_completed', 1
                )
                
                # Send notification
                self.notification_service.send_notification(
                    user_id, 'goal_completed',
                    f'🎯 Congratulations! You completed: {goal.title}'
                )
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating goal progress: {e}")
            db.session.rollback()
            return False
    
    def get_user_goals(self, user_id: str, status: Optional[str] = None,
                      category: Optional[str] = None) -> List[Goal]:
        """Get user's goals with optional filtering"""
        try:
            query = Goal.query.filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            if category:
                query = query.filter_by(category=category)
            
            return query.order_by(Goal.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error getting user goals: {e}")
            return []
    
    def add_goal_milestone(self, user_id: str, goal_id: int,
                         title: str, description: str,
                         target_date: Optional[date] = None) -> Optional[GoalMilestone]:
        """Add a milestone to a goal"""
        try:
            goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
            if not goal:
                return None
            
            # Get next order index
            max_order = db.session.query(func.max(GoalMilestone.order_index))\
                .filter_by(goal_id=goal_id).scalar() or 0
            
            milestone = GoalMilestone(
                goal_id=goal_id,
                title=title,
                description=description,
                target_date=target_date,
                order_index=max_order + 1
            )
            db.session.add(milestone)
            db.session.commit()
            
            return milestone
            
        except Exception as e:
            logger.error(f"Error adding milestone: {e}")
            db.session.rollback()
            return None
    
    # === Habit Methods ===
    
    def create_habit(self, user_id: str, name: str, description: str,
                    category: str, habit_type: str = 'daily',
                    frequency_days: Optional[List[str]] = None,
                    reminder_time: Optional[datetime.time] = None) -> Optional[Habit]:
        """
        Create a new habit
        
        ## Concept: Habit Tracking
        Building positive habits through consistent tracking
        """
        try:
            habit = Habit(
                user_id=user_id,
                name=name,
                description=description,
                category=category,
                habit_type=habit_type,
                frequency_days=frequency_days,
                reminder_time=reminder_time
            )
            db.session.add(habit)
            db.session.commit()
            
            logger.info(f"Habit '{name}' created for user {user_id}")
            return habit
            
        except Exception as e:
            logger.error(f"Error creating habit: {e}")
            db.session.rollback()
            return None
    
    def log_habit_completion(self, user_id: str, habit_id: int,
                           completed: bool = True, value: Optional[float] = None,
                           notes: Optional[str] = None) -> bool:
        """Log habit completion for today"""
        try:
            habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
            if not habit or not habit.is_active:
                return False
            
            today = date.today()
            
            # Check if already logged today
            existing = HabitEntry.query.filter_by(
                habit_id=habit_id,
                entry_date=today
            ).first()
            
            if existing:
                existing.completed = completed
                existing.value = value
                existing.notes = notes
            else:
                entry = HabitEntry(
                    habit_id=habit_id,
                    entry_date=today,
                    completed=completed,
                    value=value,
                    notes=notes
                )
                db.session.add(entry)
            
            db.session.commit()
            
            if completed:
                # Update streak
                self.gamification_service.update_streak(user_id, f'habit_{habit_id}')
                
                # Award points
                self.gamification_service.add_points(
                    user_id, 5, 'consistency', f'Completed habit: {habit.name}'
                )
                
                # Check achievements
                self.gamification_service.check_and_award_achievements(
                    user_id, 'habit_completed', 1
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging habit: {e}")
            db.session.rollback()
            return False
    
    def get_habit_stats(self, user_id: str, habit_id: int, 
                       days: int = 30) -> Dict[str, Any]:
        """Get habit completion statistics"""
        try:
            habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
            if not habit:
                return {}
            
            start_date = date.today() - timedelta(days=days)
            
            entries = HabitEntry.query.filter(
                HabitEntry.habit_id == habit_id,
                HabitEntry.entry_date >= start_date
            ).all()
            
            completed_count = sum(1 for e in entries if e.completed)
            
            # Calculate current streak
            streak = 0
            check_date = date.today()
            while check_date >= habit.created_at.date():
                entry = HabitEntry.query.filter_by(
                    habit_id=habit_id,
                    entry_date=check_date
                ).first()
                
                if entry and entry.completed:
                    streak += 1
                    check_date -= timedelta(days=1)
                else:
                    break
            
            return {
                'habit_name': habit.name,
                'total_days': days,
                'completed_days': completed_count,
                'completion_rate': (completed_count / days) * 100,
                'current_streak': streak,
                'entries': [{'date': e.entry_date.isoformat(), 
                           'completed': e.completed,
                           'value': e.value} for e in entries]
            }
            
        except Exception as e:
            logger.error(f"Error getting habit stats: {e}")
            return {}
    
    # === Journal Methods ===
    
    def create_journal_entry(self, user_id: str, content: str,
                           title: Optional[str] = None,
                           entry_type: str = 'general',
                           mood_rating: Optional[int] = None,
                           emotions: Optional[List[str]] = None,
                           tags: Optional[List[str]] = None) -> Optional[JournalEntry]:
        """Create a new journal entry"""
        try:
            entry = JournalEntry(
                user_id=user_id,
                title=title,
                content=content,
                entry_type=entry_type,
                mood_rating=mood_rating,
                emotions=emotions,
                tags=tags
            )
            db.session.add(entry)
            db.session.commit()
            
            # Award points for journaling
            self.gamification_service.add_points(
                user_id, 10, 'wellness', 'Created journal entry'
            )
            
            # Update journaling streak
            self.gamification_service.update_streak(user_id, 'journaling')
            
            # Check achievements
            self.gamification_service.check_and_award_achievements(
                user_id, 'journal_entry', 1
            )
            
            logger.info(f"Journal entry created for user {user_id}")
            return entry
            
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            db.session.rollback()
            return None
    
    def get_journal_entries(self, user_id: str, entry_type: Optional[str] = None,
                          limit: int = 20, offset: int = 0) -> List[JournalEntry]:
        """Get user's journal entries"""
        try:
            query = JournalEntry.query.filter_by(user_id=user_id)
            
            if entry_type:
                query = query.filter_by(entry_type=entry_type)
            
            return query.order_by(JournalEntry.created_at.desc())\
                       .limit(limit).offset(offset).all()
            
        except Exception as e:
            logger.error(f"Error getting journal entries: {e}")
            return []
    
    def get_random_reflection_prompt(self, category: Optional[str] = None) -> Optional[ReflectionPrompt]:
        """Get a random reflection prompt"""
        try:
            query = ReflectionPrompt.query.filter_by(is_active=True)
            
            if category:
                query = query.filter_by(category=category)
            
            # Get random prompt
            prompt = query.order_by(func.random()).first()
            
            if prompt:
                prompt.usage_count += 1
                db.session.commit()
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error getting reflection prompt: {e}")
            return None
    
    # === Vision Board Methods ===
    
    def create_vision_board(self, user_id: str, title: str,
                          description: str, theme: str,
                          is_public: bool = False) -> Optional[VisionBoard]:
        """Create a new vision board"""
        try:
            board = VisionBoard(
                user_id=user_id,
                title=title,
                description=description,
                theme=theme,
                is_public=is_public
            )
            db.session.add(board)
            db.session.commit()
            
            logger.info(f"Vision board '{title}' created for user {user_id}")
            return board
            
        except Exception as e:
            logger.error(f"Error creating vision board: {e}")
            db.session.rollback()
            return None
    
    def add_vision_board_item(self, user_id: str, board_id: int,
                            item_type: str, content: str,
                            caption: Optional[str] = None,
                            position_x: float = 0, position_y: float = 0,
                            linked_goal_id: Optional[int] = None) -> Optional[VisionBoardItem]:
        """Add an item to a vision board"""
        try:
            board = VisionBoard.query.filter_by(
                id=board_id, 
                user_id=user_id
            ).first()
            
            if not board:
                return None
            
            item = VisionBoardItem(
                board_id=board_id,
                item_type=item_type,
                content=content,
                caption=caption,
                position_x=position_x,
                position_y=position_y,
                linked_goal_id=linked_goal_id
            )
            db.session.add(item)
            db.session.commit()
            
            return item
            
        except Exception as e:
            logger.error(f"Error adding vision board item: {e}")
            db.session.rollback()
            return None
    
    def get_personal_growth_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive personal growth statistics"""
        try:
            # Goals stats
            goals = Goal.query.filter_by(user_id=user_id).all()
            active_goals = [g for g in goals if g.status == 'active']
            completed_goals = [g for g in goals if g.status == 'completed']
            
            # Habits stats
            habits = Habit.query.filter_by(user_id=user_id, is_active=True).all()
            
            # Journal stats
            journal_count = JournalEntry.query.filter_by(user_id=user_id).count()
            
            # Vision boards
            vision_boards = VisionBoard.query.filter_by(user_id=user_id).count()
            
            return {
                'goals': {
                    'total': len(goals),
                    'active': len(active_goals),
                    'completed': len(completed_goals),
                    'completion_rate': (len(completed_goals) / len(goals) * 100) if goals else 0
                },
                'habits': {
                    'active': len(habits),
                    'total_tracked': sum(h.entries.count() for h in habits)
                },
                'journaling': {
                    'total_entries': journal_count,
                    'types': db.session.query(JournalEntry.entry_type, func.count())\
                             .filter_by(user_id=user_id)\
                             .group_by(JournalEntry.entry_type).all()
                },
                'vision_boards': vision_boards
            }
            
        except Exception as e:
            logger.error(f"Error getting growth stats: {e}")
            return {}


# AI-GENERATED [2024-12-01]
# ## Affected Components: models.personal_growth_models, services.gamification_service
# ORIGINAL_INTENT: Empower users to track and achieve personal growth 