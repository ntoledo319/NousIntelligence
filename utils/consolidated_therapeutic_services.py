"""
Consolidated Therapeutic Services Helper
Combines DBT, CBT, and AA therapeutic functionality
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConsolidatedTherapeuticServices:
    """Unified therapeutic services interface combining DBT, CBT, and AA functionality"""
    
    def __init__(self):
        self.services = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all therapeutic services with fallback handling"""
        try:
            self.services['dbt'] = self._init_dbt_service()
            self.services['cbt'] = self._init_cbt_service()
            self.services['aa'] = self._init_aa_service()
            self.services['crisis'] = self._init_crisis_service()
        except Exception as e:
            logger.warning(f"Therapeutic services initialization warning: {e}")
    
    # DBT (Dialectical Behavior Therapy) functionality
    def _init_dbt_service(self):
        """Initialize DBT service"""
        try:
            from utils.dbt_helper import DBTHelper
            return DBTHelper()
        except ImportError:
            logger.warning("DBT helper not available, using fallback")
            return self._create_fallback_service('dbt')
    
    def get_dbt_skill(self, emotional_state: str, situation: str = None) -> Dict[str, Any]:
        """Get appropriate DBT skill recommendation"""
        if 'dbt' in self.services:
            try:
                return self.services['dbt'].get_skill_recommendation(emotional_state, situation)
            except Exception as e:
                logger.error(f"DBT skill recommendation failed: {e}")
        
        # Fallback DBT skills
        dbt_skills = {
            'anxiety': 'TIPP (Temperature, Intense exercise, Paced breathing, Paired muscle relaxation)',
            'anger': 'PLEASE (treat PhysicaL illness, balance Eating, avoid mood-Altering substances, balance Sleep, get Exercise)',
            'sadness': 'Opposite Action - Act opposite to the emotion\'s urge',
            'overwhelmed': 'STOP (Stop, Take a breath, Observe, Proceed mindfully)',
            'default': 'Mindfulness - Observe, describe, participate without judgment'
        }
        
        skill = dbt_skills.get(emotional_state.lower(), dbt_skills['default'])
        return {
            'success': True,
            'skill': skill,
            'emotional_state': emotional_state,
            'fallback': True
        }
    
    def practice_distress_tolerance(self, intensity: int = 5) -> Dict[str, Any]:
        """Provide distress tolerance techniques"""
        if 'dbt' in self.services:
            try:
                return self.services['dbt'].distress_tolerance_technique(intensity)
            except Exception as e:
                logger.error(f"DBT distress tolerance failed: {e}")
        
        techniques = {
            'low': ['Deep breathing', 'Count to 10', 'Cold water on face'],
            'medium': ['TIPP technique', 'Progressive muscle relaxation', 'Distraction activities'],
            'high': ['Ice cubes on skin', 'Intense exercise', 'Strong scents/tastes']
        }
        
        level = 'high' if intensity >= 8 else 'medium' if intensity >= 5 else 'low'
        return {
            'success': True,
            'techniques': techniques[level],
            'intensity_level': level,
            'fallback': True
        }
    
    def emotion_regulation_skill(self, emotion: str, intensity: int = 5) -> Dict[str, Any]:
        """Provide emotion regulation techniques"""
        if 'dbt' in self.services:
            try:
                return self.services['dbt'].emotion_regulation(emotion, intensity)
            except Exception as e:
                logger.error(f"DBT emotion regulation failed: {e}")
        
        return {
            'success': True,
            'skill': f'Check the Facts - Is your emotion fitting the facts? {emotion} at intensity {intensity}',
            'description': 'Examine whether your emotional response matches the situation',
            'fallback': True
        }
    
    # CBT (Cognitive Behavioral Therapy) functionality
    def _init_cbt_service(self):
        """Initialize CBT service"""
        try:
            from utils.cbt_helper import CBTHelper
            return CBTHelper()
        except ImportError:
            logger.warning("CBT helper not available, using fallback")
            return self._create_fallback_service('cbt')
    
    def identify_cognitive_distortion(self, thought: str) -> Dict[str, Any]:
        """Identify cognitive distortions in thoughts"""
        if 'cbt' in self.services:
            try:
                return self.services['cbt'].identify_distortion(thought)
            except Exception as e:
                logger.error(f"CBT distortion identification failed: {e}")
        
        # Basic fallback distortion detection
        distortions = []
        thought_lower = thought.lower()
        
        if any(word in thought_lower for word in ['always', 'never', 'everyone', 'no one']):
            distortions.append('All-or-Nothing Thinking')
        if 'should' in thought_lower:
            distortions.append('Should Statements')
        if any(word in thought_lower for word in ['terrible', 'awful', 'disaster']):
            distortions.append('Catastrophizing')
        
        return {
            'success': True,
            'thought': thought,
            'distortions': distortions if distortions else ['No obvious distortions detected'],
            'fallback': True
        }
    
    def challenge_thought(self, thought: str, evidence_for: List[str] = None, evidence_against: List[str] = None) -> Dict[str, Any]:
        """Help challenge negative thoughts using CBT techniques"""
        if 'cbt' in self.services:
            try:
                return self.services['cbt'].thought_challenging(thought, evidence_for, evidence_against)
            except Exception as e:
                logger.error(f"CBT thought challenging failed: {e}")
        
        questions = [
            "What evidence supports this thought?",
            "What evidence contradicts this thought?",
            "What would you tell a friend having this thought?",
            "Is there a more balanced way to think about this?",
            "What's the worst that could realistically happen?",
            "How likely is that to actually occur?"
        ]
        
        return {
            'success': True,
            'original_thought': thought,
            'challenging_questions': questions,
            'fallback': True
        }
    
    def behavioral_activation(self, mood_level: int, available_time: int = 30) -> Dict[str, Any]:
        """Suggest behavioral activation activities"""
        if 'cbt' in self.services:
            try:
                return self.services['cbt'].behavioral_activation(mood_level, available_time)
            except Exception as e:
                logger.error(f"CBT behavioral activation failed: {e}")
        
        activities = {
            'quick': ['Take a 5-minute walk', 'Call a friend', 'Listen to upbeat music'],
            'medium': ['Go for a walk outside', 'Do a hobby you enjoy', 'Exercise for 20 minutes'],
            'long': ['Meet with a friend', 'Take a nature hike', 'Work on a meaningful project']
        }
        
        time_category = 'long' if available_time >= 60 else 'medium' if available_time >= 20 else 'quick'
        return {
            'success': True,
            'mood_level': mood_level,
            'activities': activities[time_category],
            'time_available': available_time,
            'fallback': True
        }
    
    # AA (Alcoholics Anonymous) functionality
    def _init_aa_service(self):
        """Initialize AA service"""
        try:
            from utils.aa_helper import AAHelper
            return AAHelper()
        except ImportError:
            logger.warning("AA helper not available, using fallback")
            return self._create_fallback_service('aa')
    
    def get_aa_content(self, step_number: int = None, topic: str = None) -> Dict[str, Any]:
        """Get AA content for specific step or topic"""
        if 'aa' in self.services:
            try:
                return self.services['aa'].get_content(step_number, topic)
            except Exception as e:
                logger.error(f"AA content retrieval failed: {e}")
        
        # Fallback AA steps
        aa_steps = {
            1: "We admitted we were powerless over alcohol—that our lives had become unmanageable.",
            2: "Came to believe that a Power greater than ourselves could restore us to sanity.",
            3: "Made a decision to turn our will and our lives over to the care of God as we understood Him.",
            4: "Made a searching and fearless moral inventory of ourselves.",
            5: "Admitted to God, to ourselves, and to another human being the exact nature of our wrongs."
        }
        
        if step_number and step_number in aa_steps:
            return {
                'success': True,
                'step': step_number,
                'content': aa_steps[step_number],
                'fallback': True
            }
        
        return {
            'success': True,
            'message': 'AA content available for steps 1-12',
            'fallback': True
        }
    
    def daily_reflection(self, date: str = None) -> Dict[str, Any]:
        """Get daily AA reflection"""
        if 'aa' in self.services:
            try:
                return self.services['aa'].daily_reflection(date)
            except Exception as e:
                logger.error(f"AA daily reflection failed: {e}")
        
        today = date or datetime.now().strftime("%Y-%m-%d")
        return {
            'success': True,
            'date': today,
            'reflection': 'Today I will focus on living one day at a time and finding strength in my recovery journey.',
            'fallback': True
        }
    
    # Crisis intervention functionality
    def _init_crisis_service(self):
        """Initialize crisis intervention service"""
        try:
            from utils.dbt_crisis_helper import DBTCrisisHelper
            return DBTCrisisHelper()
        except ImportError:
            logger.warning("Crisis helper not available, using fallback")
            return self._create_fallback_service('crisis')
    
    def crisis_intervention(self, crisis_level: int, situation: str = None) -> Dict[str, Any]:
        """Provide crisis intervention support"""
        if 'crisis' in self.services:
            try:
                return self.services['crisis'].crisis_support(crisis_level, situation)
            except Exception as e:
                logger.error(f"Crisis intervention failed: {e}")
        
        if crisis_level >= 8:
            return {
                'success': True,
                'urgency': 'high',
                'recommendations': [
                    'Contact emergency services (911) if in immediate danger',
                    'Call National Suicide Prevention Lifeline: 988',
                    'Go to nearest emergency room',
                    'Contact your therapist or crisis counselor immediately'
                ],
                'crisis_level': crisis_level
            }
        elif crisis_level >= 5:
            return {
                'success': True,
                'urgency': 'medium',
                'recommendations': [
                    'Use distress tolerance skills (TIPP technique)',
                    'Contact a trusted friend or family member',
                    'Consider calling a crisis helpline',
                    'Practice grounding techniques'
                ],
                'crisis_level': crisis_level
            }
        else:
            return {
                'success': True,
                'urgency': 'low',
                'recommendations': [
                    'Practice mindfulness exercises',
                    'Use emotion regulation skills',
                    'Engage in self-care activities',
                    'Journal about your feelings'
                ],
                'crisis_level': crisis_level
            }
    
    def _create_fallback_service(self, service_name: str):
        """Create a fallback service object"""
        class FallbackService:
            def __init__(self, name):
                self.name = name
            
            def __getattr__(self, method_name):
                def fallback_method(*args, **kwargs):
                    return {
                        'success': False,
                        'error': f'{self.name.upper()} service not available',
                        'fallback': True
                    }
                return fallback_method
        
        return FallbackService(service_name)
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all therapeutic services"""
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

# Global instance
_therapeutic_services = None

def get_therapeutic_services() -> ConsolidatedTherapeuticServices:
    """Get the global therapeutic services instance"""
    global _therapeutic_services
    if _therapeutic_services is None:
        _therapeutic_services = ConsolidatedTherapeuticServices()
    return _therapeutic_services

# Backward compatibility functions
def get_dbt_skill(emotional_state: str, situation: str = None) -> Dict[str, Any]:
    """Backward compatibility for DBT skills"""
    return get_therapeutic_services().get_dbt_skill(emotional_state, situation)

def identify_cognitive_distortion(thought: str) -> Dict[str, Any]:
    """Backward compatibility for CBT distortion identification"""
    return get_therapeutic_services().identify_cognitive_distortion(thought)

def get_aa_content(step_number: int = None, topic: str = None) -> Dict[str, Any]:
    """Backward compatibility for AA content"""
    return get_therapeutic_services().get_aa_content(step_number, topic)

def crisis_intervention(crisis_level: int, situation: str = None) -> Dict[str, Any]:
    """Backward compatibility for crisis intervention"""
    return get_therapeutic_services().crisis_intervention(crisis_level, situation)