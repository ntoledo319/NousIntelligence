"""
Chat Memory Integration Module

This module integrates the memory service with the chat processing system,
ensuring all user interactions via text and voice are stored, accumulated,
and referenced during future conversations.

@module utils.chat_memory_integration
@description Integration between chat processing and memory systems
"""

import logging
from typing import Dict, List, Any, Optional, Union
import uuid

from services.memory_service import get_memory_service
from utils.chat_processor import get_chat_processor

logger = logging.getLogger(__name__)

class ChatMemoryIntegration:
    """
    Integrates the memory service with chat processing to ensure all
    interactions are stored and memory is incorporated into responses.
    """

    def __init__(self):
        """Initialize the integration"""
        self.memory_service = get_memory_service()
        self.chat_processor = get_chat_processor()

    def process_user_message(self, user_id: str, message: str, source_type: str = 'text',
                           emotion: Optional[str] = None) -> str:
        """
        Process a user message, store it in memory, and get a response

        Args:
            user_id: User ID
            message: User message content
            source_type: Source of the message (text, voice)
            emotion: Detected emotion if available

        Returns:
            Assistant response
        """
        # Generate a unique interaction ID to group this exchange
        interaction_id = str(uuid.uuid4())

        # Store the user message in memory
        self.memory_service.store_message(
            user_id=user_id,
            role='user',
            content=message,
            source_type=source_type,
            emotion=emotion,
            interaction_id=interaction_id
        )

        # Get memory context for enhanced responses
        memory_context = self._get_memory_context(user_id)

        # Process the message with memory context in the session
        session = {"memory_context": memory_context}
        response_data = self.chat_processor.process_message(
            message=message,
            user_id=user_id,
            session=session
        )

        # Extract the response text from the response data
        response = response_data.get('response', '')

        # Store the assistant's response in memory
        self.memory_service.store_message(
            user_id=user_id,
            role='assistant',
            content=response,
            source_type='text',  # Assistant responses are always text initially
            interaction_id=interaction_id
        )

        return response

    def process_voice_input(self, user_id: str, transcript: str,
                          emotion: Optional[str] = None,
                          audio_features: Optional[Dict[str, Any]] = None) -> str:
        """
        Process voice input with enhanced emotion and audio feature tracking

        Args:
            user_id: User ID
            transcript: Transcribed voice input
            emotion: Detected emotion from voice
            audio_features: Additional features extracted from audio

        Returns:
            Assistant response
        """
        # Store voice-specific metadata
        metadata = {'audio_features': audio_features} if audio_features else {}

        # Generate a unique interaction ID
        interaction_id = str(uuid.uuid4())

        # Store the voice message with source type and emotion
        self.memory_service.store_message(
            user_id=user_id,
            role='user',
            content=transcript,
            source_type='voice',
            emotion=emotion,
            interaction_id=interaction_id,
            metadata=metadata
        )

        # Get memory context enriched with emotion awareness
        memory_context = self._get_memory_context(user_id, include_emotions=True)

        # Create session with voice context
        voice_session = {
            "memory_context": memory_context,
            "source_type": "voice",
            "emotion": emotion
        }

        # Process with appropriate parameters
        response_data = self.chat_processor.process_message(
            message=transcript,
            user_id=user_id,
            session=voice_session
        )

        # Extract the response text from the response data
        response = response_data.get('response', '')

        # Store the assistant's response
        self.memory_service.store_message(
            user_id=user_id,
            role='assistant',
            content=response,
            source_type='text',
            interaction_id=interaction_id
        )

        return response

    def _get_memory_context(self, user_id: str, include_emotions: bool = False) -> Dict[str, Any]:
        """
        Get memory context to enhance chat responses

        Args:
            user_id: User ID
            include_emotions: Whether to include emotional context

        Returns:
            Memory context dictionary
        """
        try:
            # Get recent conversation history
            recent_messages = self.memory_service.get_recent_messages(user_id, count=10)

            # Get user's interests
            interests = self.memory_service.get_topic_interests(user_id, min_interest=3)

            # Get important entities
            entities = self.memory_service.get_entity_memories(user_id)
            important_entities = [e for e in entities if e.get('importance', 0) >= 7]

            # Format conversation history
            conversation_history = []
            for msg in reversed(recent_messages):  # Oldest first
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role and content:
                    # Add emotion if available and requested
                    if include_emotions and msg.get('emotion'):
                        content = f"[{msg['emotion']}] {content}"

                    conversation_history.append({
                        'role': role,
                        'content': content
                    })

            # Build context dictionary
            context = {
                'conversation_history': conversation_history,
                'user_interests': [i.get('topic_name') for i in interests],
                'important_entities': {
                    e.get('entity_name'): e.get('attributes', {}) for e in important_entities
                }
            }

            return context
        except Exception as e:
            logger.error(f"Error building memory context: {str(e)}")
            # Return minimal context on error
            return {
                'conversation_history': [],
                'user_interests': [],
                'important_entities': {}
            }


# Create singleton instance
chat_memory_integration = ChatMemoryIntegration()

def get_chat_memory_integration():
    """Get the chat memory integration instance"""
    return chat_memory_integration