"""
Memory Service - Comprehensive Memory Management System
Handles user memory, context retention, learning patterns, and adaptive intelligence
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone, timedelta
from database import db
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)


class MemoryType(db.Model):
    """Types of memories the system can store"""
    __tablename__ = 'memory_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    retention_days = Column(Integer, default=365)  # How long to keep this type
    priority_level = Column(Integer, default=1)  # 1=low, 5=critical
    auto_cleanup = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    memories = relationship("UserMemory", back_populates="memory_type")


class UserMemory(db.Model):
    """Individual memory entries for users"""
    __tablename__ = 'user_memories'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    memory_type_id = Column(Integer, ForeignKey('memory_types.id'), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    context_data = Column(Text)  # JSON context information
    importance_score = Column(Float, default=0.5)  # 0.0-1.0 importance
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    memory_type = relationship("MemoryType", back_populates="memories")
    associations = relationship("MemoryAssociation", foreign_keys="[MemoryAssociation.memory_id]")
    related_memories = relationship("MemoryAssociation", foreign_keys="[MemoryAssociation.related_memory_id]")


class MemoryAssociation(db.Model):
    """Associations between memories for relationship mapping"""
    __tablename__ = 'memory_associations'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey('user_memories.id'), nullable=False)
    related_memory_id = Column(Integer, ForeignKey('user_memories.id'), nullable=False)
    association_type = Column(String(50), nullable=False)  # related, caused_by, led_to, similar
    strength = Column(Float, default=0.5)  # 0.0-1.0 association strength
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ConversationMemory(db.Model):
    """Memory of conversations and interactions"""
    __tablename__ = 'conversation_memories'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    session_id = Column(String(255))  # Track conversation sessions
    conversation_type = Column(String(50), default='chat')  # chat, voice, email, etc.
    summary = Column(Text)
    key_topics = Column(Text)  # JSON array of topics discussed
    user_mood = Column(String(50))  # happy, frustrated, curious, etc.
    ai_responses_quality = Column(Float)  # User feedback on AI responses
    insights_gained = Column(Text)  # What was learned about the user
    action_items = Column(Text)  # JSON array of follow-up actions
    conversation_length = Column(Integer, default=0)  # Number of exchanges
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserPreference(db.Model):
    """User preferences and learned behaviors"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    category = Column(String(100), nullable=False)  # communication, scheduling, interests
    preference_key = Column(String(255), nullable=False)
    preference_value = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.5)  # How confident we are in this preference
    source = Column(String(100))  # explicit_setting, inferred, learned
    last_confirmed = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class MemoryService:
    """Main memory management service"""
    
    def __init__(self):
        self.default_memory_types = [
            {'name': 'personal_info', 'description': 'Personal information and details', 'retention_days': 3650, 'priority_level': 5},
            {'name': 'preferences', 'description': 'User preferences and settings', 'retention_days': 1825, 'priority_level': 4},
            {'name': 'goals', 'description': 'User goals and objectives', 'retention_days': 1095, 'priority_level': 4},
            {'name': 'habits', 'description': 'User habits and routines', 'retention_days': 730, 'priority_level': 3},
            {'name': 'events', 'description': 'Important events and milestones', 'retention_days': 1825, 'priority_level': 4},
            {'name': 'conversations', 'description': 'Chat and interaction history', 'retention_days': 365, 'priority_level': 2},
            {'name': 'learning', 'description': 'Learning progress and insights', 'retention_days': 1095, 'priority_level': 3},
            {'name': 'context', 'description': 'Contextual information', 'retention_days': 90, 'priority_level': 2},
        ]
    
    def initialize_memory_types(self):
        """Initialize default memory types"""
        try:
            for memory_type_data in self.default_memory_types:
                existing = MemoryType.query.filter_by(name=memory_type_data['name']).first()
                if not existing:
                    memory_type = MemoryType(**memory_type_data)
                    db.session.add(memory_type)
            
            db.session.commit()
            logger.info("Memory types initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing memory types: {str(e)}")
            db.session.rollback()
            return False
    
    def store_memory(self, user_id: int, memory_type: str, title: str, content: str, 
                    context: Optional[Dict[str, Any]] = None, importance: float = 0.5) -> Optional[UserMemory]:
        """Store a new memory for a user"""
        try:
            # Get memory type
            mem_type = MemoryType.query.filter_by(name=memory_type).first()
            if not mem_type:
                logger.warning(f"Memory type '{memory_type}' not found, using 'context'")
                mem_type = MemoryType.query.filter_by(name='context').first()
                if not mem_type:
                    logger.error("No fallback memory type available")
                    return None
            
            # Calculate expiration
            expires_at = None
            if mem_type.retention_days > 0:
                expires_at = datetime.now(timezone.utc) + timedelta(days=mem_type.retention_days)
            
            # Create memory
            memory = UserMemory(
                user_id=user_id,
                memory_type_id=mem_type.id,
                title=title,
                content=content,
                context_data=json.dumps(context) if context else None,
                importance_score=max(0.0, min(1.0, importance)),
                expires_at=expires_at
            )
            
            db.session.add(memory)
            db.session.commit()
            
            logger.info(f"Memory stored for user {user_id}: {title}")
            return memory
            
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            db.session.rollback()
            return None
    
    def retrieve_memories(self, user_id: int, memory_type: Optional[str] = None, 
                         limit: int = 10, importance_threshold: float = 0.0) -> List[UserMemory]:
        """Retrieve memories for a user"""
        try:
            query = UserMemory.query.filter_by(user_id=user_id, is_active=True)
            
            if memory_type:
                mem_type = MemoryType.query.filter_by(name=memory_type).first()
                if mem_type:
                    query = query.filter_by(memory_type_id=mem_type.id)
            
            if importance_threshold > 0:
                query = query.filter(UserMemory.importance_score >= importance_threshold)
            
            # Order by importance and recency
            memories = query.order_by(
                UserMemory.importance_score.desc(),
                UserMemory.updated_at.desc()
            ).limit(limit).all()
            
            # Update access tracking
            for memory in memories:
                memory.access_count += 1
                memory.last_accessed = datetime.now(timezone.utc)
            
            db.session.commit()
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            return []
    
    def search_memories(self, user_id: int, search_term: str, limit: int = 10) -> List[UserMemory]:
        """Search memories by content"""
        try:
            memories = UserMemory.query.filter(
                UserMemory.user_id == user_id,
                UserMemory.is_active == True,
                db.or_(
                    UserMemory.title.ilike(f'%{search_term}%'),
                    UserMemory.content.ilike(f'%{search_term}%')
                )
            ).order_by(
                UserMemory.importance_score.desc(),
                UserMemory.updated_at.desc()
            ).limit(limit).all()
            
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            return []
    
    def update_memory(self, memory_id: int, title: Optional[str] = None, 
                     content: Optional[str] = None, importance: Optional[float] = None) -> bool:
        """Update an existing memory"""
        try:
            memory = UserMemory.query.get(memory_id)
            if not memory:
                logger.warning(f"Memory {memory_id} not found")
                return False
            
            if title:
                memory.title = title
            if content:
                memory.content = content
            if importance is not None:
                memory.importance_score = max(0.0, min(1.0, importance))
            
            memory.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory: {str(e)}")
            db.session.rollback()
            return False
    
    def delete_memory(self, memory_id: int, soft_delete: bool = True) -> bool:
        """Delete a memory (soft or hard delete)"""
        try:
            memory = UserMemory.query.get(memory_id)
            if not memory:
                logger.warning(f"Memory {memory_id} not found")
                return False
            
            if soft_delete:
                memory.is_active = False
                memory.updated_at = datetime.now(timezone.utc)
            else:
                db.session.delete(memory)
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            db.session.rollback()
            return False
    
    def create_memory_association(self, memory_id: int, related_memory_id: int, 
                                association_type: str, strength: float = 0.5) -> bool:
        """Create an association between memories"""
        try:
            association = MemoryAssociation(
                memory_id=memory_id,
                related_memory_id=related_memory_id,
                association_type=association_type,
                strength=max(0.0, min(1.0, strength))
            )
            
            db.session.add(association)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating memory association: {str(e)}")
            db.session.rollback()
            return False
    
    def store_conversation_memory(self, user_id: int, session_id: str, summary: str,
                                topics: List[str], mood: Optional[str] = None) -> Optional[ConversationMemory]:
        """Store conversation memory"""
        try:
            conv_memory = ConversationMemory(
                user_id=user_id,
                session_id=session_id,
                summary=summary,
                key_topics=json.dumps(topics),
                user_mood=mood
            )
            
            db.session.add(conv_memory)
            db.session.commit()
            
            return conv_memory
            
        except Exception as e:
            logger.error(f"Error storing conversation memory: {str(e)}")
            db.session.rollback()
            return None
    
    def get_user_preferences(self, user_id: int, category: Optional[str] = None) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            query = UserPreference.query.filter_by(user_id=user_id)
            
            if category:
                query = query.filter_by(category=category)
            
            preferences = query.all()
            
            result = {}
            for pref in preferences:
                if pref.category not in result:
                    result[pref.category] = {}
                
                # Try to parse JSON values
                try:
                    value = json.loads(pref.preference_value)
                except:
                    value = pref.preference_value
                
                result[pref.category][pref.preference_key] = {
                    'value': value,
                    'confidence': pref.confidence_score,
                    'source': pref.source,
                    'last_confirmed': pref.last_confirmed.isoformat() if pref.last_confirmed else None
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return {}
    
    def update_user_preference(self, user_id: int, category: str, key: str, 
                             value: Any, confidence: float = 0.8, source: str = 'explicit') -> bool:
        """Update a user preference"""
        try:
            preference = UserPreference.query.filter_by(
                user_id=user_id,
                category=category,
                preference_key=key
            ).first()
            
            if preference:
                preference.preference_value = json.dumps(value) if not isinstance(value, str) else value
                preference.confidence_score = max(0.0, min(1.0, confidence))
                preference.source = source
                preference.last_confirmed = datetime.now(timezone.utc)
                preference.updated_at = datetime.now(timezone.utc)
            else:
                preference = UserPreference(
                    user_id=user_id,
                    category=category,
                    preference_key=key,
                    preference_value=json.dumps(value) if not isinstance(value, str) else value,
                    confidence_score=max(0.0, min(1.0, confidence)),
                    source=source,
                    last_confirmed=datetime.now(timezone.utc)
                )
                db.session.add(preference)
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preference: {str(e)}")
            db.session.rollback()
            return False
    
    def cleanup_expired_memories(self) -> int:
        """Clean up expired memories"""
        try:
            now = datetime.now(timezone.utc)
            
            # Find expired memories
            expired_memories = UserMemory.query.filter(
                UserMemory.expires_at < now,
                UserMemory.is_active == True
            ).all()
            
            # Soft delete expired memories
            for memory in expired_memories:
                memory.is_active = False
                memory.updated_at = now
            
            db.session.commit()
            
            logger.info(f"Cleaned up {len(expired_memories)} expired memories")
            return len(expired_memories)
            
        except Exception as e:
            logger.error(f"Error cleaning up expired memories: {str(e)}")
            db.session.rollback()
            return 0
    
    def get_memory_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        try:
            stats = {
                'total_memories': UserMemory.query.filter_by(user_id=user_id, is_active=True).count(),
                'by_type': {},
                'by_importance': {
                    'critical': UserMemory.query.filter(
                        UserMemory.user_id == user_id,
                        UserMemory.is_active == True,
                        UserMemory.importance_score >= 0.8
                    ).count(),
                    'important': UserMemory.query.filter(
                        UserMemory.user_id == user_id,
                        UserMemory.is_active == True,
                        UserMemory.importance_score >= 0.6,
                        UserMemory.importance_score < 0.8
                    ).count(),
                    'normal': UserMemory.query.filter(
                        UserMemory.user_id == user_id,
                        UserMemory.is_active == True,
                        UserMemory.importance_score < 0.6
                    ).count()
                },
                'conversations': ConversationMemory.query.filter_by(user_id=user_id).count(),
                'preferences': UserPreference.query.filter_by(user_id=user_id).count()
            }
            
            # Count by memory type
            memory_types = MemoryType.query.all()
            for mem_type in memory_types:
                count = UserMemory.query.filter_by(
                    user_id=user_id,
                    memory_type_id=mem_type.id,
                    is_active=True
                ).count()
                stats['by_type'][mem_type.name] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting memory statistics: {str(e)}")
            return {}


# Global memory service instance
memory_service = MemoryService()


# Helper functions for backward compatibility
def store_user_memory(user_id: int, memory_type: str, title: str, content: str, **kwargs):
    """Store memory for a user"""
    return memory_service.store_memory(user_id, memory_type, title, content, **kwargs)


def get_user_memories(user_id: int, **kwargs):
    """Get user memories"""
    return memory_service.retrieve_memories(user_id, **kwargs)


def search_user_memories(user_id: int, search_term: str, **kwargs):
    """Search user memories"""
    return memory_service.search_memories(user_id, search_term, **kwargs)


def get_user_context(user_id: int):
    """Get user context from memories"""
    memories = memory_service.retrieve_memories(user_id, importance_threshold=0.3, limit=20)
    
    context = {
        'preferences': memory_service.get_user_preferences(user_id),
        'recent_memories': [
            {
                'title': mem.title,
                'content': mem.content,
                'type': mem.memory_type.name,
                'importance': mem.importance_score,
                'created': mem.created_at.isoformat()
            } for mem in memories
        ]
    }
    
    return context