"""
MTM-CE Integration Hub - Comprehensive Cross-Service Intelligence
Orchestrates all MTM-CE enhanced systems for maximum synergy and performance
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class IntegrationContext:
    """Context for cross-service integration"""
    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    services_active: List[str] = field(default_factory=list)
    learning_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class MTMCEIntegrationHub:
    """Central hub for coordinating all MTM-CE enhanced systems"""
    
    def __init__(self):
        """Initialize integration hub with all available services"""
        self.services = {}
        self.learning_pipeline = None
        self.performance_tracker = {}
        
        # Initialize service connections
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize connections to all MTM-CE enhanced services"""
        try:
            # Adaptive AI System
            from utils.adaptive_ai_system import get_adaptive_ai
            self.services['adaptive_ai'] = get_adaptive_ai()
            logger.info("Adaptive AI system connected")
        except ImportError:
            logger.warning("Adaptive AI system not available")
        
        try:
            # Unified AI Service  
            from utils.unified_ai_service import get_unified_ai_service
            self.services['unified_ai'] = get_unified_ai_service()
            logger.info("Unified AI service connected")
        except ImportError:
            logger.warning("Unified AI service not available")
        
        try:
            # Plugin Registry
            from utils.plugin_registry import get_plugin_registry
            self.services['plugin_registry'] = get_plugin_registry()
            logger.info("Plugin registry connected")
        except ImportError:
            logger.warning("Plugin registry not available")
        
        try:
            # Intelligence Services
            from services.predictive_analytics import PredictiveAnalyticsEngine
            from services.enhanced_voice import EnhancedVoiceInterface
            from services.intelligent_automation import IntelligentAutomationEngine
            from services.visual_intelligence import VisualIntelligenceEngine
            from services.context_aware_ai import ContextAwareAIAssistant
            
            self.services.update({
                'predictive_analytics': PredictiveAnalyticsEngine(),
                'enhanced_voice': EnhancedVoiceInterface(),
                'intelligent_automation': IntelligentAutomationEngine(),
                'visual_intelligence': VisualIntelligenceEngine(),
                'context_aware_ai': ContextAwareAIAssistant()
            })
            logger.info("Intelligence services connected")
        except ImportError as e:
            logger.warning(f"Some intelligence services not available: {e}")
        
        logger.info(f"MTM-CE Integration Hub initialized with {len(self.services)} services")
    
    def process_unified_request(self, user_id: str, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process request through all integrated MTM-CE systems for optimal response"""
        if context is None:
            context = {}
        
        integration_context = IntegrationContext(
            user_id=user_id,
            session_id=context.get('session_id', 'default'),
            services_active=list(self.services.keys())
        )
        
        # Phase 1: Predictive Analysis
        predictions = self._get_predictive_insights(user_id, request, context)
        
        # Phase 2: Context Enhancement
        enhanced_context = self._enhance_context_with_intelligence(context, predictions)
        
        # Phase 3: Adaptive AI Processing
        adaptive_result = self._process_with_adaptive_ai(user_id, request, enhanced_context)
        
        # Phase 4: Cross-Service Integration
        integrated_response = self._integrate_all_services(user_id, request, enhanced_context, adaptive_result)
        
        # Phase 5: Learning and Optimization
        self._update_learning_pipeline(user_id, request, integrated_response, integration_context)
        
        return integrated_response
    
    def _get_predictive_insights(self, user_id: str, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get predictive insights to inform other services"""
        try:
            if 'predictive_analytics' in self.services:
                return self.services['predictive_analytics'].analyze_user_patterns(user_id, {
                    'current_request': request,
                    'context': context,
                    'timestamp': datetime.now().isoformat()
                })
            return {}
        except Exception as e:
            logger.error(f"Error getting predictive insights: {e}")
            return {}
    
    def _enhance_context_with_intelligence(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context using intelligence services"""
        enhanced_context = context.copy()
        
        try:
            # Add predictive insights
            enhanced_context['predictions'] = predictions
            
            # Add emotional context if voice service available
            if 'enhanced_voice' in self.services:
                emotional_context = self.services['enhanced_voice'].analyze_text_emotion(
                    context.get('message', '')
                )
                enhanced_context['emotional_state'] = emotional_context
            
            # Add automation opportunities
            if 'intelligent_automation' in self.services:
                automation_suggestions = self.services['intelligent_automation'].suggest_automations(
                    enhanced_context
                )
                enhanced_context['automation_opportunities'] = automation_suggestions
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Error enhancing context: {e}")
            return context
    
    def _process_with_adaptive_ai(self, user_id: str, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process through adaptive AI system"""
        try:
            if 'adaptive_ai' in self.services:
                return self.services['adaptive_ai'].process_user_request(user_id, request, context)
            return {'result': {'message': 'Adaptive AI not available'}, 'reward': 0.5}
        except Exception as e:
            logger.error(f"Error processing with adaptive AI: {e}")
            return {'result': {'message': 'Error in adaptive processing'}, 'reward': 0.0}
    
    def _integrate_all_services(self, user_id: str, request: str, context: Dict[str, Any], 
                              adaptive_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate responses from all available services"""
        integrated_response = {
            'primary_response': adaptive_result.get('result', {}),
            'enhanced_features': {},
            'intelligence_insights': {},
            'performance_metrics': {},
            'mtmce_integration': {
                'services_used': [],
                'integration_score': 0.0,
                'enhancement_level': 'full'
            }
        }
        
        try:
            # Integrate visual intelligence if available
            if 'visual_intelligence' in self.services:
                visual_insights = self._get_visual_insights(context)
                if visual_insights:
                    integrated_response['intelligence_insights']['visual'] = visual_insights
                    integrated_response['mtmce_integration']['services_used'].append('visual_intelligence')
            
            # Integrate context-aware AI
            if 'context_aware_ai' in self.services:
                context_insights = self.services['context_aware_ai'].get_contextual_response(
                    user_id, request, context
                )
                integrated_response['intelligence_insights']['contextual'] = context_insights
                integrated_response['mtmce_integration']['services_used'].append('context_aware_ai')
            
            # Integrate unified AI service for enhanced response
            if 'unified_ai' in self.services:
                messages = [{'role': 'user', 'content': request}]
                ai_response = self.services['unified_ai'].chat_completion(
                    messages=messages,
                    user_id=user_id,
                    context=context
                )
                integrated_response['enhanced_features']['ai_response'] = ai_response
                integrated_response['mtmce_integration']['services_used'].append('unified_ai')
            
            # Calculate integration score
            services_used = len(integrated_response['mtmce_integration']['services_used'])
            total_services = len(self.services)
            integrated_response['mtmce_integration']['integration_score'] = services_used / total_services if total_services > 0 else 0
            
            return integrated_response
            
        except Exception as e:
            logger.error(f"Error integrating services: {e}")
            return integrated_response
    
    def _get_visual_insights(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get visual intelligence insights if applicable"""
        try:
            # Check if context contains visual data
            if any(key in context for key in ['image', 'document', 'visual_data']):
                return self.services['visual_intelligence'].process_visual_content(context)
            return None
        except Exception as e:
            logger.error(f"Error getting visual insights: {e}")
            return None
    
    def _update_learning_pipeline(self, user_id: str, request: str, response: Dict[str, Any], 
                                 integration_context: IntegrationContext):
        """Update the learning pipeline with interaction data"""
        try:
            learning_data = {
                'user_id': user_id,
                'request': request,
                'response_quality': self._calculate_response_quality(response),
                'services_used': response.get('mtmce_integration', {}).get('services_used', []),
                'integration_score': response.get('mtmce_integration', {}).get('integration_score', 0),
                'timestamp': datetime.now().isoformat(),
                'context': integration_context
            }
            
            # Store learning data for future optimization
            if user_id not in self.performance_tracker:
                self.performance_tracker[user_id] = []
            
            self.performance_tracker[user_id].append(learning_data)
            
            # Keep only recent data (last 100 interactions)
            if len(self.performance_tracker[user_id]) > 100:
                self.performance_tracker[user_id] = self.performance_tracker[user_id][-100:]
            
            logger.info(f"Updated learning pipeline for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating learning pipeline: {e}")
    
    def _calculate_response_quality(self, response: Dict[str, Any]) -> float:
        """Calculate overall response quality score"""
        try:
            quality_factors = []
            
            # Primary response quality
            primary_response = response.get('primary_response', {})
            if primary_response.get('message'):
                quality_factors.append(0.4)  # Has primary response
            
            # Intelligence insights quality
            intelligence_insights = response.get('intelligence_insights', {})
            quality_factors.append(len(intelligence_insights) * 0.1)  # 0.1 per insight type
            
            # Integration score
            integration_score = response.get('mtmce_integration', {}).get('integration_score', 0)
            quality_factors.append(integration_score * 0.3)  # Weight integration heavily
            
            # Enhanced features
            enhanced_features = response.get('enhanced_features', {})
            quality_factors.append(len(enhanced_features) * 0.05)  # 0.05 per feature
            
            return min(1.0, sum(quality_factors))
            
        except Exception as e:
            logger.error(f"Error calculating response quality: {e}")
            return 0.5
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all MTM-CE integrations"""
        return {
            'services_available': list(self.services.keys()),
            'total_services': len(self.services),
            'integration_health': len(self.services) / 8,  # 8 expected services
            'performance_tracker_users': len(self.performance_tracker),
            'learning_pipeline_active': self.learning_pipeline is not None,
            'mtmce_features': {
                'adaptive_ai_learning': 'adaptive_ai' in self.services,
                'unified_ai_service': 'unified_ai' in self.services,
                'plugin_registry': 'plugin_registry' in self.services,
                'predictive_analytics': 'predictive_analytics' in self.services,
                'enhanced_voice': 'enhanced_voice' in self.services,
                'intelligent_automation': 'intelligent_automation' in self.services,
                'visual_intelligence': 'visual_intelligence' in self.services,
                'context_aware_ai': 'context_aware_ai' in self.services
            }
        }
    
    def optimize_performance(self, user_id: str = None) -> Dict[str, Any]:
        """Optimize performance based on learning data"""
        try:
            optimization_results = {
                'optimizations_applied': [],
                'performance_improvements': {},
                'recommendations': []
            }
            
            # Analyze user-specific data if provided
            if user_id and user_id in self.performance_tracker:
                user_data = self.performance_tracker[user_id]
                
                # Calculate average response quality
                avg_quality = sum(d['response_quality'] for d in user_data) / len(user_data)
                optimization_results['performance_improvements']['avg_response_quality'] = avg_quality
                
                # Identify most effective service combinations
                service_combinations = {}
                for data in user_data:
                    services = tuple(sorted(data['services_used']))
                    if services not in service_combinations:
                        service_combinations[services] = []
                    service_combinations[services].append(data['response_quality'])
                
                # Find best combination
                best_combination = max(service_combinations.items(), 
                                     key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)
                optimization_results['recommendations'].append(
                    f"Optimal service combination: {best_combination[0]}"
                )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing performance: {e}")
            return {'error': str(e)}

# Global integration hub instance
integration_hub = None

def get_mtmce_integration_hub() -> MTMCEIntegrationHub:
    """Get or create the global MTM-CE integration hub"""
    global integration_hub
    if integration_hub is None:
        integration_hub = MTMCEIntegrationHub()
    return integration_hub

def process_unified_request(user_id: str, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process request through unified MTM-CE system"""
    return get_mtmce_integration_hub().process_unified_request(user_id, request, context)

def get_integration_status() -> Dict[str, Any]:
    """Get MTM-CE integration status"""
    return get_mtmce_integration_hub().get_integration_status()