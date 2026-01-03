"""
Consolidated AI Services Helper
Combines AI Helper, Gemini, HuggingFace, NLP, and unified AI functionality
"""

import logging
from typing import Dict, Any, List, Optional, Union
import asyncio

logger = logging.getLogger(__name__)

class ConsolidatedAIServices:
    """Unified AI Services interface combining all AI integrations"""
    
    def __init__(self):
        self.services = {}
        self.fallback_responses = {
            'chat': "I'm here to help! However, AI services are currently limited.",
            'analysis': "Analysis capability is currently limited.",
            'generation': "Content generation is currently limited."
        }
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all AI services with fallback handling"""
        try:
            self.services['unified'] = self._init_unified_ai()
            self.services['gemini'] = self._init_gemini_service()
            self.services['huggingface'] = self._init_huggingface_service()
            self.services['nlp'] = self._init_nlp_service()
            self.services['enhanced'] = self._init_enhanced_ai()
        except Exception as e:
            logger.warning(f"AI services initialization warning: {e}")
    
    # Unified AI functionality
    def _init_unified_ai(self):
        """Initialize Unified AI service"""
        try:
            from utils.unified_ai_service import UnifiedAIService
            return UnifiedAIService()
        except ImportError:
            try:
                from utils.ai_helper import AIHelper
                return AIHelper()
            except ImportError:
                logger.warning("Unified AI service not available, using fallback")
                return self._create_fallback_service('unified_ai')
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion using best available AI service"""
        if 'unified' in self.services:
            try:
                return self.services['unified'].chat_completion(messages, **kwargs)
            except Exception as e:
                logger.error(f"Unified AI chat failed: {e}")
        
        if 'gemini' in self.services:
            try:
                return self.services['gemini'].generate_response(messages[-1].get('content', ''))
            except Exception as e:
                logger.error(f"Gemini chat failed: {e}")
        
        return {
            'success': False,
            'response': self.fallback_responses['chat'],
            'fallback': True
        }
    
    def analyze_text(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze text using AI services"""
        if 'nlp' in self.services:
            try:
                return self.services['nlp'].analyze_text(text, analysis_type)
            except Exception as e:
                logger.error(f"NLP analysis failed: {e}")
        
        if 'unified' in self.services:
            try:
                analysis_prompt = f"Analyze the following text for {analysis_type} insights: {text}"
                return self.services['unified'].chat_completion([
                    {"role": "user", "content": analysis_prompt}
                ])
            except Exception as e:
                logger.error(f"Unified AI analysis failed: {e}")
        
        return {
            'success': False,
            'analysis': self.fallback_responses['analysis'],
            'fallback': True
        }
    
    # Gemini AI functionality
    def _init_gemini_service(self):
        """Initialize Gemini AI service"""
        try:
            from utils.gemini_helper import GeminiHelper
            return GeminiHelper()
        except ImportError:
            logger.warning("Gemini helper not available, using fallback")
            return self._create_fallback_service('gemini')
    
    def generate_content(self, prompt: str, model: str = "gemini-pro") -> Dict[str, Any]:
        """Generate content using Gemini AI"""
        if 'gemini' in self.services:
            try:
                return self.services['gemini'].generate_content(prompt, model)
            except Exception as e:
                logger.error(f"Gemini content generation failed: {e}")
        
        return self.chat_completion([{"role": "user", "content": prompt}])
    
    def analyze_image(self, image_path: str, prompt: str = "Describe this image") -> Dict[str, Any]:
        """Analyze image using Gemini Vision"""
        if 'gemini' in self.services:
            try:
                return self.services['gemini'].analyze_image(image_path, prompt)
            except Exception as e:
                logger.error(f"Gemini image analysis failed: {e}")
        
        return {
            'success': False,
            'analysis': "Image analysis not available",
            'fallback': True
        }
    
    # HuggingFace functionality
    def _init_huggingface_service(self):
        """Initialize HuggingFace service"""
        try:
            from utils.huggingface_helper import HuggingFaceHelper
            return HuggingFaceHelper()
        except ImportError:
            logger.warning("HuggingFace helper not available, using fallback")
            return self._create_fallback_service('huggingface')
    
    def text_to_speech(self, text: str, voice: str = "default") -> Dict[str, Any]:
        """Convert text to speech using HuggingFace"""
        if 'huggingface' in self.services:
            try:
                return self.services['huggingface'].text_to_speech(text, voice)
            except Exception as e:
                logger.error(f"HuggingFace TTS failed: {e}")
        
        return {
            'success': False,
            'audio_url': None,
            'error': 'Text-to-speech not available',
            'fallback': True
        }
    
    def speech_to_text(self, audio_data: bytes) -> Dict[str, Any]:
        """Convert speech to text using HuggingFace"""
        if 'huggingface' in self.services:
            try:
                return self.services['huggingface'].speech_to_text(audio_data)
            except Exception as e:
                logger.error(f"HuggingFace STT failed: {e}")
        
        return {
            'success': False,
            'transcription': '',
            'error': 'Speech-to-text not available',
            'fallback': True
        }
    
    def classify_text(self, text: str, labels: List[str] = None) -> Dict[str, Any]:
        """Classify text using HuggingFace models"""
        if 'huggingface' in self.services:
            try:
                return self.services['huggingface'].classify_text(text, labels)
            except Exception as e:
                logger.error(f"HuggingFace classification failed: {e}")
        
        return {
            'success': False,
            'classification': [],
            'error': 'Text classification not available',
            'fallback': True
        }
    
    # NLP functionality
    def _init_nlp_service(self):
        """Initialize NLP service"""
        try:
            from utils.nlp_helper import NLPHelper
            return NLPHelper()
        except ImportError:
            logger.warning("NLP helper not available, using fallback")
            return self._create_fallback_service('nlp')
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        if 'nlp' in self.services:
            try:
                return self.services['nlp'].extract_entities(text)
            except Exception as e:
                logger.error(f"NLP entity extraction failed: {e}")
        
        return {
            'success': False,
            'entities': [],
            'error': 'Entity extraction not available',
            'fallback': True
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if 'nlp' in self.services:
            try:
                return self.services['nlp'].analyze_sentiment(text)
            except Exception as e:
                logger.error(f"NLP sentiment analysis failed: {e}")
        
        return {
            'success': False,
            'sentiment': 'neutral',
            'confidence': 0.0,
            'error': 'Sentiment analysis not available',
            'fallback': True
        }
    
    def summarize_text(self, text: str, max_length: int = 100) -> Dict[str, Any]:
        """Summarize text content"""
        if 'nlp' in self.services:
            try:
                return self.services['nlp'].summarize_text(text, max_length)
            except Exception as e:
                logger.error(f"NLP summarization failed: {e}")
        
        # Fallback to simple truncation
        summary = text[:max_length] + "..." if len(text) > max_length else text
        return {
            'success': True,
            'summary': summary,
            'fallback': True
        }
    
    # Enhanced AI functionality
    def _init_enhanced_ai(self):
        """Initialize Enhanced AI service"""
        try:
            from utils.enhanced_ai_system import EnhancedAISystem
            return EnhancedAISystem()
        except ImportError:
            logger.warning("Enhanced AI system not available, using fallback")
            return self._create_fallback_service('enhanced_ai')
    
    def research_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process research-type queries with enhanced AI"""
        if 'enhanced' in self.services:
            try:
                return self.services['enhanced'].research_query(query, context)
            except Exception as e:
                logger.error(f"Enhanced AI research failed: {e}")
        
        return self.chat_completion([
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": query}
        ])
    
    def therapeutic_response(self, message: str, emotional_state: str = None) -> Dict[str, Any]:
        """Generate therapeutic responses with enhanced AI"""
        if 'enhanced' in self.services:
            try:
                return self.services['enhanced'].therapeutic_response(message, emotional_state)
            except Exception as e:
                logger.error(f"Enhanced AI therapeutic response failed: {e}")
        
        therapeutic_prompt = f"Provide a supportive, therapeutic response to: {message}"
        if emotional_state:
            therapeutic_prompt += f" (User's emotional state: {emotional_state})"
        
        return self.chat_completion([
            {"role": "system", "content": "You are a supportive therapeutic assistant."},
            {"role": "user", "content": therapeutic_prompt}
        ])
    
    def _create_fallback_service(self, service_name: str):
        """Create a fallback service object"""
        class FallbackService:
            def __init__(self, name):
                self.name = name
            
            def __getattr__(self, method_name):
                def fallback_method(*args, **kwargs):
                    return {
                        'success': False,
                        'error': f'{self.name.title()} service not available',
                        'fallback': True
                    }
                return fallback_method
        
        return FallbackService(service_name)
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all AI services"""
        health_status = {}
        
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'health_check'):
                    health_status[service_name] = service.health_check()
                else:
                    health_status[service_name] = {'status': 'available', 'service': service_name}
            except Exception as e:
                health_status[service_name] = {'status': 'error', 'error': str(e)}
        
        return {
            'overall_status': 'healthy' if all(s.get('status') != 'error' for s in health_status.values()) else 'degraded',
            'services': health_status
        }
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Get cost report from AI services"""
        if 'unified' in self.services and hasattr(self.services['unified'], 'get_cost_report'):
            try:
                return self.services['unified'].get_cost_report()
            except Exception as e:
                logger.error(f"Cost report failed: {e}")
        
        return {
            'total_cost': 0.0,
            'usage_stats': {},
            'optimization_recommendations': ['Use consolidated AI services for better cost management']
        }

# Global instance
_ai_services = None

def get_ai_services() -> ConsolidatedAIServices:
    """Get the global AI services instance"""
    global _ai_services
    if _ai_services is None:
        _ai_services = ConsolidatedAIServices()
    return _ai_services

# Backward compatibility functions
def chat_completion(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Backward compatibility for chat completion"""
    return get_ai_services().chat_completion(messages, **kwargs)

def generate_content(prompt: str, model: str = "gemini-pro") -> Dict[str, Any]:
    """Backward compatibility for content generation"""
    return get_ai_services().generate_content(prompt, model)

def analyze_text(text: str, analysis_type: str = "general") -> Dict[str, Any]:
    """Backward compatibility for text analysis"""
    return get_ai_services().analyze_text(text, analysis_type)

def text_to_speech(text: str, voice: str = "default") -> Dict[str, Any]:
    """Backward compatibility for TTS"""
    return get_ai_services().text_to_speech(text, voice)