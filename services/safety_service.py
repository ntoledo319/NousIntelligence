"""
Safety Service

Implements the multi-layer crisis detection and response protocol.
Integrates with mental_health_resources models for location-aware referrals.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Level 1: Immediate Danger Regex Patterns
PATTERNS_LEVEL_1 = [
    r"\b(kill|hang|shoot|cut|hurt) myself\b",
    r"\b(suicide|suicidal)\b",
    r"\bwant to die\b",
    r"\bend it all\b",
    r"\btake my (own )?life\b",
    r"\boverdose\b",
    r"\bswallow pills\b",
    r"\bjump off\b"
]

# Level 1.5: Medical Emergency
PATTERNS_MEDICAL = [
    r"\bheart attack\b",
    r"\bstroke\b",
    r"\bbleeding out\b",
    r"\bcan't breathe\b",
    r"\bcall 911\b"
]

# Level 2: Abuse/Trauma
PATTERNS_LEVEL_2 = [
    r"\b(rape|raped|sexual assault)\b",
    r"\b(beat|hit) me\b",
    r"\bdomestic violence\b",
    r"\babuse\b",
    r"\bscared of him\b",
    r"\bscared of her\b"
]

class SafetyService:
    def __init__(self):
        self.l1_regex = [re.compile(p, re.IGNORECASE) for p in PATTERNS_LEVEL_1]
        self.medical_regex = [re.compile(p, re.IGNORECASE) for p in PATTERNS_MEDICAL]
        self.l2_regex = [re.compile(p, re.IGNORECASE) for p in PATTERNS_LEVEL_2]

    def analyze_risk_level(self, text: str) -> str:
        """
        Determines the risk level of the input text.
        Returns: 'imminent_harm', 'medical_emergency', 'abuse_trauma', or 'safe'
        """
        if not text:
            return 'safe'

        # Check Medical first
        for p in self.medical_regex:
            if p.search(text):
                return 'medical_emergency'

        # Check Suicide/Self-Harm
        for p in self.l1_regex:
            if p.search(text):
                return 'imminent_harm'

        # Check Abuse/Trauma
        for p in self.l2_regex:
            if p.search(text):
                return 'abuse_trauma'

        return 'safe'

    def get_safety_protocol(self, risk_type: str, user=None) -> Dict[str, Any]:
        """
        Returns the appropriate response protocol including scripts and resources.
        """
        response = {
            'is_crisis': True,
            'risk_type': risk_type,
            'message': "",
            'resources': []
        }

        if risk_type == 'medical_emergency':
            response['message'] = (
                "This sounds like a medical emergency. Please call 911 (or your local emergency number) immediately, "
                "or go to the nearest emergency room. I cannot provide medical help."
            )
            response['resources'] = [{'name': 'Emergency Services', 'phone': '911'}]

        elif risk_type == 'imminent_harm':
            response['message'] = (
                "I hear how much pain you're in, and I want you to be safe. "
                "You are not alone. Please reach out to a crisis counselor who can listen and help right now."
            )
            # Fetch resources
            response['resources'] = self._get_suicide_resources(user)

            # Add user's own safety plan if available
            if user and hasattr(user, 'crisis_plan') and user.crisis_plan:
                 response['safety_plan'] = user.crisis_plan.reasons_to_live

        elif risk_type == 'abuse_trauma':
            response['message'] = (
                "I am so sorry that happened to you. You did not deserve this. "
                "There are people who can support you through this. Would you like the number for a support hotline?"
            )
            response['resources'] = self._get_trauma_resources(user)

        return response

    def _get_suicide_resources(self, user) -> List[Dict]:
        """Fetches suicide prevention resources, prioritizing user location if known"""
        # Logic to query database would go here. For now, we assume US/General defaults
        # In production, we'd query CrisisResource based on user.country_code
        return [
            {
                'name': 'National Suicide Prevention Lifeline (US)',
                'phone': '988',
                'description': '24/7, free and confidential support'
            },
            {
                'name': 'Crisis Text Line',
                'text': 'HOME to 741741',
                'description': 'Free 24/7 support via text'
            }
        ]

    def _get_trauma_resources(self, user) -> List[Dict]:
        return [
            {
                'name': 'RAINN (National Sexual Assault Hotline)',
                'phone': '800-656-4673',
                'website': 'rainn.org'
            },
            {
                'name': 'National Domestic Violence Hotline',
                'phone': '800-799-7233',
                'website': 'thehotline.org'
            }
        ]
