"""
Memory Service

This service manages user memory operations, providing a comprehensive system
for storing and retrieving chat text and voice interaction data, topics of interest,
and entity memories to enable persistent learning and personalization.

@module services.memory_service
@description User memory management service
"""

import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Set, Union
from sqlalchemy.exc import SQLAlchemyError

# Import db from app factory
from app_factory import db
from models.memory_models import UserMemoryEntry, UserTopicInterest, UserEntityMemory
from utils.enhanced_memory import UserMemory, get_user_memory

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Service for managing user memory, including conversations, topics, and entities.
    This provides a central point for all memory-related operations.
    """
    
    def initialize_memory_for_user(self, user_id: str) -> bool:
        """
        Initialize memory system for a new user
        
        Args:
            user_id: User ID to initialize memory for
            
        Returns:
            bool: Success status
        """
        try:
            # We don't need to check if the user exists - just initialize memory
            # for whatever ID is provided as the system will create entries as needed
                
            # Ensure we have a memory instance for this user
            memory = get_user_memory(user_id)
            
            # Add a welcome message to start their memory history
            memory.add_message(
                'system', 
                'Memory system initialized. I will remember our conversations and learn your preferences over time.'
            )
            
            return True
        except Exception as e:
            logger.error(f"Error initializing memory for user {user_id}: {str(e)}")
            return False
    
    def store_message(self, user_id: str, role: str, content: str, 
                     source_type: str = 'text', emotion: Optional[str] = None,
                     interaction_id: Optional[str] = None, 
                     metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Store a message in the user's memory
        
        Args:
            user_id: User ID
            role: Message role (user, assistant, system)
            content: Message content
            source_type: Source of the message (text, voice)
            emotion: Detected emotion if available
            interaction_id: ID to group related messages
            metadata: Additional metadata
            
        Returns:
            Optional[int]: ID of created memory entry or None on error
        """
        try:
            # First update the in-memory cache via the memory manager
            memory = get_user_memory(user_id)
            memory.add_message(role, content)
            
            # Then ensure we have a direct database record with all details
            metadata_str = json.dumps(metadata) if metadata else None
            
            entry = UserMemoryEntry()
            entry.user_id = user_id
            entry.role = role
            entry.content = content
            entry.source_type = source_type
            entry.emotion = emotion
            entry.interaction_id = interaction_id
            entry.metadata = metadata_str
            entry.timestamp = datetime.datetime.utcnow()
            
            db.session.add(entry)
            db.session.commit()
            
            # If user message, analyze for topics and entities
            if role == 'user':
                self._analyze_message(user_id, content, entry.id)
            
            return entry.id
        except SQLAlchemyError as e:
            logger.error(f"Database error storing message for user {user_id}: {str(e)}")
            db.session.rollback()
            return None
        except Exception as e:
            logger.error(f"Error storing message for user {user_id}: {str(e)}")
            return None
    
    def get_recent_messages(self, user_id: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent messages for a user
        
        Args:
            user_id: User ID
            count: Number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            entries = UserMemoryEntry.query.filter_by(
                user_id=user_id
            ).order_by(UserMemoryEntry.timestamp.desc()).limit(count).all()
            
            # Convert to dictionaries
            return [entry.to_dict() for entry in entries]
        except Exception as e:
            logger.error(f"Error getting recent messages for user {user_id}: {str(e)}")
            return []
    
    def get_topic_interests(self, user_id: str, min_interest: int = 0) -> List[Dict[str, Any]]:
        """
        Get topics of interest for a user
        
        Args:
            user_id: User ID
            min_interest: Minimum interest level to include
            
        Returns:
            List of topic interest dictionaries
        """
        try:
            topics = UserTopicInterest.query.filter(
                UserTopicInterest.user_id == user_id,
                UserTopicInterest.interest_level >= min_interest
            ).order_by(UserTopicInterest.interest_level.desc()).all()
            
            return [topic.to_dict() for topic in topics]
        except Exception as e:
            logger.error(f"Error getting topic interests for user {user_id}: {str(e)}")
            return []
    
    def get_entity_memories(self, user_id: str, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get entity memories for a user
        
        Args:
            user_id: User ID
            entity_type: Optional filter for entity type
            
        Returns:
            List of entity memory dictionaries
        """
        try:
            query = UserEntityMemory.query.filter(UserEntityMemory.user_id == user_id)
            
            if entity_type:
                query = query.filter(UserEntityMemory.entity_type == entity_type)
                
            entities = query.order_by(
                UserEntityMemory.importance.desc(),
                UserEntityMemory.mention_count.desc()
            ).all()
            
            return [entity.to_dict() for entity in entities]
        except Exception as e:
            logger.error(f"Error getting entity memories for user {user_id}: {str(e)}")
            return []
    
    def update_entity_memory(self, user_id: str, entity_name: str, entity_type: str, 
                            attributes: Dict[str, Any], importance: Optional[int] = None) -> bool:
        """
        Update or create an entity memory
        
        Args:
            user_id: User ID
            entity_name: Name of the entity
            entity_type: Type of entity (person, place, thing)
            attributes: Entity attributes
            importance: Optional importance score (1-10)
            
        Returns:
            bool: Success status
        """
        try:
            # Get the memory object to update in-memory cache
            memory = get_user_memory(user_id)
            
            # Update database directly
            entity = UserEntityMemory.query.filter_by(
                user_id=user_id,
                entity_name=entity_name
            ).first()
            
            now = datetime.datetime.utcnow()
            
            if entity:
                # Update existing entity
                existing_attrs = json.loads(entity.attributes) if entity.attributes else {}
                existing_attrs.update(attributes)
                
                entity.attributes = json.dumps(existing_attrs)
                entity.last_mentioned = now
                entity.mention_count += 1
                
                if importance is not None:
                    entity.importance = importance
            else:
                # Create new entity
                entity = UserEntityMemory()
                entity.user_id = user_id
                entity.entity_name = entity_name
                entity.entity_type = entity_type
                entity.attributes = json.dumps(attributes)
                entity.last_mentioned = now
                entity.mention_count = 1
                entity.importance = importance or 5  # Default importance
                db.session.add(entity)
            
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error updating entity memory: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error updating entity memory: {str(e)}")
            return False
    
    def update_topic_interest(self, user_id: str, topic_name: str, 
                             interest_delta: int = 1, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a topic interest for a user
        
        Args:
            user_id: User ID
            topic_name: Name of the topic
            interest_delta: Change in interest level
            metadata: Additional topic metadata
            
        Returns:
            bool: Success status
        """
        try:
            # Get the memory object to update in-memory cache
            memory = get_user_memory(user_id)
            
            # Update database directly
            topic = UserTopicInterest.query.filter_by(
                user_id=user_id,
                topic_name=topic_name
            ).first()
            
            now = datetime.datetime.utcnow()
            
            if topic:
                # Update existing topic
                topic.interest_level += interest_delta
                topic.last_discussed = now
                topic.engagement_count += 1
                
                # Update metadata if provided
                if metadata:
                    existing_meta = json.loads(topic.metadata) if topic.metadata else {}
                    existing_meta.update(metadata)
                    topic.metadata = json.dumps(existing_meta)
            else:
                # Create new topic
                meta_str = json.dumps(metadata) if metadata else None
                topic = UserTopicInterest()
                topic.user_id = user_id
                topic.topic_name = topic_name
                topic.interest_level = max(1, interest_delta)  # Ensure at least 1
                topic.last_discussed = now
                topic.engagement_count = 1
                topic.metadata = meta_str
                db.session.add(topic)
            
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error updating topic interest: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error updating topic interest: {str(e)}")
            return False
    
    def get_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of the user's memory
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing memory summary
        """
        try:
            memory = get_user_memory(user_id)
            
            # Get counts from database for accuracy
            message_count = UserMemoryEntry.query.filter_by(user_id=user_id).count()
            topic_count = UserTopicInterest.query.filter_by(user_id=user_id).count()
            entity_count = UserEntityMemory.query.filter_by(user_id=user_id).count()
            
            # Get top topics
            top_topics = UserTopicInterest.query.filter_by(
                user_id=user_id
            ).order_by(UserTopicInterest.interest_level.desc()).limit(5).all()
            
            # Get most mentioned entities
            top_entities = UserEntityMemory.query.filter_by(
                user_id=user_id
            ).order_by(UserEntityMemory.mention_count.desc()).limit(5).all()
            
            return {
                'message_count': message_count,
                'topic_count': topic_count,
                'entity_count': entity_count,
                'top_topics': [t.topic_name for t in top_topics],
                'top_entities': [e.entity_name for e in top_entities],
                'memory_quality': self._calculate_memory_quality(message_count, topic_count, entity_count)
            }
        except Exception as e:
            logger.error(f"Error getting memory summary for user {user_id}: {str(e)}")
            return {
                'message_count': 0,
                'topic_count': 0,
                'entity_count': 0,
                'top_topics': [],
                'top_entities': [],
                'memory_quality': 'minimal'
            }
    
    def _calculate_memory_quality(self, message_count: int, topic_count: int, entity_count: int) -> str:
        """
        Calculate memory quality based on data quantity and variety
        
        Args:
            message_count: Number of stored messages
            topic_count: Number of tracked topics
            entity_count: Number of remembered entities
            
        Returns:
            String describing memory quality
        """
        total_points = 0
        
        # Points from messages
        if message_count > 1000:
            total_points += 5
        elif message_count > 500:
            total_points += 4
        elif message_count > 100:
            total_points += 3
        elif message_count > 50:
            total_points += 2
        elif message_count > 10:
            total_points += 1
            
        # Points from topics
        if topic_count > 20:
            total_points += 5
        elif topic_count > 10:
            total_points += 4
        elif topic_count > 5:
            total_points += 3
        elif topic_count > 2:
            total_points += 2
        elif topic_count > 0:
            total_points += 1
            
        # Points from entities
        if entity_count > 20:
            total_points += 5
        elif entity_count > 10:
            total_points += 4
        elif entity_count > 5:
            total_points += 3
        elif entity_count > 2:
            total_points += 2
        elif entity_count > 0:
            total_points += 1
            
        # Determine quality based on points
        if total_points >= 12:
            return 'exceptional'
        elif total_points >= 9:
            return 'comprehensive'
        elif total_points >= 6:
            return 'good'
        elif total_points >= 3:
            return 'basic'
        else:
            return 'minimal'
    
    def _analyze_message(self, user_id: str, content: str, message_id: int) -> None:
        """
        Analyze a user message for topics and entities
        
        Args:
            user_id: User ID
            content: Message content
            message_id: ID of the message entry
        """
        try:
            # In a production system, this would use NLP or call an AI service
            # For now, we'll use a simplified approach
            
            # Extract topics based on keywords
            topics_to_check = {
                "travel": ["travel", "trip", "vacation", "flight", "hotel", "destination"],
                "health": ["health", "doctor", "medicine", "exercise", "diet", "fitness"],
                "technology": ["tech", "computer", "software", "app", "device", "digital"],
                "finance": ["money", "finance", "invest", "stock", "budget", "saving"],
                "food": ["food", "recipe", "cook", "restaurant", "meal", "dish"],
                "entertainment": ["movie", "show", "music", "game", "book", "play"],
                "education": ["learn", "study", "school", "course", "teach", "education"],
            }
            
            content_lower = content.lower()
            
            # Check for topics
            for topic, keywords in topics_to_check.items():
                for keyword in keywords:
                    if keyword in content_lower:
                        self.update_topic_interest(user_id, topic)
                        break
            
            # Basic entity extraction for people (very simplified)
            # Look for possessive patterns like "my wife", "my friend", etc.
            relation_patterns = [
                "my wife", "my husband", "my partner", "my boyfriend", 
                "my girlfriend", "my mother", "my father", "my dad", "my mom",
                "my son", "my daughter", "my child", "my brother", "my sister",
                "my friend", "my colleague", "my boss", "my coworker", "my neighbor"
            ]
            
            for pattern in relation_patterns:
                if pattern in content_lower:
                    idx = content_lower.find(pattern)
                    remaining = content_lower[idx + len(pattern):].strip()
                    
                    # Try to extract the name if it follows the pattern
                    if remaining and remaining[0] in [' ', ',', '.', ':', ';']:
                        name_parts = remaining[1:].split()
                        if name_parts:
                            first_name = name_parts[0].strip(',.!?')
                            if first_name and len(first_name) > 1:  # Name should be more than 1 character
                                self.update_entity_memory(
                                    user_id, 
                                    first_name.capitalize(), 
                                    "person", 
                                    {"relation": pattern.replace("my ", "")},
                                    importance=8  # People are usually important
                                )
            
            # Look for place mentions (very simplified)
            place_indicators = ["in ", "at ", "to ", "from "]
            place_types = ["home", "work", "office", "school", "park", "city", "country", "store"]
            
            for indicator in place_indicators:
                for place_type in place_types:
                    pattern = f"{indicator}{place_type}"
                    if pattern in content_lower:
                        self.update_entity_memory(
                            user_id,
                            place_type.capitalize(),
                            "place",
                            {"mentioned_in_context": content[:50] + "..."},
                            importance=6
                        )
            
        except Exception as e:
            logger.error(f"Error analyzing message {message_id}: {str(e)}")


# Create singleton instance
memory_service = MemoryService()

def get_memory_service() -> MemoryService:
    """Get the memory service instance"""
    return memory_service