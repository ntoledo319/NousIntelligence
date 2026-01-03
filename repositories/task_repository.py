"""
Task Repository
Data access layer for task and reminder management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from models.database import db
import logging

logger = logging.getLogger(__name__)

# Attempt to import Task and Reminder models
try:
    from models.task_models import Task, Reminder
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    logger.warning("Task models not available")


class TaskRepository:
    """Repository for task and reminder data access"""
    
    @staticmethod
    def create_task(user_id: int, title: str, description: str = '',
                   due_date: Optional[datetime] = None, priority: str = 'medium',
                   category: str = 'general', recurring: bool = False,
                   recurrence_pattern: Optional[Dict] = None) -> Optional[Any]:
        """Create a new task"""
        if not MODELS_AVAILABLE:
            logger.warning("Cannot create task - models not available")
            return None
        
        try:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                category=category,
                recurring=recurring,
                recurrence_pattern=recurrence_pattern,
                completed=False
            )
            db.session.add(task)
            db.session.commit()
            logger.info(f"Created task for user {user_id}: {title}")
            return task
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating task: {e}")
            return None
    
    @staticmethod
    def get_user_tasks(user_id: int, include_completed: bool = False,
                      category: Optional[str] = None,
                      due_before: Optional[datetime] = None) -> List[Any]:
        """Get tasks for a user with filters"""
        if not MODELS_AVAILABLE:
            return []
        
        try:
            query = Task.query.filter_by(user_id=user_id)
            
            if not include_completed:
                query = query.filter_by(completed=False)
            
            if category:
                query = query.filter_by(category=category)
            
            if due_before:
                query = query.filter(Task.due_date <= due_before)
            
            return query.order_by(Task.due_date.asc()).all()
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []
    
    @staticmethod
    def get_overdue_tasks(user_id: int) -> List[Any]:
        """Get tasks that are past their due date"""
        if not MODELS_AVAILABLE:
            return []
        
        try:
            now = datetime.utcnow()
            return Task.query.filter(
                and_(
                    Task.user_id == user_id,
                    Task.completed == False,
                    Task.due_date < now
                )
            ).order_by(Task.due_date.asc()).all()
        except Exception as e:
            logger.error(f"Error getting overdue tasks: {e}")
            return []
    
    @staticmethod
    def get_today_tasks(user_id: int) -> List[Any]:
        """Get tasks due today"""
        if not MODELS_AVAILABLE:
            return []
        
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            return Task.query.filter(
                and_(
                    Task.user_id == user_id,
                    Task.completed == False,
                    Task.due_date >= today_start,
                    Task.due_date < today_end
                )
            ).order_by(Task.due_date.asc()).all()
        except Exception as e:
            logger.error(f"Error getting today's tasks: {e}")
            return []
    
    @staticmethod
    def complete_task(task_id: int, user_id: int) -> bool:
        """Mark a task as completed"""
        if not MODELS_AVAILABLE:
            return False
        
        try:
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            if task:
                task.completed = True
                task.completed_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Task {task_id} marked completed")
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error completing task: {e}")
            return False
    
    @staticmethod
    def update_task(task_id: int, user_id: int, **updates) -> bool:
        """Update task fields"""
        if not MODELS_AVAILABLE:
            return False
        
        try:
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            if task:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating task: {e}")
            return False
    
    @staticmethod
    def delete_task(task_id: int, user_id: int) -> bool:
        """Delete a task"""
        if not MODELS_AVAILABLE:
            return False
        
        try:
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            if task:
                db.session.delete(task)
                db.session.commit()
                logger.info(f"Task {task_id} deleted")
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting task: {e}")
            return False
    
    # ===== REMINDER METHODS =====
    
    @staticmethod
    def create_reminder(user_id: int, task_id: Optional[int], 
                       reminder_time: datetime, message: str = '',
                       reminder_type: str = 'notification') -> Optional[Any]:
        """Create a reminder"""
        if not MODELS_AVAILABLE:
            return None
        
        try:
            reminder = Reminder(
                user_id=user_id,
                task_id=task_id,
                reminder_time=reminder_time,
                message=message,
                reminder_type=reminder_type,
                sent=False
            )
            db.session.add(reminder)
            db.session.commit()
            return reminder
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating reminder: {e}")
            return None
    
    @staticmethod
    def get_pending_reminders(user_id: int, before_time: Optional[datetime] = None) -> List[Any]:
        """Get unsent reminders due before specified time"""
        if not MODELS_AVAILABLE:
            return []
        
        try:
            if not before_time:
                before_time = datetime.utcnow()
            
            return Reminder.query.filter(
                and_(
                    Reminder.user_id == user_id,
                    Reminder.sent == False,
                    Reminder.reminder_time <= before_time
                )
            ).order_by(Reminder.reminder_time.asc()).all()
        except Exception as e:
            logger.error(f"Error getting pending reminders: {e}")
            return []
    
    @staticmethod
    def mark_reminder_sent(reminder_id: int) -> bool:
        """Mark a reminder as sent"""
        if not MODELS_AVAILABLE:
            return False
        
        try:
            reminder = Reminder.query.get(reminder_id)
            if reminder:
                reminder.sent = True
                reminder.sent_at = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error marking reminder sent: {e}")
            return False
