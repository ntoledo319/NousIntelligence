"""
Social Service

This service handles all social and community features including support groups,
peer connections, anonymous sharing, and community interactions.

@module services.social_service
@ai_prompt Use this service for any social/community features like support groups or peer connections
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import and_, or_, func
from flask import g

from database import db
from models.social_models import (
    SupportGroup, GroupMembership, PeerConnection, AnonymousShare,
    AnonymousResponse, GroupPost, GroupComment
)
from models.user import User
from utils.notification_service import NotificationService

logger = logging.getLogger(__name__)


class SocialService:
    """Service for managing social and community features"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        logger.info("Social Service initialized")
    
    # === Support Group Methods ===
    
    def create_support_group(self, user_id: str, name: str, description: str, 
                            category: str, privacy_level: str = 'private') -> Optional[SupportGroup]:
        """
        Create a new support group
        
        @ai_prompt Use this to create a new support group for users with similar challenges
        """
        try:
            # Check if user can create groups (implement limits if needed)
            existing_groups = SupportGroup.query.filter_by(created_by=user_id, is_active=True).count()
            if existing_groups >= 5:  # Limit to 5 groups per user
                logger.warning(f"User {user_id} has reached group creation limit")
                return None
            
            group = SupportGroup(
                name=name,
                description=description,
                category=category,
                privacy_level=privacy_level,
                created_by=user_id
            )
            db.session.add(group)
            db.session.flush()
            
            # Creator automatically becomes admin member
            membership = GroupMembership(
                user_id=user_id,
                group_id=group.id,
                role='admin'
            )
            db.session.add(membership)
            db.session.commit()
            
            logger.info(f"Support group '{name}' created by user {user_id}")
            return group
            
        except Exception as e:
            logger.error(f"Error creating support group: {e}")
            db.session.rollback()
            return None
    
    def join_support_group(self, user_id: str, group_id: int) -> bool:
        """Join a support group"""
        try:
            group = SupportGroup.query.get(group_id)
            if not group or not group.is_active:
                return False
            
            # Check if already a member
            existing = GroupMembership.query.filter_by(
                user_id=user_id, 
                group_id=group_id
            ).first()
            if existing:
                return True
            
            # Check if group is full
            member_count = GroupMembership.query.filter_by(
                group_id=group_id, 
                is_active=True
            ).count()
            if member_count >= group.max_members:
                return False
            
            membership = GroupMembership(
                user_id=user_id,
                group_id=group_id,
                role='member'
            )
            db.session.add(membership)
            db.session.commit()
            
            # Notify group admins
            self._notify_group_admins(group_id, f"New member joined: {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error joining group: {e}")
            db.session.rollback()
            return False
    
    def get_user_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all groups a user is a member of"""
        try:
            memberships = GroupMembership.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            groups = []
            for membership in memberships:
                if membership.group.is_active:
                    group_dict = membership.group.to_dict()
                    group_dict['user_role'] = membership.role
                    group_dict['notifications_enabled'] = membership.notification_enabled
                    groups.append(group_dict)
            
            return groups
            
        except Exception as e:
            logger.error(f"Error getting user groups: {e}")
            return []
    
    def search_support_groups(self, category: Optional[str] = None, 
                             query: Optional[str] = None) -> List[SupportGroup]:
        """Search for support groups"""
        try:
            q = SupportGroup.query.filter_by(is_active=True)
            
            if category:
                q = q.filter_by(category=category)
            
            if query:
                q = q.filter(
                    or_(
                        SupportGroup.name.ilike(f'%{query}%'),
                        SupportGroup.description.ilike(f'%{query}%')
                    )
                )
            
            # Only show public groups in search
            q = q.filter(SupportGroup.privacy_level != 'private')
            
            return q.limit(20).all()
            
        except Exception as e:
            logger.error(f"Error searching groups: {e}")
            return []
    
    # === Peer Connection Methods ===
    
    def request_peer_connection(self, user_id: str, peer_id: str, 
                               connection_type: str = 'peer') -> bool:
        """Request a peer connection (friend/mentor)"""
        try:
            # Check if connection already exists
            existing = PeerConnection.query.filter(
                or_(
                    and_(PeerConnection.user_id == user_id, PeerConnection.peer_id == peer_id),
                    and_(PeerConnection.user_id == peer_id, PeerConnection.peer_id == user_id)
                )
            ).first()
            
            if existing:
                return existing.status == 'accepted'
            
            connection = PeerConnection(
                user_id=user_id,
                peer_id=peer_id,
                connection_type=connection_type,
                status='pending'
            )
            db.session.add(connection)
            db.session.commit()
            
            # Notify peer
            self.notification_service.send_notification(
                peer_id,
                'connection_request',
                f'You have a new {connection_type} connection request'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error requesting connection: {e}")
            db.session.rollback()
            return False
    
    def accept_peer_connection(self, user_id: str, connection_id: int) -> bool:
        """Accept a peer connection request"""
        try:
            connection = PeerConnection.query.get(connection_id)
            if not connection or connection.peer_id != user_id:
                return False
            
            connection.status = 'accepted'
            connection.accepted_at = datetime.utcnow()
            db.session.commit()
            
            # Notify original requester
            self.notification_service.send_notification(
                connection.user_id,
                'connection_accepted',
                'Your connection request was accepted!'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error accepting connection: {e}")
            db.session.rollback()
            return False
    
    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all peer connections for a user"""
        try:
            connections = []
            
            # Connections initiated by user
            initiated = PeerConnection.query.filter_by(
                user_id=user_id,
                status='accepted'
            ).all()
            
            for conn in initiated:
                peer = User.query.get(conn.peer_id)
                if peer:
                    connections.append({
                        'connection_id': conn.id,
                        'peer_id': conn.peer_id,
                        'peer_name': peer.username,
                        'connection_type': conn.connection_type,
                        'connected_since': conn.accepted_at.isoformat() if conn.accepted_at else None
                    })
            
            # Connections received by user
            received = PeerConnection.query.filter_by(
                peer_id=user_id,
                status='accepted'
            ).all()
            
            for conn in received:
                peer = User.query.get(conn.user_id)
                if peer:
                    connections.append({
                        'connection_id': conn.id,
                        'peer_id': conn.user_id,
                        'peer_name': peer.username,
                        'connection_type': conn.connection_type,
                        'connected_since': conn.accepted_at.isoformat() if conn.accepted_at else None
                    })
            
            return connections
            
        except Exception as e:
            logger.error(f"Error getting connections: {e}")
            return []
    
    # === Anonymous Sharing Methods ===
    
    def create_anonymous_share(self, user_id: str, category: str, 
                              title: str, content: str, mood: Optional[str] = None) -> Optional[AnonymousShare]:
        """
        Create an anonymous share
        
        ## Concept: Anonymous Sharing
        Allows users to share experiences without revealing identity
        """
        try:
            # Hash user ID for tracking (for moderation only)
            user_hash = hashlib.sha256(f"{user_id}:{datetime.utcnow().date()}".encode()).hexdigest()
            
            share = AnonymousShare(
                category=category,
                title=title,
                content=content,
                mood_at_sharing=mood,
                user_hash=user_hash
            )
            db.session.add(share)
            db.session.commit()
            
            logger.info(f"Anonymous share created in category {category}")
            return share
            
        except Exception as e:
            logger.error(f"Error creating anonymous share: {e}")
            db.session.rollback()
            return None
    
    def get_anonymous_shares(self, category: Optional[str] = None, 
                            limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent anonymous shares"""
        try:
            query = AnonymousShare.query.filter_by(is_published=True)
            
            if category:
                query = query.filter_by(category=category)
            
            shares = query.order_by(AnonymousShare.created_at.desc()).limit(limit).all()
            
            return [share.to_dict() for share in shares]
            
        except Exception as e:
            logger.error(f"Error getting anonymous shares: {e}")
            return []
    
    def add_support_to_share(self, share_id: str, user_id: str) -> bool:
        """Add support/helpful reaction to an anonymous share"""
        try:
            share = AnonymousShare.query.filter_by(share_id=share_id).first()
            if not share:
                return False
            
            share.support_count += 1
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding support: {e}")
            db.session.rollback()
            return False
    
    # === Group Post Methods ===
    
    def create_group_post(self, user_id: str, group_id: int, 
                         title: str, content: str, post_type: str = 'discussion') -> Optional[GroupPost]:
        """Create a post in a support group"""
        try:
            # Verify membership
            membership = GroupMembership.query.filter_by(
                user_id=user_id,
                group_id=group_id,
                is_active=True
            ).first()
            
            if not membership:
                return None
            
            post = GroupPost(
                group_id=group_id,
                user_id=user_id,
                title=title,
                content=content,
                post_type=post_type
            )
            db.session.add(post)
            db.session.commit()
            
            # Notify group members
            self._notify_group_members(group_id, f"New {post_type} in group", exclude_user=user_id)
            
            return post
            
        except Exception as e:
            logger.error(f"Error creating group post: {e}")
            db.session.rollback()
            return None
    
    # === Helper Methods ===
    
    def _notify_group_admins(self, group_id: int, message: str):
        """Notify all group admins"""
        try:
            admin_memberships = GroupMembership.query.filter_by(
                group_id=group_id,
                role='admin',
                is_active=True,
                notification_enabled=True
            ).all()
            
            for membership in admin_memberships:
                self.notification_service.send_notification(
                    membership.user_id,
                    'group_admin',
                    message
                )
                
        except Exception as e:
            logger.error(f"Error notifying admins: {e}")
    
    def _notify_group_members(self, group_id: int, message: str, exclude_user: Optional[str] = None):
        """Notify all group members"""
        try:
            memberships = GroupMembership.query.filter_by(
                group_id=group_id,
                is_active=True,
                notification_enabled=True
            ).all()
            
            for membership in memberships:
                if membership.user_id != exclude_user:
                    self.notification_service.send_notification(
                        membership.user_id,
                        'group_update',
                        message
                    )
                    
        except Exception as e:
            logger.error(f"Error notifying members: {e}")
    
    def get_community_stats(self, user_id: str) -> Dict[str, Any]:
        """Get community engagement statistics for a user"""
        try:
            stats = {
                'groups_joined': GroupMembership.query.filter_by(
                    user_id=user_id, is_active=True
                ).count(),
                'connections': len(self.get_user_connections(user_id)),
                'posts_created': GroupPost.query.filter_by(user_id=user_id).count(),
                'support_given': 0,  # Would need to track this separately
                'member_since': User.query.get(user_id).created_at.isoformat() if User.query.get(user_id) else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting community stats: {e}")
            return {}


# AI-GENERATED [2024-12-01]
# @see models.social_models for database schema
# NON-NEGOTIABLES: Anonymous shares must remain truly anonymous 