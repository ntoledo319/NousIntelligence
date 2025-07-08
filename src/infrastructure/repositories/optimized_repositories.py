from sqlalchemy.orm import joinedload, selectinload
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OptimizedRepository:
    """Base repository with eager loading optimizations"""
    
    def __init__(self, model_class):
        self.model = model_class
    
    def get_with_relations(self, id: str, user_id: str = None):
        """Get entity with all related data in single query"""
        query = self.model.query.options(
            self._get_eager_loading_options()
        )
        
        if user_id:
            query = query.filter_by(id=id, user_id=user_id)
        else:
            query = query.filter_by(id=id)
            
        return query.first()
    
    def get_all_with_relations(self, user_id: str, limit: int = 100):
        """Get all entities with relations - optimized"""
        return self.model.query.options(
            self._get_eager_loading_options()
        ).filter_by(user_id=user_id).limit(limit).all()
    
    def _get_eager_loading_options(self):
        """Override in subclasses to define eager loading"""
        return []

class TaskRepository(OptimizedRepository):
    """Optimized task repository"""
    
    def _get_eager_loading_options(self):
        return [
            joinedload('assignee'),
            joinedload('family'),
            selectinload('comments')
        ]
    
    def get_user_tasks_optimized(self, user_id: str):
        """Get user tasks with minimal queries"""
        return self.model.query.options(
            joinedload('assignee'),
            joinedload('family'),
            selectinload('comments').joinedload('author')
        ).filter_by(user_id=user_id).all()

class FamilyRepository(OptimizedRepository):
    """Optimized family repository"""
    
    def _get_eager_loading_options(self):
        return [
            selectinload('members').joinedload('user'),
            selectinload('tasks'),
            selectinload('shopping_lists')
        ]
    
    def get_family_dashboard_data(self, family_id: str):
        """Get all family data in minimal queries"""
        from models import Family
        
        return Family.query.options(
            selectinload('members').joinedload('user'),
            selectinload('tasks').joinedload('assignee'),
            selectinload('shopping_lists').selectinload('items'),
            selectinload('events')
        ).filter_by(id=family_id).first()

class MoodRepository(OptimizedRepository):
    """Optimized mood repository"""
    
    def get_mood_analytics(self, user_id: str, days: int = 30):
        """Get mood data for analytics"""
        from datetime import datetime, timedelta
        from models import MoodEntry
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return MoodEntry.query.filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= cutoff_date
        ).order_by(MoodEntry.created_at).all()
