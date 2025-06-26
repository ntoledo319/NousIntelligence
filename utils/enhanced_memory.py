"""
Enhanced conversation memory management with personalization features.
This module provides improved memory persistence and recall capabilities.
"""

import json
import datetime
import logging
from typing import Dict, List, Any, Optional, Set
from flask_sqlalchemy import SQLAlchemy
from flask import g, current_app

# Will be set during initialization
db = None

def init_db(database):
    """Initialize the module with a database connection"""
    global db
    db = database

class UserMemory:
    """Enhanced user memory system with personalization and topic tracking"""

    def __init__(self, user_id: str):
        """Initialize memory for a specific user"""
        self.user_id = user_id
        self._load_from_db()

    def _load_from_db(self):
        """Load memory data from database"""
        from models.memory_models import UserMemoryEntry, UserTopicInterest, UserEntityMemory

        # Initialize empty containers
        self.messages = []
        self.contexts = {}
        self.topic_interests = {}
        self.entity_memories = {}

        if not db:
            logging.error("Database not initialized for UserMemory")
            return

        try:
            # Load recent messages
            memory_entries = UserMemoryEntry.query.filter_by(
                user_id=self.user_id
            ).order_by(UserMemoryEntry.timestamp.desc()).limit(50).all()

            for entry in memory_entries:
                self.messages.append({
                    'role': entry.role,
                    'content': entry.content,
                    'timestamp': entry.timestamp
                })

            # Load topic interests
            topic_entries = UserTopicInterest.query.filter_by(
                user_id=self.user_id
            ).all()

            for topic in topic_entries:
                self.topic_interests[topic.topic_name] = {
                    'interest_level': topic.interest_level,
                    'last_discussed': topic.last_discussed,
                    'engagement_count': topic.engagement_count
                }

            # Load entity memories (people, places, things the user has mentioned)
            entity_entries = UserEntityMemory.query.filter_by(
                user_id=self.user_id
            ).all()

            for entity in entity_entries:
                self.entity_memories[entity.entity_name] = {
                    'entity_type': entity.entity_type,
                    'attributes': json.loads(entity.attributes),
                    'last_mentioned': entity.last_mentioned,
                    'mention_count': entity.mention_count
                }

        except Exception as e:
            logging.error(f"Error loading user memory: {str(e)}")
            # Initialize with empty state on error
            self.messages = []
            self.contexts = {}
            self.topic_interests = {}
            self.entity_memories = {}

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        from models import UserMemoryEntry

        if not db:
            logging.error("Database not initialized for UserMemory")
            return

        timestamp = datetime.datetime.utcnow()

        # Add to in-memory cache
        self.messages.insert(0, {
            'role': role,
            'content': content,
            'timestamp': timestamp
        })

        # Persist to database
        try:
            memory_entry = UserMemoryEntry()
            memory_entry.user_id = self.user_id
            memory_entry.role = role
            memory_entry.content = content
            memory_entry.timestamp = timestamp
            db.session.add(memory_entry)
            db.session.commit()

            # If this is a user message, analyze for entities and topics
            if role == 'user':
                self._analyze_message_for_entities_and_topics(content)

        except Exception as e:
            logging.error(f"Error saving message to memory: {str(e)}")
            db.session.rollback()

    def _analyze_message_for_entities_and_topics(self, message: str) -> None:
        """
        Analyze user message to extract entities and topics of interest.
        In a production system, this would use NLP or an AI service.
        This implementation uses a simplified approach.
        """
        # This is a placeholder for a real implementation that would use
        # NLP or call an AI service to extract entities and topics

        # For demonstration, just detect some common topics based on keywords
        topics_to_check = {
            "travel": ["travel", "trip", "vacation", "flight", "hotel", "destination"],
            "health": ["health", "doctor", "medicine", "exercise", "diet", "fitness"],
            "technology": ["tech", "computer", "software", "app", "device", "digital"],
            "finance": ["money", "finance", "budget", "invest", "expense", "saving"],
            "entertainment": ["movie", "music", "book", "show", "game", "concert"],
            "food": ["food", "recipe", "restaurant", "cooking", "meal", "dish"]
        }

        message_lower = message.lower()

        # Check for topic keywords
        for topic, keywords in topics_to_check.items():
            if any(keyword in message_lower for keyword in keywords):
                self._update_topic_interest(topic)

        # For entities, a real implementation would use NER (Named Entity Recognition)
        # This placeholder just checks for simple patterns
        # For example, detect mentions of people with "my [relation]" patterns
        relation_patterns = ["my friend", "my mother", "my father", "my sister",
                           "my brother", "my wife", "my husband", "my partner",
                           "my boss", "my colleague", "my doctor"]

        for pattern in relation_patterns:
            if pattern in message_lower:
                # Find what comes after the pattern
                start_idx = message_lower.find(pattern) + len(pattern)
                if start_idx < len(message_lower):
                    # Look for the name that might follow
                    # This is very simplistic and would be more robust in a real implementation
                    remaining = message_lower[start_idx:].strip()
                    first_word = remaining.split(' ')[0].strip('.,!?')
                    if first_word and len(first_word) > 1:  # Consider it a name if it's not just a single character
                        self._update_entity_memory(first_word, "person", {"relation": pattern.replace("my ", "")})

    def _update_topic_interest(self, topic_name: str) -> None:
        """Update a topic of interest for the user"""
        from models import UserTopicInterest

        if not db:
            logging.error("Database not initialized for UserMemory")
            return

        now = datetime.datetime.utcnow()

        try:
            # Update in-memory cache
            if topic_name in self.topic_interests:
                self.topic_interests[topic_name]['interest_level'] += 1
                self.topic_interests[topic_name]['last_discussed'] = now
                self.topic_interests[topic_name]['engagement_count'] += 1
            else:
                self.topic_interests[topic_name] = {
                    'interest_level': 1,
                    'last_discussed': now,
                    'engagement_count': 1
                }

            # Update database
            topic = UserTopicInterest.query.filter_by(
                user_id=self.user_id,
                topic_name=topic_name
            ).first()

            if topic:
                topic.interest_level += 1
                topic.last_discussed = now
                topic.engagement_count += 1
            else:
                topic = UserTopicInterest()
                topic.user_id = self.user_id
                topic.topic_name = topic_name
                topic.interest_level = 1
                topic.last_discussed = now
                topic.engagement_count = 1
                db.session.add(topic)

            db.session.commit()

        except Exception as e:
            logging.error(f"Error updating topic interest: {str(e)}")
            db.session.rollback()

    def _update_entity_memory(self, entity_name: str, entity_type: str, attributes: Dict[str, Any]) -> None:
        """Update or add an entity memory"""
        from models import UserEntityMemory

        if not db:
            logging.error("Database not initialized for UserMemory")
            return

        now = datetime.datetime.utcnow()

        try:
            # Update in-memory cache
            if entity_name in self.entity_memories:
                # Update existing attributes
                self.entity_memories[entity_name]['attributes'].update(attributes)
                self.entity_memories[entity_name]['last_mentioned'] = now
                self.entity_memories[entity_name]['mention_count'] += 1
            else:
                self.entity_memories[entity_name] = {
                    'entity_type': entity_type,
                    'attributes': attributes,
                    'last_mentioned': now,
                    'mention_count': 1
                }

            # Update database
            entity = UserEntityMemory.query.filter_by(
                user_id=self.user_id,
                entity_name=entity_name
            ).first()

            if entity:
                # Merge existing attributes with new ones
                existing_attrs = json.loads(entity.attributes)
                existing_attrs.update(attributes)

                entity.attributes = json.dumps(existing_attrs)
                entity.last_mentioned = now
                entity.mention_count += 1
            else:
                entity = UserEntityMemory()
                entity.user_id = self.user_id
                entity.entity_name = entity_name
                entity.entity_type = entity_type
                entity.attributes = json.dumps(attributes)
                entity.last_mentioned = now
                entity.mention_count = 1
                db.session.add(entity)

            db.session.commit()

        except Exception as e:
            logging.error(f"Error updating entity memory: {str(e)}")
            db.session.rollback()

    def get_recent_messages(self, count: Optional[int] = None) -> List[Dict[str, str]]:
        """Get recent conversation messages"""
        if count is None or count > len(self.messages):
            return self.messages
        return self.messages[:count]

    def get_topic_summary(self) -> str:
        """Get a summary of the user's topic interests"""
        if not self.topic_interests:
            return "No specific topic interests identified yet."

        # Sort topics by interest level
        sorted_topics = sorted(
            self.topic_interests.items(),
            key=lambda x: x[1]['interest_level'],
            reverse=True
        )

        # Limit to top 5 topics
        top_topics = sorted_topics[:5]

        # Format as readable text
        topic_lines = []
        for topic_name, data in top_topics:
            last_discussed = data['last_discussed'].strftime("%Y-%m-%d") if data['last_discussed'] else "unknown"
            topic_lines.append(f"{topic_name.capitalize()} (interest level: {data['interest_level']}, last discussed: {last_discussed})")

        return "Topic interests: " + "; ".join(topic_lines)

    def get_entity_summary(self) -> str:
        """Get a summary of the entities the user has discussed"""
        if not self.entity_memories:
            return "No specific entities identified in conversations yet."

        # Group entities by type
        entities_by_type = {}
        for entity_name, data in self.entity_memories.items():
            entity_type = data['entity_type']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append((entity_name, data))

        # Format as readable text
        summary_parts = []
        for entity_type, entities in entities_by_type.items():
            # Sort by mention count
            sorted_entities = sorted(entities, key=lambda x: x[1]['mention_count'], reverse=True)

            # Format entities of this type
            if entity_type == "person":
                people = []
                for entity_name, data in sorted_entities[:5]:  # Limit to 5 people
                    relation = data['attributes'].get('relation', 'acquaintance')
                    people.append(f"{entity_name} ({relation})")
                summary_parts.append(f"People: {', '.join(people)}")
            else:
                # Generic formatting for other entity types
                entity_names = [e[0] for e in sorted_entities[:5]]
                if entity_names:
                    summary_parts.append(f"{entity_type.capitalize()}s: {', '.join(entity_names)}")

        if not summary_parts:
            return "No specific entities identified in conversations yet."

        return " ".join(summary_parts)

    def get_memory_context(self) -> str:
        """
        Get a comprehensive context summary for AI prompting
        that includes topic interests, entities, and any other relevant memory
        """
        parts = []

        # Add topic interests
        topic_summary = self.get_topic_summary()
        if "No specific topic" not in topic_summary:
            parts.append(topic_summary)

        # Add entity memories
        entity_summary = self.get_entity_summary()
        if "No specific entities" not in entity_summary:
            parts.append(entity_summary)

        # Join all parts
        if parts:
            return "User Memory:\n" + "\n".join(parts)
        else:
            return ""


# Global registry of user memories
_user_memories = {}

def get_user_memory(user_id: str) -> UserMemory:
    """Get or create a memory object for a user"""
    global _user_memories

    if user_id not in _user_memories:
        _user_memories[user_id] = UserMemory(user_id)

    return _user_memories[user_id]