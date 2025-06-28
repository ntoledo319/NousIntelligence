"""
Context-Aware AI Assistant
Enhances unified AI service with contextual memory across sessions
for natural, human-like interactions that remember user preferences
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict, deque

from utils.unified_ai_service import UnifiedAIService
from services.predictive_analytics import predictive_engine

logger = logging.getLogger(__name__)

class ConversationContext:
    """Manages conversation context and memory"""
    
    def __init__(self, max_memory_items: int = 100):
        """Initialize conversation context"""
        self.max_memory_items = max_memory_items
        self.short_term_memory = deque(maxlen=max_memory_items)
        self.long_term_memory = {}
        self.user_preferences = {}
        self.conversation_patterns = {}
        
    def add_interaction(self, user_input: str, ai_response: str, context: Dict[str, Any]):
        """Add interaction to memory"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'context': context,
            'interaction_id': len(self.short_term_memory)
        }
        
        self.short_term_memory.append(interaction)
        self._update_patterns(interaction)
    
    def _update_patterns(self, interaction: Dict[str, Any]):
        """Update conversation patterns"""
        user_input = interaction['user_input'].lower()
        
        # Track question types
        if '?' in user_input:
            question_type = self._classify_question(user_input)
            if question_type not in self.conversation_patterns:
                self.conversation_patterns[question_type] = 0
            self.conversation_patterns[question_type] += 1
        
        # Track topics
        topics = self._extract_topics(user_input)
        for topic in topics:
            if 'topics' not in self.conversation_patterns:
                self.conversation_patterns['topics'] = {}
            if topic not in self.conversation_patterns['topics']:
                self.conversation_patterns['topics'][topic] = 0
            self.conversation_patterns['topics'][topic] += 1
    
    def _classify_question(self, text: str) -> str:
        """Classify type of question"""
        if any(word in text for word in ['what', 'how', 'why', 'when', 'where']):
            return 'informational'
        elif any(word in text for word in ['can', 'could', 'would', 'should']):
            return 'capability'
        elif any(word in text for word in ['help', 'assist', 'support']):
            return 'assistance'
        else:
            return 'general'
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        
        # Simple keyword-based topic extraction
        topic_keywords = {
            'tasks': ['task', 'todo', 'reminder', 'schedule'],
            'weather': ['weather', 'rain', 'sunny', 'cloudy'],
            'health': ['health', 'wellness', 'medicine', 'exercise'],
            'music': ['music', 'song', 'playlist', 'spotify'],
            'calendar': ['calendar', 'meeting', 'event', 'appointment'],
            'finance': ['money', 'budget', 'expense', 'payment']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def get_relevant_context(self, current_input: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant context from memory"""
        relevant_interactions = []
        current_topics = self._extract_topics(current_input.lower())
        
        # Search recent interactions for relevance
        for interaction in reversed(list(self.short_term_memory)):
            if len(relevant_interactions) >= limit:
                break
                
            # Check topic relevance
            interaction_topics = self._extract_topics(interaction['user_input'].lower())
            if any(topic in current_topics for topic in interaction_topics):
                relevant_interactions.append(interaction)
            
            # Always include very recent interactions
            elif len(relevant_interactions) < 2:
                relevant_interactions.append(interaction)
        
        return relevant_interactions

class UserPersonality:
    """Manages user personality and preference modeling"""
    
    def __init__(self):
        """Initialize user personality model"""
        self.traits = {
            'formality': 0.5,  # 0 = very casual, 1 = very formal
            'verbosity': 0.5,  # 0 = brief, 1 = detailed
            'technicality': 0.5,  # 0 = simple, 1 = technical
            'proactivity': 0.5,  # 0 = reactive, 1 = proactive
            'emotionality': 0.5  # 0 = logical, 1 = emotional
        }
        
        self.preferences = {
            'response_style': 'balanced',
            'preferred_features': [],
            'communication_times': [],
            'topics_of_interest': []
        }
        
        self.interaction_count = 0
    
    def update_from_interaction(self, user_input: str, feedback_score: float = None):
        """Update personality model from user interaction"""
        self.interaction_count += 1
        
        # Analyze formality
        formal_indicators = ['please', 'thank you', 'could you', 'would you']
        casual_indicators = ['hey', 'yo', 'sup', 'gonna', 'wanna']
        
        formal_score = sum(1 for indicator in formal_indicators if indicator in user_input.lower())
        casual_score = sum(1 for indicator in casual_indicators if indicator in user_input.lower())
        
        if formal_score > casual_score:
            self.traits['formality'] = min(1.0, self.traits['formality'] + 0.1)
        elif casual_score > formal_score:
            self.traits['formality'] = max(0.0, self.traits['formality'] - 0.1)
        
        # Analyze verbosity preference
        if len(user_input.split()) > 20:
            self.traits['verbosity'] = min(1.0, self.traits['verbosity'] + 0.05)
        elif len(user_input.split()) < 5:
            self.traits['verbosity'] = max(0.0, self.traits['verbosity'] - 0.05)
        
        # Analyze technical language
        technical_terms = ['api', 'database', 'algorithm', 'configuration', 'parameter']
        if any(term in user_input.lower() for term in technical_terms):
            self.traits['technicality'] = min(1.0, self.traits['technicality'] + 0.1)
    
    def get_response_style(self) -> Dict[str, Any]:
        """Get recommended response style based on personality"""
        return {
            'formality_level': 'formal' if self.traits['formality'] > 0.6 else 'casual',
            'detail_level': 'detailed' if self.traits['verbosity'] > 0.6 else 'brief',
            'technical_level': 'technical' if self.traits['technicality'] > 0.6 else 'simple',
            'proactive_suggestions': self.traits['proactivity'] > 0.5,
            'emotional_tone': 'warm' if self.traits['emotionality'] > 0.6 else 'professional'
        }

class ContextAwareAIAssistant:
    """Main context-aware AI assistant with enhanced memory"""
    
    def __init__(self):
        """Initialize context-aware AI assistant"""
        self.ai_service = UnifiedAIService()
        self.db_path = Path("instance/context_memory.db")
        self.init_database()
        
        # Per-user context and personality
        self.user_contexts = {}
        self.user_personalities = {}
        
        # Global knowledge and patterns
        self.global_patterns = {}
        
        logger.info("Context-Aware AI Assistant initialized")
    
    def init_database(self):
        """Initialize context memory database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    context_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    interaction_type TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    preference_type TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, preference_type)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def get_user_context(self, user_id: str) -> ConversationContext:
        """Get or create user conversation context"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = ConversationContext()
            self._load_user_context_from_db(user_id)
        
        return self.user_contexts[user_id]
    
    def get_user_personality(self, user_id: str) -> UserPersonality:
        """Get or create user personality model"""
        if user_id not in self.user_personalities:
            self.user_personalities[user_id] = UserPersonality()
            self._load_user_personality_from_db(user_id)
        
        return self.user_personalities[user_id]
    
    def _load_user_context_from_db(self, user_id: str):
        """Load user context from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_input, ai_response, context_data, timestamp
                    FROM conversation_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                """, (user_id,))
                
                context = self.user_contexts[user_id]
                for row in cursor.fetchall():
                    user_input, ai_response, context_data, timestamp = row
                    parsed_context = json.loads(context_data) if context_data else {}
                    
                    context.add_interaction(user_input, ai_response, parsed_context)
                    
        except Exception as e:
            logger.error(f"Error loading user context: {e}")
    
    def _load_user_personality_from_db(self, user_id: str):
        """Load user personality from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT preference_type, preference_value, confidence
                    FROM user_preferences
                    WHERE user_id = ?
                """, (user_id,))
                
                personality = self.user_personalities[user_id]
                for row in cursor.fetchall():
                    pref_type, pref_value, confidence = row
                    
                    if pref_type in personality.traits:
                        personality.traits[pref_type] = float(pref_value)
                    elif pref_type in personality.preferences:
                        personality.preferences[pref_type] = json.loads(pref_value)
                        
        except Exception as e:
            logger.error(f"Error loading user personality: {e}")
    
    async def process_with_context(self, user_input: str, user_id: str, 
                                  additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input with full context awareness"""
        try:
            # Get user context and personality
            context = self.get_user_context(user_id)
            personality = self.get_user_personality(user_id)
            
            # Get relevant conversation history
            relevant_history = context.get_relevant_context(user_input)
            
            # Get predictions for proactive assistance
            predictions = predictive_engine.get_active_predictions(user_id)
            
            # Build comprehensive context
            full_context = self._build_comprehensive_context(
                user_input, user_id, context, personality, 
                relevant_history, predictions, additional_context
            )
            
            # Generate context-aware response
            ai_response = await self._generate_context_aware_response(
                user_input, full_context, personality
            )
            
            # Update memory and personality
            context.add_interaction(user_input, ai_response['content'], full_context)
            personality.update_from_interaction(user_input)
            
            # Store in database
            self._store_interaction(user_id, user_input, ai_response['content'], full_context)
            self._update_user_preferences(user_id, personality)
            
            return {
                'response': ai_response['content'],
                'context_used': len(relevant_history),
                'personality_traits': personality.get_response_style(),
                'predictions_considered': len(predictions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing with context: {e}")
            return {
                'response': "I'm having trouble processing that with full context. Let me try a simpler approach.",
                'error': str(e)
            }
    
    def _build_comprehensive_context(self, user_input: str, user_id: str,
                                   context: ConversationContext, personality: UserPersonality,
                                   relevant_history: List[Dict], predictions: List[Dict],
                                   additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build comprehensive context for AI response"""
        return {
            'user_input': user_input,
            'user_id': user_id,
            'current_time': datetime.now().isoformat(),
            'conversation_history': relevant_history,
            'user_personality': personality.get_response_style(),
            'conversation_patterns': context.conversation_patterns,
            'active_predictions': predictions,
            'interaction_count': personality.interaction_count,
            'additional_context': additional_context or {}
        }
    
    async def _generate_context_aware_response(self, user_input: str, 
                                             full_context: Dict[str, Any],
                                             personality: UserPersonality) -> Dict[str, Any]:
        """Generate AI response with full context awareness"""
        # Build context-aware prompt
        response_style = personality.get_response_style()
        
        # Summarize conversation history
        history_summary = self._summarize_conversation_history(
            full_context.get('conversation_history', [])
        )
        
        # Format predictions
        predictions_text = self._format_predictions(
            full_context.get('active_predictions', [])
        )
        
        prompt = f"""
        You are NOUS, a context-aware personal assistant. Respond to the user with full awareness of:
        
        Current request: "{user_input}"
        
        User personality and preferences:
        - Formality: {response_style['formality_level']}
        - Detail preference: {response_style['detail_level']}
        - Technical level: {response_style['technical_level']}
        - Emotional tone: {response_style['emotional_tone']}
        
        Recent conversation context:
        {history_summary}
        
        Relevant predictions:
        {predictions_text}
        
        Response guidelines:
        1. Reference relevant conversation history naturally
        2. Adapt your communication style to user preferences
        3. Be proactive with helpful suggestions if appropriate
        4. Maintain conversation continuity
        5. Use predictions to anticipate needs
        
        Respond as NOUS would, maintaining personality and context awareness.
        """
        
        response = self.ai_service.chat_completion([
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ])
        
        return response
    
    def _summarize_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Summarize conversation history for context"""
        if not history:
            return "No recent conversation history."
        
        summary_parts = []
        for interaction in history[-3:]:  # Last 3 interactions
            timestamp = interaction.get('timestamp', '')
            user_msg = interaction.get('user_input', '')[:50] + "..."
            ai_msg = interaction.get('ai_response', '')[:50] + "..."
            
            summary_parts.append(f"User: {user_msg} | AI: {ai_msg}")
        
        return "\n".join(summary_parts)
    
    def _format_predictions(self, predictions: List[Dict[str, Any]]) -> str:
        """Format predictions for context prompt"""
        if not predictions:
            return "No active predictions."
        
        formatted = []
        for pred in predictions[:3]:  # Top 3 predictions
            pred_type = pred.get('type', 'unknown')
            prediction_text = pred.get('prediction', '')
            confidence = pred.get('confidence', 0)
            
            formatted.append(f"- {pred_type}: {prediction_text} (confidence: {confidence:.1%})")
        
        return "\n".join(formatted)
    
    def _store_interaction(self, user_id: str, user_input: str, ai_response: str, 
                          context: Dict[str, Any]):
        """Store interaction in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO conversation_history 
                    (user_id, user_input, ai_response, context_data, session_id, interaction_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id, user_input, ai_response, json.dumps(context),
                    context.get('session_id', 'default'), 'context_aware'
                ))
        except Exception as e:
            logger.error(f"Error storing interaction: {e}")
    
    def _update_user_preferences(self, user_id: str, personality: UserPersonality):
        """Update user preferences in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for trait, value in personality.traits.items():
                    conn.execute("""
                        INSERT OR REPLACE INTO user_preferences 
                        (user_id, preference_type, preference_value, confidence)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, trait, str(value), 0.8))
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user interaction patterns"""
        try:
            context = self.get_user_context(user_id)
            personality = self.get_user_personality(user_id)
            
            insights = {
                'interaction_count': personality.interaction_count,
                'personality_traits': personality.traits,
                'conversation_patterns': context.conversation_patterns,
                'preferred_topics': [],
                'communication_style': personality.get_response_style(),
                'context_retention': len(context.short_term_memory)
            }
            
            # Extract preferred topics
            if 'topics' in context.conversation_patterns:
                topics = context.conversation_patterns['topics']
                insights['preferred_topics'] = sorted(
                    topics.items(), key=lambda x: x[1], reverse=True
                )[:5]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting user insights: {e}")
            return {}
    
    def reset_user_context(self, user_id: str):
        """Reset user context and personality (for debugging)"""
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
        if user_id in self.user_personalities:
            del self.user_personalities[user_id]
        
        logger.info(f"Reset context for user {user_id}")
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user context and personality data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get conversation history
                cursor = conn.execute("""
                    SELECT * FROM conversation_history WHERE user_id = ?
                    ORDER BY timestamp DESC
                """, (user_id,))
                
                conversations = [dict(zip([col[0] for col in cursor.description], row)) 
                               for row in cursor.fetchall()]
                
                # Get preferences
                cursor = conn.execute("""
                    SELECT * FROM user_preferences WHERE user_id = ?
                """, (user_id,))
                
                preferences = [dict(zip([col[0] for col in cursor.description], row)) 
                             for row in cursor.fetchall()]
                
                return {
                    'user_id': user_id,
                    'conversation_history': conversations,
                    'preferences': preferences,
                    'insights': self.get_user_insights(user_id),
                    'exported_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return {}

# Global instance
context_ai = ContextAwareAIAssistant()