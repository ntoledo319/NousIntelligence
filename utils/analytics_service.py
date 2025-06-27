"""
Analytics Service

This module provides analytics and insights functionality for the NOUS application,
supporting user activity tracking, metrics generation, and AI-powered insights.
"""

import json
import logging
from datetime import datetime, timedelta, date
from sqlalchemy import func, and_, or_
from typing import Dict, List, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for user analytics and insights"""
    
    def __init__(self, db):
        self.db = db
    
    def track_activity(self, user_id: str, activity_type: str, activity_category: str = None, 
                      activity_data: Dict = None, duration_seconds: int = 0, session_id: str = None):
        """Track a user activity"""
        try:
            from models.analytics_models import UserActivity
            
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                activity_category=activity_category,
                activity_data=activity_data or {},
                duration_seconds=duration_seconds,
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
            
            self.db.session.add(activity)
            self.db.session.commit()
            
            # Update daily metrics
            self._update_daily_metrics(user_id, activity_type, activity_category)
            
            return activity.to_dict()
            
        except Exception as e:
            logger.error(f"Error tracking activity: {str(e)}")
            self.db.session.rollback()
            return None
    
    def get_user_analytics_dashboard(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            # Get activity summary
            activity_summary = self._get_activity_summary(user_id, start_date, end_date)
            
            # Get productivity metrics
            productivity_metrics = self._get_productivity_metrics(user_id, start_date, end_date)
            
            # Get health metrics
            health_metrics = self._get_health_metrics(user_id, start_date, end_date)
            
            # Get engagement metrics
            engagement_metrics = self._get_engagement_metrics(user_id, start_date, end_date)
            
            # Get trends
            trends = self._get_trends(user_id, start_date, end_date)
            
            # Get recent insights
            insights = self._get_recent_insights(user_id, limit=5)
            
            # Get goals progress
            goals_progress = self._get_goals_progress(user_id)
            
            return {
                'period': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()},
                'activity_summary': activity_summary,
                'productivity_metrics': productivity_metrics,
                'health_metrics': health_metrics,
                'engagement_metrics': engagement_metrics,
                'trends': trends,
                'insights': insights,
                'goals_progress': goals_progress,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics dashboard: {str(e)}")
            return {}
    
    def _get_activity_summary(self, user_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get activity summary for the period"""
        from models.analytics_models import UserActivity
        
        activities = self.db.session.query(UserActivity).filter(
            and_(
                UserActivity.user_id == user_id,
                func.date(UserActivity.timestamp) >= start_date,
                func.date(UserActivity.timestamp) <= end_date
            )
        ).all()
        
        # Group by activity type
        by_type = defaultdict(int)
        by_category = defaultdict(int)
        total_duration = 0
        
        for activity in activities:
            by_type[activity.activity_type] += 1
            if activity.activity_category:
                by_category[activity.activity_category] += 1
            total_duration += activity.duration_seconds or 0
        
        return {
            'total_activities': len(activities),
            'total_duration_hours': round(total_duration / 3600, 2),
            'by_type': dict(by_type),
            'by_category': dict(by_category),
            'daily_average': round(len(activities) / max(1, (end_date - start_date).days), 2)
        }
    
    def _get_productivity_metrics(self, user_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get productivity metrics"""
        from models.analytics_models import UserMetrics
        
        metrics = self.db.session.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date >= start_date,
                UserMetrics.metric_date <= end_date
            )
        ).all()
        
        total_tasks = sum(m.tasks_completed or 0 for m in metrics)
        total_messages = sum(m.chat_messages_sent or 0 for m in metrics)
        total_active_time = sum(m.active_time_minutes or 0 for m in metrics)
        
        # Get unique features used
        all_features = set()
        for m in metrics:
            if m.features_used:
                all_features.update(m.features_used)
        
        return {
            'tasks_completed': total_tasks,
            'chat_messages_sent': total_messages,
            'active_time_hours': round(total_active_time / 60, 2),
            'features_used_count': len(all_features),
            'features_used': list(all_features),
            'avg_daily_tasks': round(total_tasks / max(1, len(metrics)), 2),
            'avg_daily_active_time': round((total_active_time / max(1, len(metrics))) / 60, 2)
        }
    
    def _get_health_metrics(self, user_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get health and wellness metrics"""
        from models.analytics_models import UserMetrics
        
        metrics = self.db.session.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date >= start_date,
                UserMetrics.metric_date <= end_date
            )
        ).all()
        
        mood_ratings = [m.mood_average for m in metrics if m.mood_average is not None]
        total_workouts = sum(m.workouts_logged or 0 for m in metrics)
        total_dbt_skills = sum(m.dbt_skills_used or 0 for m in metrics)
        
        return {
            'workouts_logged': total_workouts,
            'dbt_skills_used': total_dbt_skills,
            'avg_mood': round(sum(mood_ratings) / max(1, len(mood_ratings)), 2) if mood_ratings else None,
            'mood_trend': self._calculate_trend(mood_ratings),
            'workout_frequency': round(total_workouts / max(1, len(metrics)), 2),
            'wellness_score': self._calculate_wellness_score(mood_ratings, total_workouts, total_dbt_skills)
        }
    
    def _get_engagement_metrics(self, user_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get user engagement metrics"""
        from models.analytics_models import UserMetrics
        
        metrics = self.db.session.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date >= start_date,
                UserMetrics.metric_date <= end_date
            )
        ).all()
        
        total_logins = sum(m.login_count or 0 for m in metrics)
        streak_days = max((m.streak_days or 0 for m in metrics), default=0)
        active_days = len([m for m in metrics if (m.login_count or 0) > 0])
        
        return {
            'total_logins': total_logins,
            'current_streak': streak_days,
            'active_days': active_days,
            'engagement_rate': round(active_days / max(1, len(metrics)) * 100, 2),
            'avg_daily_logins': round(total_logins / max(1, len(metrics)), 2)
        }
    
    def _get_trends(self, user_id: str, start_date: date, end_date: date) -> Dict[str, List]:
        """Get trending data over time"""
        from models.analytics_models import UserMetrics
        
        metrics = self.db.session.query(UserMetrics).filter(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.metric_date >= start_date,
                UserMetrics.metric_date <= end_date
            )
        ).order_by(UserMetrics.metric_date).all()
        
        trends = {
            'productivity': [],
            'mood': [],
            'activity': [],
            'engagement': []
        }
        
        for metric in metrics:
            date_str = metric.metric_date.isoformat()
            
            trends['productivity'].append({
                'date': date_str,
                'tasks': metric.tasks_completed or 0,
                'active_time': metric.active_time_minutes or 0
            })
            
            trends['mood'].append({
                'date': date_str,
                'mood': metric.mood_average
            })
            
            trends['activity'].append({
                'date': date_str,
                'workouts': metric.workouts_logged or 0,
                'dbt_skills': metric.dbt_skills_used or 0
            })
            
            trends['engagement'].append({
                'date': date_str,
                'logins': metric.login_count or 0,
                'messages': metric.chat_messages_sent or 0
            })
        
        return trends
    
    def _get_recent_insights(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent AI insights"""
        from models.analytics_models import UserInsight
        
        insights = self.db.session.query(UserInsight).filter(
            and_(
                UserInsight.user_id == user_id,
                UserInsight.is_dismissed == False
            )
        ).order_by(UserInsight.generated_at.desc()).limit(limit).all()
        
        return [insight.to_dict() for insight in insights]
    
    def _get_goals_progress(self, user_id: str) -> List[Dict]:
        """Get current goals progress"""
        from models.analytics_models import UserGoal
        
        goals = self.db.session.query(UserGoal).filter(
            and_(
                UserGoal.user_id == user_id,
                UserGoal.is_active == True
            )
        ).all()
        
        return [goal.to_dict() for goal in goals]
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        recent_avg = sum(values[-3:]) / min(3, len(values))
        earlier_avg = sum(values[:-3]) / max(1, len(values) - 3) if len(values) > 3 else values[0]
        
        if recent_avg > earlier_avg * 1.1:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_wellness_score(self, mood_ratings: List[float], workouts: int, dbt_skills: int) -> float:
        """Calculate overall wellness score"""
        score = 0
        
        # Mood component (40%)
        if mood_ratings:
            avg_mood = sum(mood_ratings) / len(mood_ratings)
            score += (avg_mood / 10) * 40
        
        # Activity component (30%)
        if workouts > 0:
            activity_score = min(workouts * 2, 30)  # Cap at 30
            score += activity_score
        
        # Mental health component (30%)
        if dbt_skills > 0:
            mental_score = min(dbt_skills, 30)  # Cap at 30
            score += mental_score
        
        return round(score, 1)
    
    def _update_daily_metrics(self, user_id: str, activity_type: str, activity_category: str):
        """Update daily metrics for user"""
        try:
            from models.analytics_models import UserMetrics
            
            today = date.today()
            
            # Get or create daily metric
            metric = self.db.session.query(UserMetrics).filter(
                and_(
                    UserMetrics.user_id == user_id,
                    UserMetrics.metric_date == today,
                    UserMetrics.metric_type == 'daily'
                )
            ).first()
            
            if not metric:
                metric = UserMetrics(
                    user_id=user_id,
                    metric_type='daily',
                    metric_date=today,
                    features_used=[]
                )
                self.db.session.add(metric)
            
            # Update based on activity type
            if activity_type == 'chat':
                metric.chat_messages_sent = (metric.chat_messages_sent or 0) + 1
            elif activity_type == 'task_completed':
                metric.tasks_completed = (metric.tasks_completed or 0) + 1
            elif activity_type == 'workout':
                metric.workouts_logged = (metric.workouts_logged or 0) + 1
            elif activity_type == 'dbt_skill':
                metric.dbt_skills_used = (metric.dbt_skills_used or 0) + 1
            
            # Add feature to used features
            if activity_category and activity_category not in (metric.features_used or []):
                features = metric.features_used or []
                features.append(activity_category)
                metric.features_used = features
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating daily metrics: {str(e)}")
            self.db.session.rollback()
    
    def generate_ai_insight(self, user_id: str, insight_type: str, title: str, content: str, 
                           confidence_score: float = 0.8, priority: str = 'medium'):
        """Generate an AI insight for the user"""
        try:
            from models.analytics_models import UserInsight
            
            insight = UserInsight(
                user_id=user_id,
                insight_type=insight_type,
                title=title,
                content=content,
                confidence_score=confidence_score,
                priority=priority,
                generated_at=datetime.utcnow()
            )
            
            self.db.session.add(insight)
            self.db.session.commit()
            
            return insight.to_dict()
            
        except Exception as e:
            logger.error(f"Error generating AI insight: {str(e)}")
            self.db.session.rollback()
            return None 