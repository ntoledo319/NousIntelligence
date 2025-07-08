"""
Mental Health Chat Handler

Enhanced chat integration for mental health resources with sophisticated
crisis detection and natural language understanding.

@module utils.mental_health_chat_handler
@ai_prompt Use this for all mental health related chat interactions
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from services.mental_health_resources_service import MentalHealthResourcesService

logger = logging.getLogger(__name__)


class MentalHealthChatHandler:
    """
    Handles mental health related chat interactions with enhanced crisis detection
    and conversational resource discovery.
    """
    
    def __init__(self):
        self.resources_service = MentalHealthResourcesService()
        
        # Enhanced crisis patterns with severity levels
        self.crisis_patterns = {
            'immediate': {
                'patterns': [
                    r'\b(kill\s+myself|suicide|suicidal|end\s+my\s+life|not\s+worth\s+living)\b',
                    r'\b(overdose|OD|pills\s+to\s+die|jump\s+off|hang\s+myself)\b',
                    r'\b(goodbye\s+forever|final\s+goodbye|last\s+message|won\'t\s+be\s+here)\b',
                    r'\b(cutting\s+myself|self\s+harm|hurt\s+myself\s+badly)\b'
                ],
                'severity': 10,
                'response_type': 'immediate_crisis'
            },
            'high': {
                'patterns': [
                    r'\b(want\s+to\s+die|wish\s+I\s+was\s+dead|better\s+off\s+dead)\b',
                    r'\b(can\'t\s+go\s+on|can\'t\s+take\s+it|give\s+up|no\s+hope)\b',
                    r'\b(worthless|hopeless|no\s+point|why\s+bother)\b',
                    r'\b(nobody\s+cares|alone\s+forever|no\s+one\s+would\s+miss)\b'
                ],
                'severity': 8,
                'response_type': 'high_concern'
            },
            'moderate': {
                'patterns': [
                    r'\b(depressed|depression|anxiety|panic\s+attack)\b',
                    r'\b(struggling|overwhelmed|can\'t\s+cope|falling\s+apart)\b',
                    r'\b(need\s+help|talk\s+to\s+someone|therapist|counselor)\b',
                    r'\b(mental\s+health|emotional\s+support|crisis)\b'
                ],
                'severity': 5,
                'response_type': 'support_needed'
            }
        }
        
        # False positive patterns to exclude
        self.false_positive_patterns = [
            r'\b(killing\s+it|killed\s+it|crushing\s+it)\b',  # Positive expressions
            r'\b(dying\s+of\s+laughter|dying\s+to\s+know)\b',  # Figures of speech
            r'\b(game|movie|book|story|character)\b',  # Fiction context
            r'\b(homework|assignment|project|deadline)\b'  # Academic stress
        ]
        
        # Resource request patterns
        self.resource_patterns = {
            'therapy': [
                r'\b(therapist|counselor|therapy|counseling|psychologist)\b',
                r'\b(someone\s+to\s+talk|professional\s+help|mental\s+health\s+professional)\b',
                r'\b(find\s+help|get\s+help|need\s+support)\b'
            ],
            'psychiatry': [
                r'\b(psychiatrist|medication|meds|prescribe|prescription)\b',
                r'\b(mental\s+health\s+medication|antidepressant|anti-anxiety)\b'
            ],
            'affordable': [
                r'\b(can\'t\s+afford|no\s+money|free|low\s+cost|sliding\s+scale)\b',
                r'\b(insurance|medicaid|medicare|uninsured)\b',
                r'\b(cheap|affordable|budget)\b'
            ],
            'crisis': [
                r'\b(crisis\s+line|hotline|emergency\s+number|help\s+line)\b',
                r'\b(someone\s+now|right\s+now|immediately|urgent)\b'
            ]
        }
    
    def process_message(self, user_id: str, message: str, 
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a chat message for mental health concerns and resource requests
        
        Returns comprehensive response with resources and support
        """
        message_lower = message.lower()
        context = context or {}
        
        # Step 1: Check for crisis situations
        crisis_level, crisis_type = self._detect_crisis_level(message_lower)
        
        if crisis_level >= 8:  # High or immediate crisis
            return self._handle_crisis_response(user_id, crisis_level, crisis_type, context)
        
        # Step 2: Check for resource requests
        resource_request = self._detect_resource_request(message_lower)
        
        if resource_request:
            return self._handle_resource_request(user_id, resource_request, context)
        
        # Step 3: Check for general mental health discussion
        if crisis_level >= 5:  # Moderate concern
            return self._handle_support_response(user_id, message, context)
        
        # Step 4: Check for follow-up on previous mental health discussions
        if self._is_mental_health_followup(user_id, context):
            return self._handle_followup_response(user_id, message, context)
        
        return None  # No mental health content detected
    
    def _detect_crisis_level(self, message: str) -> Tuple[int, str]:
        """
        Detect crisis level with false positive filtering
        
        Returns: (severity_level, crisis_type)
        """
        # Check for false positives first
        for pattern in self.false_positive_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return 0, 'none'
        
        # Check crisis patterns by severity
        for crisis_type, config in self.crisis_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, message, re.IGNORECASE):
                    return config['severity'], crisis_type
        
        return 0, 'none'
    
    def _detect_resource_request(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect what type of mental health resource the user is requesting"""
        request = {
            'types': [],
            'constraints': []
        }
        
        # Check resource type patterns
        for resource_type, patterns in self.resource_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    if resource_type in ['therapy', 'psychiatry', 'crisis']:
                        request['types'].append(resource_type)
                    elif resource_type == 'affordable':
                        request['constraints'].append('affordable')
                    break
        
        # Check for location mentions
        location_pattern = r'\b(near\s+me|in\s+[\w\s]+|around\s+[\w\s]+|local|my\s+area)\b'
        if re.search(location_pattern, message, re.IGNORECASE):
            request['constraints'].append('location_based')
        
        # Check for urgency
        urgency_pattern = r'\b(now|today|immediately|urgent|asap|right\s+away)\b'
        if re.search(urgency_pattern, message, re.IGNORECASE):
            request['constraints'].append('urgent')
        
        return request if request['types'] or request['constraints'] else None
    
    def _handle_crisis_response(self, user_id: str, severity: int, 
                               crisis_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle crisis situations with immediate support
        
        NON-NEGOTIABLES: Always provide multiple resources, validate feelings
        """
        # Get crisis resources immediately
        country = context.get('location', {}).get('country_code', 'US')
        resources = self.resources_service.get_crisis_resources(country)[:5]
        
        # Build crisis response
        response = {
            'type': 'crisis_support',
            'severity': severity,
            'requires_immediate_display': True,
            'response_parts': []
        }
        
        # Part 1: Immediate acknowledgment and validation
        if crisis_type == 'immediate_crisis':
            response['response_parts'].append({
                'type': 'validation',
                'content': "I hear you, and I'm deeply concerned about what you're going through. Your life has value, and there are people who want to help you right now.",
                'emphasis': 'high'
            })
        else:
            response['response_parts'].append({
                'type': 'validation',
                'content': "I can hear that you're going through a really difficult time. Thank you for reaching out - that takes courage.",
                'emphasis': 'medium'
            })
        
        # Part 2: Crisis resources
        response['response_parts'].append({
            'type': 'crisis_resources',
            'content': "Here are crisis support services available 24/7:",
            'resources': [self._format_crisis_resource(r) for r in resources],
            'display_format': 'prominent'
        })
        
        # Part 3: Safety check
        response['response_parts'].append({
            'type': 'safety_check',
            'content': "Are you safe right now? If you're in immediate danger, please call 911 or your local emergency number.",
            'show_emergency': True
        })
        
        # Part 4: Coping support
        response['response_parts'].append({
            'type': 'coping_support',
            'content': "While you decide what to do, here are some things that might help right now:",
            'techniques': [
                "Take slow, deep breaths - in for 4, hold for 4, out for 4",
                "If you can, reach out to someone you trust",
                "Focus on just the next hour - you don't have to figure everything out right now",
                "Remember: Feelings, even the most painful ones, do pass"
            ]
        })
        
        # Part 5: Continued support offer
        response['response_parts'].append({
            'type': 'continued_support',
            'content': "I'm here to keep talking if you need me. You don't have to go through this alone.",
            'options': [
                "Tell me more about what you're feeling",
                "Help me find a therapist",
                "Just chat about something else for distraction"
            ]
        })
        
        # Log crisis interaction for follow-up
        self._log_crisis_interaction(user_id, severity, crisis_type)
        
        return response
    
    def _handle_resource_request(self, user_id: str, request: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for mental health resources"""
        response = {
            'type': 'resource_discovery',
            'response_parts': []
        }
        
        # Determine what resources to show
        show_crisis = 'crisis' in request['types'] or 'urgent' in request['constraints']
        show_therapy = 'therapy' in request['types'] or not request['types']
        show_psychiatry = 'psychiatry' in request['types']
        needs_location = 'location_based' in request['constraints']
        affordable_only = 'affordable' in request['constraints']
        
        # Part 1: Acknowledgment
        response['response_parts'].append({
            'type': 'acknowledgment',
            'content': "I'll help you find the mental health support you need. Let me show you some options."
        })
        
        # Part 2: Crisis resources if needed
        if show_crisis:
            country = context.get('location', {}).get('country_code', 'US')
            crisis_resources = self.resources_service.get_crisis_resources(country)[:3]
            
            response['response_parts'].append({
                'type': 'crisis_resources',
                'content': "For immediate support, these services are available 24/7:",
                'resources': [self._format_crisis_resource(r) for r in crisis_resources]
            })
        
        # Part 3: Location check if needed
        if needs_location and not context.get('location'):
            response['response_parts'].append({
                'type': 'location_request',
                'content': "To find providers near you, I'll need your location. You can share:",
                'options': [
                    "Your city and state (e.g., 'Austin, TX')",
                    "Your zip code",
                    "Or say 'online only' for telehealth options"
                ]
            })
            response['needs_location'] = True
            return response
        
        # Part 4: Therapy options
        if show_therapy:
            therapy_content = self._build_therapy_recommendations(
                context.get('location', {}),
                affordable_only
            )
            response['response_parts'].append(therapy_content)
        
        # Part 5: Psychiatry options
        if show_psychiatry:
            psychiatry_content = self._build_psychiatry_recommendations(
                context.get('location', {}),
                affordable_only
            )
            response['response_parts'].append(psychiatry_content)
        
        # Part 6: Next steps
        response['response_parts'].append({
            'type': 'next_steps',
            'content': "Would you like me to:",
            'options': [
                "Search for specific providers in your area",
                "Explain the difference between therapy and psychiatry",
                "Find support groups or community resources",
                "Save these resources for later"
            ]
        })
        
        return response
    
    def _handle_support_response(self, user_id: str, message: str, 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle moderate mental health concerns"""
        response = {
            'type': 'support_response',
            'response_parts': []
        }
        
        # Acknowledge their feelings
        response['response_parts'].append({
            'type': 'validation',
            'content': "Thank you for sharing what you're going through. It's important to talk about these feelings."
        })
        
        # Offer support options
        response['response_parts'].append({
            'type': 'support_menu',
            'content': "I can help you in several ways:",
            'options': [
                {
                    'label': "🆘 Get crisis support numbers",
                    'action': 'show_crisis_resources'
                },
                {
                    'label': "🏥 Find a therapist or counselor",
                    'action': 'search_therapy'
                },
                {
                    'label': "💊 Find a psychiatrist",
                    'action': 'search_psychiatry'
                },
                {
                    'label': "🤝 Find free/low-cost resources",
                    'action': 'affordable_resources'
                },
                {
                    'label': "🧘 Learn coping techniques",
                    'action': 'coping_techniques'
                },
                {
                    'label': "💬 Just talk about what's on your mind",
                    'action': 'supportive_chat'
                }
            ]
        })
        
        # Add gentle crisis resources
        country = context.get('location', {}).get('country_code', 'US')
        crisis_resources = self.resources_service.get_crisis_resources(country)[:2]
        
        response['response_parts'].append({
            'type': 'gentle_resources',
            'content': "If you need someone to talk to right away:",
            'resources': [self._format_crisis_resource(r) for r in crisis_resources],
            'display_format': 'subtle'
        })
        
        return response
    
    def _handle_followup_response(self, user_id: str, message: str, 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle follow-up to previous mental health discussions"""
        # Check if this is a check-in response
        last_crisis = self._get_last_crisis_interaction(user_id)
        
        if last_crisis and (datetime.now() - last_crisis['timestamp']).days <= 7:
            return {
                'type': 'followup_checkin',
                'response_parts': [
                    {
                        'type': 'checkin',
                        'content': "I'm glad to hear from you again. How have you been feeling since we last talked?"
                    },
                    {
                        'type': 'support_reminder',
                        'content': "Remember, support is always available if you need it.",
                        'show_saved_resources': True
                    }
                ]
            }
        
        return None
    
    def _format_crisis_resource(self, resource: Any) -> Dict[str, Any]:
        """Format crisis resource for display"""
        if isinstance(resource, dict):
            return {
                'name': resource.get('name', 'Crisis Support'),
                'phone': resource.get('phone_number'),
                'text': resource.get('text_number'),
                'description': resource.get('description', ''),
                'available': '24/7' if resource.get('is_24_7', True) else 'Limited hours',
                'action_buttons': self._build_action_buttons(resource)
            }
        else:
            # Handle CrisisResource model
            return {
                'name': resource.name,
                'phone': resource.phone_number,
                'text': resource.text_number,
                'description': resource.description,
                'available': '24/7' if resource.is_24_7 else 'Limited hours',
                'action_buttons': self._build_action_buttons(resource)
            }
    
    def _build_action_buttons(self, resource: Any) -> List[Dict[str, str]]:
        """Build action buttons for a resource"""
        buttons = []
        
        phone = getattr(resource, 'phone_number', None) or resource.get('phone_number')
        if phone:
            buttons.append({
                'type': 'call',
                'label': f'Call {phone}',
                'action': f'tel:{phone}',
                'style': 'primary'
            })
        
        text = getattr(resource, 'text_number', None) or resource.get('text_number')
        if text:
            buttons.append({
                'type': 'text',
                'label': f'Text {text}',
                'action': f'sms:{text}',
                'style': 'primary'
            })
        
        return buttons
    
    def _build_therapy_recommendations(self, location: Dict[str, Any], 
                                     affordable_only: bool) -> Dict[str, Any]:
        """Build therapy provider recommendations"""
        content = {
            'type': 'therapy_options',
            'content': "For ongoing therapy support:"
        }
        
        if affordable_only:
            content['filters'] = ['Sliding scale fees', 'Accepts insurance', 'Low-cost options']
            content['message'] = "I'll focus on affordable therapy options for you."
        
        if location.get('city') and location.get('state'):
            # Get actual providers
            providers = self.resources_service.get_affordable_therapy_options(
                location['city'], 
                location['state']
            )
            
            if providers:
                content['providers'] = [
                    {
                        'name': p.name,
                        'specialties': p.specializations[:3] if p.specializations else [],
                        'sliding_scale': p.has_sliding_scale,
                        'online': p.is_online,
                        'accepting': p.is_accepting_patients
                    }
                    for p in providers[:5]
                ]
            else:
                content['message'] = "I couldn't find specific providers in your area, but here are online options:"
                content['online_options'] = [
                    "BetterHelp - Online therapy with financial aid available",
                    "7 Cups - Free emotional support and affordable therapy",
                    "Open Path Collective - Therapy sessions $30-$80"
                ]
        else:
            content['general_options'] = [
                "Psychology Today - Search with filters for insurance and sliding scale",
                "SAMHSA Treatment Locator - Find local mental health services",
                "Community mental health centers - Often offer reduced fees"
            ]
        
        return content
    
    def _build_psychiatry_recommendations(self, location: Dict[str, Any], 
                                        affordable_only: bool) -> Dict[str, Any]:
        """Build psychiatry provider recommendations"""
        content = {
            'type': 'psychiatry_options',
            'content': "For medication management:"
        }
        
        if affordable_only:
            content['filters'] = ['Accepts Medicare/Medicaid', 'Sliding scale', 'Community clinics']
        
        content['options'] = [
            "Community mental health centers - Often have psychiatrists on staff",
            "Federally Qualified Health Centers (FQHCs) - Income-based fees",
            "Teaching hospitals - May offer reduced-cost services",
            "Telehealth platforms - Some offer affordable psychiatric care"
        ]
        
        if location.get('state'):
            content['state_resources'] = f"Search for '{location['state']} community mental health' for local options"
        
        return content
    
    def _is_mental_health_followup(self, user_id: str, context: Dict[str, Any]) -> bool:
        """Check if this is a follow-up to previous mental health discussion"""
        # Check conversation history in context
        history = context.get('conversation_history', [])
        
        for entry in history[-5:]:  # Check last 5 messages
            if any(keyword in entry.get('message', '').lower() 
                   for keyword in ['therapy', 'crisis', 'mental health', 'depression', 'anxiety']):
                return True
        
        return False
    
    def _log_crisis_interaction(self, user_id: str, severity: int, crisis_type: str):
        """Log crisis interaction for follow-up and safety"""
        try:
            # This would integrate with your logging/database system
            logger.warning(f"Crisis interaction logged - User: {user_id}, Severity: {severity}, Type: {crisis_type}")
            
            # In production, you might want to:
            # 1. Store in database for follow-up
            # 2. Alert support team if severity is high
            # 3. Schedule automated check-ins
            
        except Exception as e:
            logger.error(f"Failed to log crisis interaction: {e}")
    
    def _get_last_crisis_interaction(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the last crisis interaction for a user"""
        # This would query your database
        # For now, return None
        return None
    
    def format_chat_response(self, response_data: Dict[str, Any]) -> str:
        """
        Format the structured response into a chat message
        
        This converts our structured response into natural chat text
        """
        if not response_data or 'response_parts' not in response_data:
            return ""
        
        message_parts = []
        
        for part in response_data['response_parts']:
            part_type = part.get('type')
            
            if part_type == 'validation':
                message_parts.append(part['content'])
                
            elif part_type == 'crisis_resources':
                message_parts.append(part['content'])
                for resource in part.get('resources', []):
                    resource_text = f"\n🆘 **{resource['name']}**"
                    if resource.get('phone'):
                        resource_text += f"\n   📞 Call: {resource['phone']}"
                    if resource.get('text'):
                        resource_text += f"\n   💬 Text: {resource['text']}"
                    if resource.get('description'):
                        resource_text += f"\n   {resource['description']}"
                    message_parts.append(resource_text)
                    
            elif part_type == 'safety_check':
                message_parts.append(f"\n{part['content']}")
                
            elif part_type == 'coping_support':
                message_parts.append(f"\n{part['content']}")
                for technique in part.get('techniques', []):
                    message_parts.append(f"• {technique}")
                    
            elif part_type == 'continued_support':
                message_parts.append(f"\n{part['content']}")
                
            elif part_type == 'support_menu':
                message_parts.append(part['content'])
                for option in part.get('options', []):
                    message_parts.append(f"• {option['label']}")
                    
            elif part_type in ['acknowledgment', 'checkin', 'support_reminder']:
                message_parts.append(part['content'])
                
            elif part_type == 'therapy_options':
                message_parts.append(f"\n{part['content']}")
                if part.get('providers'):
                    for provider in part['providers'][:3]:
                        message_parts.append(f"• {provider['name']} - {'Sliding scale' if provider.get('sliding_scale') else 'Standard fees'}")
                elif part.get('online_options'):
                    for option in part['online_options']:
                        message_parts.append(f"• {option}")
                        
            elif part_type == 'next_steps':
                message_parts.append(f"\n{part['content']}")
                for option in part.get('options', []):
                    message_parts.append(f"• {option}")
        
        return "\n\n".join(message_parts)


# Singleton instance
_handler_instance = None

def get_mental_health_handler() -> MentalHealthChatHandler:
    """Get singleton instance of mental health chat handler"""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = MentalHealthChatHandler()
    return _handler_instance


# AI-GENERATED [2024-12-01]
# CRITICAL: Crisis detection must be accurate but avoid false positives
# NON-NEGOTIABLES: Always provide multiple crisis resources, never just one
