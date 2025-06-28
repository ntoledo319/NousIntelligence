"""
AI Service Manager - Centralized AI service coordination and management

This module provides centralized management of AI services with load balancing,
cost optimization, and provider selection based on task requirements.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Supported AI providers"""
    OPENROUTER = "openrouter"
    UNIFIED = "unified"
    FALLBACK = "fallback"

class TaskType(Enum):
    """AI task types for optimization"""
    CHAT = "chat"
    COMPLETION = "completion"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"

class AIServiceManager:
    """Manages AI services with load balancing and cost optimization"""
    
    def __init__(self):
        self.providers = {}
        self.usage_stats = {}
        self.cost_tracking = {}
        self.provider_health = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers"""
        try:
            from utils.unified_ai_service import get_unified_ai_service
            self.providers[AIProvider.UNIFIED] = get_unified_ai_service()
            self.provider_health[AIProvider.UNIFIED] = True
            logger.info("Unified AI service initialized")
        except ImportError:
            logger.warning("Unified AI service not available")
            self.provider_health[AIProvider.UNIFIED] = False
        
        # Always have fallback available
        self.provider_health[AIProvider.FALLBACK] = True
    
    def get_best_provider(self, task_type: TaskType, user_id: Optional[str] = None) -> AIProvider:
        """
        Select the best provider for a given task type and user
        
        Args:
            task_type: Type of AI task
            user_id: Optional user ID for personalization
            
        Returns:
            Best available AI provider
        """
        # Provider preference based on task type
        task_preferences = {
            TaskType.CHAT: [AIProvider.UNIFIED, AIProvider.FALLBACK],
            TaskType.COMPLETION: [AIProvider.UNIFIED, AIProvider.FALLBACK],
            TaskType.ANALYSIS: [AIProvider.UNIFIED, AIProvider.FALLBACK],
            TaskType.SUMMARIZATION: [AIProvider.UNIFIED, AIProvider.FALLBACK],
            TaskType.TRANSLATION: [AIProvider.UNIFIED, AIProvider.FALLBACK],
            TaskType.CODE_GENERATION: [AIProvider.UNIFIED, AIProvider.FALLBACK]
        }
        
        preferred_providers = task_preferences.get(task_type, [AIProvider.FALLBACK])
        
        # Return first available healthy provider
        for provider in preferred_providers:
            if self.provider_health.get(provider, False):
                return provider
        
        return AIProvider.FALLBACK
    
    def process_request(self, request_data: Dict[str, Any], task_type: TaskType = TaskType.CHAT,
                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process AI request using the best available provider
        
        Args:
            request_data: Request data (messages, prompt, etc.)
            task_type: Type of AI task
            user_id: Optional user ID
            
        Returns:
            AI response with metadata
        """
        provider = self.get_best_provider(task_type, user_id)
        
        try:
            if provider == AIProvider.UNIFIED and self.providers.get(AIProvider.UNIFIED):
                result = self._process_unified_request(request_data, user_id)
            else:
                result = self._process_fallback_request(request_data, task_type)
            
            # Track usage
            self._track_usage(provider, task_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"AI request processing failed with {provider.value}: {str(e)}")
            # Fallback to basic response
            return self._process_fallback_request(request_data, task_type, error=str(e))
    
    def _process_unified_request(self, request_data: Dict[str, Any], user_id: Optional[str]) -> Dict[str, Any]:
        """Process request using unified AI service"""
        unified_service = self.providers[AIProvider.UNIFIED]
        
        # Extract messages or build from prompt
        messages = request_data.get('messages')
        if not messages and 'prompt' in request_data:
            messages = [{"role": "user", "content": request_data['prompt']}]
        
        if not messages:
            raise ValueError("No messages or prompt provided")
        
        result = unified_service.chat_completion(
            messages=messages,
            max_tokens=request_data.get('max_tokens', 500),
            user_id=user_id
        )
        
        if result.get('success'):
            return {
                'success': True,
                'response': result.get('response', ''),
                'provider': AIProvider.UNIFIED.value,
                'metadata': result.get('metadata', {}),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise Exception(result.get('error', 'Unified AI service failed'))
    
    def _process_fallback_request(self, request_data: Dict[str, Any], task_type: TaskType,
                                 error: Optional[str] = None) -> Dict[str, Any]:
        """Process request using fallback logic"""
        # Extract the main content
        content = ""
        if 'messages' in request_data:
            for msg in request_data['messages']:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    break
        elif 'prompt' in request_data:
            content = request_data['prompt']
        
        # Generate appropriate fallback response
        fallback_response = self._generate_fallback_response(content, task_type)
        
        return {
            'success': False,
            'response': fallback_response,
            'provider': AIProvider.FALLBACK.value,
            'metadata': {
                'fallback_reason': error or 'AI services unavailable',
                'task_type': task_type.value
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_fallback_response(self, content: str, task_type: TaskType) -> str:
        """Generate appropriate fallback response based on task type"""
        fallback_responses = {
            TaskType.CHAT: f"I understand you're asking about: '{content[:100]}...'. AI services are currently unavailable, but I've noted your request.",
            TaskType.ANALYSIS: f"Analysis requested for content (length: {len(content)} characters). AI analysis services are currently unavailable.",
            TaskType.SUMMARIZATION: f"Summary requested for content. AI summarization services are currently unavailable.",
            TaskType.TRANSLATION: "Translation services are currently unavailable. Please try again later.",
            TaskType.CODE_GENERATION: "Code generation services are currently unavailable. Please consult documentation or examples.",
            TaskType.COMPLETION: f"Text completion requested. AI completion services are currently unavailable."
        }
        
        return fallback_responses.get(task_type, "AI services are currently unavailable. Please try again later.")
    
    def _track_usage(self, provider: AIProvider, task_type: TaskType, result: Dict[str, Any]):
        """Track usage statistics for optimization"""
        if provider.value not in self.usage_stats:
            self.usage_stats[provider.value] = {}
        
        if task_type.value not in self.usage_stats[provider.value]:
            self.usage_stats[provider.value][task_type.value] = {
                'count': 0,
                'success_count': 0,
                'total_tokens': 0,
                'total_cost': 0.0
            }
        
        stats = self.usage_stats[provider.value][task_type.value]
        stats['count'] += 1
        
        if result.get('success'):
            stats['success_count'] += 1
            
        metadata = result.get('metadata', {})
        stats['total_tokens'] += metadata.get('tokens_used', 0)
        stats['total_cost'] += metadata.get('cost_estimate', 0.0)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            'usage_stats': self.usage_stats,
            'provider_health': {k.value: v for k, v in self.provider_health.items()},
            'timestamp': datetime.now().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all providers"""
        health_results = {}
        
        for provider in AIProvider:
            try:
                if provider == AIProvider.UNIFIED and self.providers.get(AIProvider.UNIFIED):
                    # Test unified service
                    test_result = self._process_unified_request(
                        {'messages': [{'role': 'user', 'content': 'test'}]}, 
                        None
                    )
                    health_results[provider.value] = test_result.get('success', False)
                elif provider == AIProvider.FALLBACK:
                    health_results[provider.value] = True  # Fallback always available
                else:
                    health_results[provider.value] = False
                    
            except Exception as e:
                logger.warning(f"Health check failed for {provider.value}: {str(e)}")
                health_results[provider.value] = False
        
        # Update provider health
        for provider, is_healthy in health_results.items():
            self.provider_health[AIProvider(provider)] = is_healthy
        
        return {
            'provider_health': health_results,
            'timestamp': datetime.now().isoformat()
        }

# Global AI service manager instance
_ai_service_manager = None

def get_ai_service_manager() -> AIServiceManager:
    """Get global AI service manager instance"""
    global _ai_service_manager
    if _ai_service_manager is None:
        _ai_service_manager = AIServiceManager()
    return _ai_service_manager

def process_ai_request(request_data: Dict[str, Any], task_type: str = 'chat',
                      user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for processing AI requests
    
    Args:
        request_data: Request data
        task_type: Type of task as string
        user_id: Optional user ID
        
    Returns:
        AI response
    """
    manager = get_ai_service_manager()
    
    # Convert string task type to enum
    try:
        task_enum = TaskType(task_type.lower())
    except ValueError:
        task_enum = TaskType.CHAT
    
    return manager.process_request(request_data, task_enum, user_id)