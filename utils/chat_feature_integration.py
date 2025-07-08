"""
Chat Feature Integration

This module shows how to integrate new user features (social, gamification, 
personal growth) with the existing chat/AI assistant functionality.

@module utils.chat_feature_integration
@ai_prompt Use this to understand user's goals, habits, and social connections in chat
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import services
from services.social_service import SocialService
from services.gamification_service import GamificationService
from services.personal_growth_service import PersonalGrowthService
from services.mental_health_resources_service import MentalHealthResourcesService

logger = logging.getLogger(__name__)


class ChatFeatureIntegration:
    """
    Integrates new user features into chat conversations
    
    ## Concept: Context-Aware Chat
    The AI assistant can reference user's goals, achievements, and connections
    """
    
    def __init__(self):
        self.social_service = SocialService()
        self.gamification_service = GamificationService()
        self.growth_service = PersonalGrowthService()
        self.resources_service = MentalHealthResourcesService()
        self.mental_health_handler = None  # Lazy load to avoid circular import
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user context for AI conversations
        
        @ai_prompt Call this to understand user's current state and progress
        """
        context = {
            'personal_growth': self._get_growth_context(user_id),
            'social': self._get_social_context(user_id),
            'gamification': self._get_gamification_context(user_id),
            'suggestions': self._get_contextual_suggestions(user_id)
        }
        
        return context
    
    def _get_growth_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's personal growth context"""
        try:
            # Get active goals
            active_goals = self.growth_service.get_user_goals(user_id, status='active')
            
            # Get recent journal entries
            recent_journals = self.growth_service.get_journal_entries(user_id, limit=5)
            
            # Get active habits
            from models.personal_growth_models import Habit
            habits = Habit.query.filter_by(user_id=user_id, is_active=True).all()
            
            return {
                'active_goals': [{'title': g.title, 'progress': g.progress} for g in active_goals[:3]],
                'recent_mood': recent_journals[0].mood_rating if recent_journals else None,
                'active_habits': len(habits),
                'journaling_streak': self._get_journaling_streak(user_id)
            }
        except Exception as e:
            logger.error(f"Error getting growth context: {e}")
            return {}
    
    def _get_social_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's social context"""
        try:
            # Get user's groups
            groups = self.social_service.get_user_groups(user_id)
            
            # Get connections
            connections = self.social_service.get_user_connections(user_id)
            
            return {
                'support_groups': len(groups),
                'connections': len(connections),
                'community_role': 'active' if len(groups) > 0 else 'exploring'
            }
        except Exception as e:
            logger.error(f"Error getting social context: {e}")
            return {}
    
    def _get_gamification_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's gamification context"""
        try:
            # Get points and level
            points_summary = self.gamification_service.get_user_points_summary(user_id)
            
            # Get recent achievements
            achievements = self.gamification_service.get_user_achievements(user_id)
            recent_achievements = sorted(achievements, 
                                       key=lambda x: x.get('earned_at', ''), 
                                       reverse=True)[:3]
            
            # Get streaks
            streaks = self.gamification_service.get_all_user_streaks(user_id)
            
            return {
                'level': points_summary.get('current_level', 1),
                'total_points': points_summary.get('total_points', 0),
                'recent_achievements': [a['name'] for a in recent_achievements],
                'active_streaks': len([s for s in streaks if s['current_streak'] > 0])
            }
        except Exception as e:
            logger.error(f"Error getting gamification context: {e}")
            return {}
    
    def _get_contextual_suggestions(self, user_id: str) -> List[str]:
        """Get AI suggestions based on user context"""
        suggestions = []
        
        try:
            # Check if user has no goals
            goals = self.growth_service.get_user_goals(user_id, status='active')
            if not goals:
                suggestions.append("Consider setting a personal goal to work towards")
            
            # Check social engagement
            groups = self.social_service.get_user_groups(user_id)
            if not groups:
                suggestions.append("Join a support group to connect with others")
            
            # Check streaks
            streaks = self.gamification_service.get_all_user_streaks(user_id)
            if not any(s['current_streak'] > 0 for s in streaks):
                suggestions.append("Start building healthy habits with daily tracking")
            
            return suggestions[:3]  # Limit to 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    def _get_journaling_streak(self, user_id: str) -> int:
        """Get user's journaling streak"""
        try:
            streak = self.gamification_service.get_user_streak(user_id, 'journaling')
            return streak.current_streak if streak else 0
        except:
            return 0
    
    def detect_crisis_keywords(self, message: str) -> bool:
        """
        Detect potential crisis situations in messages
        
        CRITICAL: This is for support, not diagnosis
        """
        crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'not worth living',
            'hurt myself', 'self harm', 'cutting', 'overdose',
            'no reason to live', 'better off dead', 'final goodbye'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in crisis_keywords)
    
    def get_crisis_response(self, country_code: str = 'US') -> Dict[str, Any]:
        """
        Get immediate crisis resources
        
        NON-NEGOTIABLES: Always provide multiple crisis options
        """
        resources = self.resources_service.get_crisis_resources(country_code)
        
        return {
            'is_crisis': True,
            'resources': [r.to_dict() if hasattr(r, 'to_dict') else r for r in resources[:3]],
            'message': "I'm concerned about you. Please reach out for support:",
            'disclaimer': "If you're in immediate danger, please call 911 or your local emergency number."
        }
    
    def _get_mental_health_handler(self):
        """Lazy load mental health handler to avoid circular import"""
        if self.mental_health_handler is None:
            from utils.mental_health_chat_handler import get_mental_health_handler
            self.mental_health_handler = get_mental_health_handler()
        return self.mental_health_handler
    
    def process_chat_intent(self, user_id: str, message: str, 
                          location: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Process chat message for feature-related intents
        
        Returns action data if the message relates to new features
        """
        # Use enhanced mental health handler for all mental health related messages
        mental_health_response = self._get_mental_health_handler().process_message(
            user_id, message, {'location': location} if location else {}
        )
        
        if mental_health_response:
            # Format the response for chat
            formatted_message = self._get_mental_health_handler().format_chat_response(mental_health_response)
            return {
                'intent': 'mental_health_support',
                'action': mental_health_response['type'],
                'data': {
                    'message': formatted_message,
                    'structured_response': mental_health_response,
                    'requires_immediate_display': mental_health_response.get('requires_immediate_display', False)
                }
            }
        
        message_lower = message.lower()
        
        # Mental health resource intents
        if any(word in message_lower for word in ['therapist', 'counselor', 'psychiatrist', 'therapy']):
            return {
                'intent': 'therapy_search',
                'action': 'search_providers',
                'data': {
                    'message': 'I can help you find therapy options. What location should I search?',
                    'needs_location': True
                }
            }
        
        if any(word in message_lower for word in ['crisis', 'help line', 'hotline', 'emergency']):
            country = location.get('country_code', 'US') if location else 'US'
            resources = self.resources_service.get_crisis_resources(country)
            return {
                'intent': 'crisis_resources',
                'action': 'show_resources',
                'data': {
                    'resources': [r.to_dict() if hasattr(r, 'to_dict') else r for r in resources[:5]],
                    'message': 'Here are crisis support resources available 24/7:'
                }
            }
        
        # Goal-related intents
        if any(word in message_lower for word in ['goal', 'objective', 'achieve']):
            return {
                'intent': 'goal_discussion',
                'action': 'show_goals',
                'data': self.growth_service.get_user_goals(user_id, status='active')
            }
        
        # Habit-related intents
        if any(word in message_lower for word in ['habit', 'routine', 'daily']):
            return {
                'intent': 'habit_discussion',
                'action': 'show_habits',
                'data': {'message': 'Would you like to see your habits or create a new one?'}
            }
        
        # Achievement-related intents
        if any(word in message_lower for word in ['achievement', 'badge', 'progress']):
            return {
                'intent': 'achievement_discussion',
                'action': 'show_achievements',
                'data': self.gamification_service.get_user_achievements(user_id)
            }
        
        # Journal-related intents
        if any(word in message_lower for word in ['journal', 'diary', 'reflect']):
            prompt = self.growth_service.get_random_reflection_prompt()
            return {
                'intent': 'journal_discussion',
                'action': 'suggest_journaling',
                'data': {'prompt': prompt.prompt_text if prompt else None}
            }
        
        # Support group intents
        if any(word in message_lower for word in ['support', 'group', 'community']):
            return {
                'intent': 'social_discussion',
                'action': 'show_groups',
                'data': {'groups': self.social_service.get_user_groups(user_id)}
            }
        
        return None
    
    def reward_chat_engagement(self, user_id: str, message_type: str = 'general'):
        """
        Award points for meaningful chat engagement
        
        @ai_prompt Call this after helpful chat interactions
        """
        points_map = {
            'therapy_discussion': 15,
            'goal_setting': 10,
            'reflection': 10,
            'support_seeking': 5,
            'general': 2
        }
        
        points = points_map.get(message_type, 2)
        
        self.gamification_service.add_points(
            user_id, points, 'wellness', f'Engaged in {message_type} chat'
        )
        
        # Check for chat-related achievements
        self.gamification_service.check_and_award_achievements(
            user_id, 'chat_engagement', 1
        )

    def enhance_response_with_resources(self, user_id: str, response: str, 
                                      detected_mood: Optional[str] = None) -> str:
        """
        Enhance AI response with helpful resources based on context
        
        @ai_prompt Call this to add relevant resources to responses
        """
        enhanced = response
        
        # If user seems distressed, add gentle resource reminder
        if detected_mood in ['sad', 'anxious', 'distressed', 'overwhelmed']:
            enhanced += "\n\n💙 Remember, support is always available. You can type 'resources' to see helpful options."
        
        # Check if user has saved crisis resources
        saved = self.resources_service.get_user_saved_resources(user_id)
        if saved.get('crisis') and detected_mood in ['very_distressed', 'crisis']:
            primary = next((r for r in saved['crisis'] if r.get('is_primary')), None)
            if primary:
                enhanced += f"\n\n📞 Your saved crisis contact: {primary['name']} - {primary['phone_number']}"
        
        return enhanced


# Example usage in chat routes
def enhance_chat_response(user_id: str, ai_response: str) -> str:
    """
    Enhance AI response with user context
    
    Example of how to use in existing chat routes
    """
    integration = ChatFeatureIntegration()
    context = integration.get_user_context(user_id)
    
    # Add contextual information to response
    if context['gamification']['level'] > 5:
        ai_response += f"\n\n🌟 By the way, you're doing amazing at level {context['gamification']['level']}!"
    
    if context['personal_growth']['active_goals']:
        goal = context['personal_growth']['active_goals'][0]
        if goal['progress'] > 80:
            ai_response += f"\n\n🎯 You're so close to completing your goal: {goal['title']}!"
    
    return ai_response


# AI-GENERATED [2024-12-01]
# @see services/* for individual service implementations
# ## Affected Components: api/chat.py, api/enhanced_chat.py
