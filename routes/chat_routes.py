"""
🌈 Chat Routes - Where Connection Begins
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every conversation is an opportunity for growth
Every message carries the potential for understanding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import logging
from datetime import datetime
from flask import Blueprint, render_template, session, g, jsonify, request

# 🧘‍♀️ Import our wellness framework
try:
    from utils.therapeutic_code_framework import (
        with_therapy_session, cognitive_reframe, stop_skill,
        generate_affirmation, log_with_self_compassion,
        TherapeuticContext, with_mindful_breathing,
        COMPASSION_PROMPTS
    )
except ImportError:
    # Graceful fallback
    def with_therapy_session(t): return lambda f: f
    def cognitive_reframe(n, b): return lambda f: f
    def stop_skill(d): return lambda f: f
    def with_mindful_breathing(c): return lambda f: f
    def generate_affirmation(c): return "You're doing great!"
    COMPASSION_PROMPTS = ["Keep going!"]

logger = logging.getLogger(__name__)

# 💝 Create chat blueprint with intention
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@with_therapy_session("chat interface")
@cognitive_reframe(
    negative_pattern="Just another chat interface",
    balanced_thought="A sacred space for connection and growth"
)
def chat_interface():
    """
    Main chat interface - A safe space for exploration and support
    Remember: NOUS is a wellness companion, not a therapist
    """
    try:
        # 🤗 Check in with our visitor
        with TherapeuticContext("session preparation"):
            # Ensure they have a warm welcome
            if 'user' not in session:
                session['user'] = {
                    'id': 'wellness_explorer_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
                    'name': 'Wellness Explorer',
                    'email': 'explorer@nous.app',
                    'demo_mode': True,
                    'journey_start': datetime.now().isoformat(),
                    'affirmation': generate_affirmation('general')
                }
                log_with_self_compassion('info', "New friend joining us for support")
            
            # Add wellness context
            g.chat_context = {
                'intention': 'supportive_companion',
                'boundaries': 'wellness_not_therapy',
                'daily_affirmation': generate_affirmation('general'),
                'wellness_tips': [
                    "Take breaks when you need them",
                    "Your pace is the right pace",
                    "Small steps count"
                ]
            }
        
        return render_template('chat.html', 
                             user=session['user'],
                             wellness_context=g.chat_context)
                             
    except Exception as e:
        log_with_self_compassion('error', f"Chat interface challenge: {e}")
        
        # 💕 Fallback with compassion
        supportive_user = {
            'id': 'resilient_explorer_' + datetime.now().strftime('%H%M%S'),
            'name': 'Resilient Explorer',
            'email': 'support@nous.app',
            'demo_mode': True,
            'affirmation': "Every challenge is a chance to grow"
        }
        
        return render_template('chat.html', 
                             user=supportive_user,
                             error_occurred=True,
                             support_message="Let's try a fresh start together")

@chat_bp.route('/chat/demo')
@stop_skill("creating demo experience")
def demo_chat():
    """
    Demo chat interface - A judgment-free space to explore
    """
    # Create a welcoming demo experience
    explorerIdentity = {  # Therapeutic variable name
        'id': 'curious_soul_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
        'name': 'Curious Soul',
        'email': 'explore@nous.app',
        'demo_mode': True,
        'login_time': datetime.now().isoformat(),
        'welcome_message': "Welcome to your safe exploration space",
        'affirmation': generate_affirmation('general'),
        'boundaries_note': "This is a wellness companion, not therapy"
    }
    
    return render_template('chat.html', 
                         user=explorerIdentity, 
                         demo_mode=True,
                         demo_features={
                             'mindfulness_tools': True,
                             'wellness_tracking': True,
                             'supportive_ai': True,
                             'professional_resources': '/resources'
                         })

@chat_bp.route('/chat/check-in', methods=['POST'])
@with_mindful_breathing(breath_count=1)
def emotional_check_in():
    """
    Optional emotional check-in endpoint
    Not diagnostic - just supportive awareness
    """
    try:
        data = request.get_json() or {}
        currentFeeling = data.get('feeling', 'present')  # Therapeutic naming
        
        # Generate supportive response
        response = {
            'acknowledged': True,
            'feeling': currentFeeling,
            'support': f"Thank you for sharing that you're feeling {currentFeeling}",
            'wellness_suggestion': _get_gentle_suggestion(currentFeeling),
            'affirmation': generate_affirmation('general'),
            'reminder': "Your feelings are valid and temporary",
            'boundaries': "For professional support, please see /resources"
        }
        
        return jsonify(response)
        
    except Exception as e:
        log_with_self_compassion('error', f"Check-in challenge: {e}")
        return jsonify({
            'acknowledged': True,
            'support': "I'm here with you",
            'affirmation': generate_affirmation('error')
        })

@chat_bp.route('/chat/affirmation')
def get_affirmation():
    """
    Get a fresh affirmation - because everyone needs encouragement
    """
    context = request.args.get('context', 'general')
    
    return jsonify({
        'affirmation': generate_affirmation(context),
        'timestamp': datetime.now().isoformat(),
        'reminder': "You are valued and capable"
    })

@chat_bp.route('/chat/wellness-break')
@cognitive_reframe(
    negative_pattern="Taking breaks is lazy",
    balanced_thought="Rest is productive self-care"
)
def wellness_break():
    """
    Encourage wellness breaks - self-care is not selfish
    """
    break_suggestions = [
        "Stand up and stretch for 30 seconds",
        "Take 3 deep breaths",
        "Look away from the screen at something distant",
        "Drink a glass of water mindfully",
        "Write down one thing you're grateful for"
    ]
    
    return jsonify({
        'break_suggestion': break_suggestions[datetime.now().second % len(break_suggestions)],
        'duration': "Just 1-2 minutes",
        'affirmation': "Taking breaks helps you show up better",
        'next_reminder': "in 25 minutes",
        'gentle_note': "Your wellbeing matters"
    })

# 🌸 Helper functions with compassion
def _get_gentle_suggestion(feeling: str) -> str:
    """
    Get a gentle wellness suggestion based on feeling
    Not prescriptive - just supportive options
    """
    suggestions = {
        'anxious': "Would you like to try a breathing exercise together?",
        'sad': "Sometimes a walk or talking to a friend can help. What feels right for you?",
        'stressed': "Let's take this one moment at a time. You've got this.",
        'happy': "Wonderful! Savoring positive moments is great self-care.",
        'tired': "Rest is important. Be gentle with yourself today.",
        'default': "Thank you for checking in. How can I support you?"
    }
    
    return suggestions.get(feeling.lower(), suggestions['default'])

# 💫 Export with love
__all__ = ['chat_bp']

# 🎊 Module blessing
log_with_self_compassion('info', "Chat routes initialized - ready to support and connect!")