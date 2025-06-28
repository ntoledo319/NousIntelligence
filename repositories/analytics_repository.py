"""
Analytics Repository - Data access layer for analytics and metrics operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from database import db
from models.analytics_models import UserActivity, Goal, Insight

class AnalyticsRepository:
    """Repository for analytics-related data access operations"""

    # User Activity methods
    @staticmethod
    def log_user_activity(user_id: str, activity_data: Dict[str, Any]) -> UserActivity:
        """Log a user activity"""
        activity = UserActivity(user_id=user_id, **activity_data)
        db.session.add(activity)
        db.session.commit()
        return activity

    @staticmethod
    def get_user_activities(user_id: str, limit: Optional[int] = None, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[UserActivity]:
        """Get user activities with optional filters"""
        query = UserActivity.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(UserActivity.timestamp >= start_date)
        if end_date:
            query = query.filter(UserActivity.timestamp <= end_date)
            
        query = query.order_by(UserActivity.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()

    @staticmethod
    def get_activity_summary(user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get activity summary for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        activities = AnalyticsRepository.get_user_activities(
            user_id, start_date=start_date
        )
        
        summary = {
            'total_activities': len(activities),
            'categories': {},
            'daily_counts': {},
            'most_active_day': None,
            'most_common_category': None
        }
        
        for activity in activities:
            # Count by category
            category = getattr(activity, 'category', 'unknown')
            summary['categories'][category] = summary['categories'].get(category, 0) + 1
            
            # Count by day
            day = activity.timestamp.date().isoformat()
            summary['daily_counts'][day] = summary['daily_counts'].get(day, 0) + 1
        
        # Find most active day and common category
        if summary['daily_counts']:
            summary['most_active_day'] = max(summary['daily_counts'], 
                                           key=summary['daily_counts'].get)
        if summary['categories']:
            summary['most_common_category'] = max(summary['categories'], 
                                                key=summary['categories'].get)
        
        return summary

    # Goal tracking methods
    @staticmethod
    def create_goal(user_id: str, goal_data: Dict[str, Any]) -> Goal:
        """Create a new goal"""
        goal = Goal(user_id=user_id, **goal_data)
        db.session.add(goal)
        db.session.commit()
        return goal

    @staticmethod
    def get_user_goals(user_id: str, status: Optional[str] = None) -> List[Goal]:
        """Get user goals, optionally filtered by status"""
        query = Goal.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Goal.created_at.desc()).all()

    @staticmethod
    def update_goal_progress(goal_id: int, progress: float) -> Optional[Goal]:
        """Update goal progress"""
        goal = Goal.query.get(goal_id)
        if goal:
            goal.progress = progress
            if progress >= 100:
                goal.status = 'completed'
                goal.completed_at = datetime.utcnow()
            db.session.commit()
        return goal

    # Insights methods
    @staticmethod
    def create_insight(user_id: str, insight_data: Dict[str, Any]) -> Insight:
        """Create a new insight"""
        insight = Insight(user_id=user_id, **insight_data)
        db.session.add(insight)
        db.session.commit()
        return insight

    @staticmethod
    def get_user_insights(user_id: str, category: Optional[str] = None, 
                         limit: int = 10) -> List[Insight]:
        """Get user insights"""
        query = Insight.query.filter_by(user_id=user_id)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(Insight.generated_at.desc()).limit(limit).all()

    @staticmethod
    def get_insights_by_priority(user_id: str, limit: int = 5) -> List[Insight]:
        """Get insights ordered by priority"""
        return Insight.query.filter_by(user_id=user_id)\
                           .order_by(Insight.priority.desc(), Insight.generated_at.desc())\
                           .limit(limit).all()