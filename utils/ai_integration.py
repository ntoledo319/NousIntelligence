"""
AI Integration Module - Cost-optimized AI processing with fallback handling

This module provides unified AI integration capabilities with cost optimization
and fallback mechanisms for reliable AI processing.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Import unified AI service with fallback
try:
    from utils.unified_ai_service import get_unified_ai_service
    UNIFIED_AI_AVAILABLE = True
except ImportError:
    UNIFIED_AI_AVAILABLE = False
    logger.warning("Unified AI service not available")

def generate_ai_text(prompt: str, task_type: str = 'general', 
                    user_id: Optional[str] = None, max_tokens: int = 500,
                    **kwargs) -> Dict[str, Any]:
    """
    Generate AI text response with cost optimization and fallback handling
    
    Args:
        prompt: The input prompt for AI generation
        task_type: Type of task for optimization selection
        user_id: Optional user ID for personalization
        max_tokens: Maximum tokens for response
        **kwargs: Additional parameters
    
    Returns:
        Dict containing success status, response text, and metadata
    """
    try:
        if UNIFIED_AI_AVAILABLE:
            # Use unified AI service for cost-optimized processing
            ai_service = get_unified_ai_service()
            
            # Build messages format
            messages = [{"role": "user", "content": prompt}]
            
            # Add system message for task type optimization
            if task_type != 'general':
                system_message = _get_system_message_for_task(task_type)
                if system_message:
                    messages.insert(0, {"role": "system", "content": system_message})
            
            # Get AI response
            result = ai_service.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                user_id=user_id,
                **kwargs
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'response': result.get('response', ''),
                    'provider': result.get('metadata', {}).get('provider', 'unified_ai'),
                    'tokens_used': result.get('metadata', {}).get('tokens_used', 0),
                    'cost_estimate': result.get('metadata', {}).get('cost_estimate', 0),
                    'task_type': task_type,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Unified AI service failed: {result.get('error', 'Unknown error')}")
        
        # Fallback to simple echo response
        return _fallback_response(prompt, task_type)
        
    except Exception as e:
        logger.error(f"AI text generation failed: {str(e)}")
        return _fallback_response(prompt, task_type, error=str(e))

def analyze_document_content(content: str, analysis_type: str = 'general',
                           user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze document content with AI processing
    
    Args:
        content: Document content to analyze
        analysis_type: Type of analysis to perform
        user_id: Optional user ID
    
    Returns:
        Dict containing analysis results
    """
    try:
        if UNIFIED_AI_AVAILABLE:
            ai_service = get_unified_ai_service()
            
            # Build analysis prompt
            analysis_prompt = _build_analysis_prompt(content, analysis_type)
            
            messages = [{"role": "user", "content": analysis_prompt}]
            
            result = ai_service.chat_completion(
                messages=messages,
                max_tokens=800,
                user_id=user_id
            )
            
            if result.get('success'):
                analysis_result = result.get('response', '')
                
                return {
                    'success': True,
                    'analysis': analysis_result,
                    'content_length': len(content),
                    'analysis_type': analysis_type,
                    'provider': result.get('metadata', {}).get('provider', 'unified_ai'),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Fallback analysis
        return _fallback_document_analysis(content, analysis_type)
        
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}")
        return _fallback_document_analysis(content, analysis_type, error=str(e))

def _get_system_message_for_task(task_type: str) -> Optional[str]:
    """Get optimized system message for specific task types"""
    task_messages = {
        'aa_content_question': """You are a helpful assistant specializing in Alcoholics Anonymous (AA) 
        content and recovery support. Provide clear, supportive responses based on AA principles 
        and Big Book content. Focus on practical guidance for recovery.""",
        
        'dbt_skills': """You are a DBT (Dialectical Behavior Therapy) skills coach. Provide 
        practical guidance on DBT skills including distress tolerance, emotion regulation, 
        interpersonal effectiveness, and mindfulness.""",
        
        'health_advice': """You are a wellness coach providing evidence-based health and 
        wellness guidance. Focus on practical, actionable advice for physical and mental health.""",
        
        'language_learning': """You are a language learning tutor. Provide clear explanations, 
        practice exercises, and encouraging feedback for language learners."""
    }
    
    return task_messages.get(task_type)

def _build_analysis_prompt(content: str, analysis_type: str) -> str:
    """Build analysis prompt based on content and type"""
    base_prompt = f"Please analyze the following content:\n\n{content[:2000]}..."
    
    analysis_instructions = {
        'sentiment': "Analyze the sentiment and emotional tone of this content.",
        'summary': "Provide a concise summary of the key points in this content.",
        'keywords': "Extract the main keywords and topics from this content.",
        'insights': "Provide insights and key takeaways from this content.",
        'general': "Provide a general analysis of this content."
    }
    
    instruction = analysis_instructions.get(analysis_type, analysis_instructions['general'])
    
    return f"{base_prompt}\n\n{instruction}"

def _fallback_response(prompt: str, task_type: str, error: Optional[str] = None) -> Dict[str, Any]:
    """Provide fallback response when AI services are unavailable"""
    fallback_responses = {
        'aa_content_question': "I understand you're asking about AA content. While AI services are currently unavailable, I encourage you to refer to your Big Book or speak with your sponsor for guidance.",
        'dbt_skills': "For DBT skills guidance, please consult your DBT workbook or speak with your therapist for personalized advice.",
        'health_advice': "For health-related questions, please consult with a healthcare professional for personalized advice.",
        'language_learning': "For language learning assistance, consider using practice exercises or speaking with a language tutor.",
        'general': f"Thank you for your message: '{prompt[:100]}...'. AI services are currently unavailable, but your request has been noted."
    }
    
    response = fallback_responses.get(task_type, fallback_responses['general'])
    
    return {
        'success': False,
        'response': response,
        'provider': 'fallback',
        'task_type': task_type,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }

def _fallback_document_analysis(content: str, analysis_type: str, error: Optional[str] = None) -> Dict[str, Any]:
    """Provide fallback document analysis when AI services are unavailable"""
    basic_analysis = {
        'word_count': len(content.split()),
        'character_count': len(content),
        'estimated_reading_time': f"{len(content.split()) // 200 + 1} minutes"
    }
    
    return {
        'success': False,
        'analysis': f"Basic analysis: {basic_analysis}",
        'content_length': len(content),
        'analysis_type': analysis_type,
        'provider': 'fallback',
        'error': error,
        'timestamp': datetime.now().isoformat()
    }