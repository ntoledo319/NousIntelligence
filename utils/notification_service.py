"""
Notification Service

This module provides notification management functionality for the NOUS application,
supporting user notifications, alerts, reminders, and notification center features.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing user notifications"""
    
    def __init__(self, db):
        self.db = db
    
    def create_notification(self, user_id: str, notification_type: str, title: str, 
                          message: str, priority: str = 'normal', action_url: str = None,
                          metadata: Dict = None, expires_at: datetime = None) -> Dict[str, Any]:
        """Create a new notification for user"""
        try:
            from models.analytics_models import NotificationQueue
            
            notification = NotificationQueue(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                action_url=action_url,
                metadata=metadata or {},
                expires_at=expires_at,
                created_at=datetime.utcnow()
            )
            
            self.db.session.add(notification)
            self.db.session.commit()
            
            logger.info(f"Created notification for user {user_id}: {title}")
            return notification.to_dict()
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            self.db.session.rollback()
            return None
    
    def get_user_notifications(self, user_id: str, include_read: bool = True, 
                             limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get notifications for user"""
        try:
            from models.analytics_models import NotificationQueue
            
            query = self.db.session.query(NotificationQueue).filter(
                and_(
                    NotificationQueue.user_id == user_id,
                    NotificationQueue.is_dismissed == False,
                    or_(
                        NotificationQueue.expires_at.is_(None),
                        NotificationQueue.expires_at > datetime.utcnow()
                    )
                )
            )
            
            if not include_read:
                query = query.filter(NotificationQueue.is_read == False)
            
            # Get total count
            total_count = query.count()
            unread_count = query.filter(NotificationQueue.is_read == False).count()
            
            # Get notifications with pagination
            notifications = query.order_by(
                NotificationQueue.priority.desc(),
                NotificationQueue.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            # Group by priority
            grouped_notifications = self._group_by_priority(notifications)
            
            return {
                'notifications': [n.to_dict() for n in notifications],
                'grouped_notifications': grouped_notifications,
                'total_count': total_count,
                'unread_count': unread_count,
                'has_more': total_count > (offset + limit)
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return {
                'notifications': [],
                'grouped_notifications': {},
                'total_count': 0,
                'unread_count': 0,
                'has_more': False
            }
    
    def mark_as_read(self, user_id: str, notification_id: int) -> bool:
        """Mark notification as read"""
        try:
            from models.analytics_models import NotificationQueue
            
            notification = self.db.session.query(NotificationQueue).filter(
                and_(
                    NotificationQueue.id == notification_id,
                    NotificationQueue.user_id == user_id
                )
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                self.db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            self.db.session.rollback()
            return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for user"""
        try:
            from models.analytics_models import NotificationQueue
            
            count = self.db.session.query(NotificationQueue).filter(
                and_(
                    NotificationQueue.user_id == user_id,
                    NotificationQueue.is_read == False
                )
            ).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            
            self.db.session.commit()
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            self.db.session.rollback()
            return 0
    
    def dismiss_notification(self, user_id: str, notification_id: int) -> bool:
        """Dismiss (hide) a notification"""
        try:
            from models.analytics_models import NotificationQueue
            
            notification = self.db.session.query(NotificationQueue).filter(
                and_(
                    NotificationQueue.id == notification_id,
                    NotificationQueue.user_id == user_id
                )
            ).first()
            
            if notification:
                notification.is_dismissed = True
                self.db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error dismissing notification: {str(e)}")
            self.db.session.rollback()
            return False
    
    def create_reminder_notification(self, user_id: str, title: str, message: str, 
                                   remind_at: datetime, reminder_type: str = 'reminder',
                                   metadata: Dict = None) -> Dict[str, Any]:
        """Create a reminder notification for future delivery"""
        return self.create_notification(
            user_id=user_id,
            notification_type=reminder_type,
            title=title,
            message=message,
            priority='normal',
            metadata={'remind_at': remind_at.isoformat(), **(metadata or {})}
        )
    
    def create_achievement_notification(self, user_id: str, achievement_title: str, 
                                      achievement_description: str, 
                                      metadata: Dict = None) -> Dict[str, Any]:
        """Create an achievement notification"""
        return self.create_notification(
            user_id=user_id,
            notification_type='achievement',
            title=f'🎉 Achievement Unlocked: {achievement_title}',
            message=achievement_description,
            priority='high',
            metadata=metadata
        )
    
    def create_system_notification(self, user_id: str, title: str, message: str,
                                 priority: str = 'normal', action_url: str = None) -> Dict[str, Any]:
        """Create a system notification"""
        return self.create_notification(
            user_id=user_id,
            notification_type='system',
            title=title,
            message=message,
            priority=priority,
            action_url=action_url
        )
    
    def create_health_reminder(self, user_id: str, reminder_type: str, message: str,
                             metadata: Dict = None) -> Dict[str, Any]:
        """Create health-related reminders"""
        icons = {
            'medication': '💊',
            'appointment': '🏥',
            'exercise': '💪',
            'hydration': '💧',
            'sleep': '😴'
        }
        
        icon = icons.get(reminder_type, '⚕️')
        
        return self.create_notification(
            user_id=user_id,
            notification_type='health_reminder',
            title=f'{icon} Health Reminder',
            message=message,
            priority='high',
            metadata={'reminder_type': reminder_type, **(metadata or {})}
        )
    
    def create_goal_progress_notification(self, user_id: str, goal_title: str, 
                                        progress_percentage: float, 
                                        milestone_reached: bool = False) -> Dict[str, Any]:
        """Create goal progress notification"""
        if milestone_reached:
            title = f'🎯 Milestone Reached: {goal_title}'
            message = f'Congratulations! You\'ve reached {progress_percentage}% of your goal.'
            priority = 'high'
        else:
            title = f'📈 Goal Progress: {goal_title}'
            message = f'You\'re making progress! {progress_percentage}% complete.'
            priority = 'normal'
        
        return self.create_notification(
            user_id=user_id,
            notification_type='goal_progress',
            title=title,
            message=message,
            priority=priority,
            metadata={
                'goal_title': goal_title,
                'progress_percentage': progress_percentage,
                'milestone_reached': milestone_reached
            }
        )
    
    def get_notification_summary(self, user_id: str) -> Dict[str, Any]:
        """Get notification summary for user"""
        try:
            from models.analytics_models import NotificationQueue
            
            # Get counts by type and priority
            type_counts = self.db.session.query(
                NotificationQueue.notification_type,
                func.count(NotificationQueue.id)
            ).filter(
                and_(
                    NotificationQueue.user_id == user_id,
                    NotificationQueue.is_dismissed == False,
                    NotificationQueue.is_read == False
                )
            ).group_by(NotificationQueue.notification_type).all()
            
            priority_counts = self.db.session.query(
                NotificationQueue.priority,
                func.count(NotificationQueue.id)
            ).filter(
                and_(
                    NotificationQueue.user_id == user_id,
                    NotificationQueue.is_dismissed == False,
                    NotificationQueue.is_read == False
                )
            ).group_by(NotificationQueue.priority).all()
            
            # Get recent notifications
            recent = self.db.session.query(NotificationQueue).filter(
                and_(
                    NotificationQueue.user_id == user_id,
                    NotificationQueue.is_dismissed == False,
                    NotificationQueue.created_at > datetime.utcnow() - timedelta(hours=24)
                )
            ).order_by(NotificationQueue.created_at.desc()).limit(5).all()
            
            total_unread = sum(count for _, count in type_counts)
            
            return {
                'total_unread': total_unread,
                'type_counts': {ntype: count for ntype, count in type_counts},
                'priority_counts': {priority: count for priority, count in priority_counts},
                'recent_notifications': [n.to_dict() for n in recent],
                'has_urgent': any(priority == 'urgent' for priority, _ in priority_counts)
            }
            
        except Exception as e:
            logger.error(f"Error getting notification summary: {str(e)}")
            return {
                'total_unread': 0,
                'type_counts': {},
                'priority_counts': {},
                'recent_notifications': [],
                'has_urgent': False
            }
    
    def cleanup_expired_notifications(self, user_id: str = None) -> int:
        """Clean up expired notifications"""
        try:
            from models.analytics_models import NotificationQueue
            
            query = self.db.session.query(NotificationQueue).filter(
                and_(
                    NotificationQueue.expires_at.isnot(None),
                    NotificationQueue.expires_at < datetime.utcnow()
                )
            )
            
            if user_id:
                query = query.filter(NotificationQueue.user_id == user_id)
            
            count = query.count()
            query.delete()
            self.db.session.commit()
            
            logger.info(f"Cleaned up {count} expired notifications")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {str(e)}")
            self.db.session.rollback()
            return 0
    
    def _group_by_priority(self, notifications) -> Dict[str, List[Dict]]:
        """Group notifications by priority"""
        grouped = {
            'urgent': [],
            'high': [],
            'normal': [],
            'low': []
        }
        
        for notification in notifications:
            priority = notification.priority or 'normal'
            if priority in grouped:
                grouped[priority].append(notification.to_dict())
        
        return grouped
    
    def bulk_create_notifications(self, notifications_data: List[Dict]) -> List[Dict]:
        """Create multiple notifications in bulk"""
        try:
            from models.analytics_models import NotificationQueue
            
            notifications = []
            for data in notifications_data:
                notification = NotificationQueue(**data)
                notifications.append(notification)
                self.db.session.add(notification)
            
            self.db.session.commit()
            
            return [n.to_dict() for n in notifications]
            
        except Exception as e:
            logger.error(f"Error bulk creating notifications: {str(e)}")
            self.db.session.rollback()
            return []
