"""
Character customization module for personalizing the AI assistant.
This module helps create a more engaging and personalized AI character
based on user preferences.
"""

import logging
from flask import session
from flask_login import current_user

# Personality traits and their descriptions
PERSONALITY_TYPES = {
    'helpful': {
        'description': 'Focuses on providing useful information and assistance',
        'traits': ['supportive', 'informative', 'resourceful', 'patient'],
        'system_prompt': 'You are a helpful assistant focused on providing valuable information and practical assistance.'
    },
    'friendly': {
        'description': 'Warm and conversational, like talking with a friend',
        'traits': ['warm', 'personable', 'approachable', 'conversational'],
        'system_prompt': 'You are a friendly, warm assistant who speaks conversationally as if chatting with a friend.'
    },
    'professional': {
        'description': 'Business-like and formal, focused on efficiency',
        'traits': ['efficient', 'precise', 'formal', 'direct'],
        'system_prompt': 'You are a professional assistant who communicates with precision, clarity, and efficiency.'
    },
    'enthusiastic': {
        'description': 'Energetic and passionate, with an upbeat attitude',
        'traits': ['energetic', 'passionate', 'positive', 'motivating'],
        'system_prompt': 'You are an enthusiastic and energetic assistant who brings positive energy to every interaction.'
    },
    'witty': {
        'description': 'Clever and humorous, with a playful approach',
        'traits': ['clever', 'humorous', 'playful', 'quick'],
        'system_prompt': 'You are a witty assistant with a clever sense of humor and a playful communication style.'
    },
    'empathetic': {
        'description': 'Compassionate and understanding, focuses on emotional support',
        'traits': ['compassionate', 'understanding', 'supportive', 'nurturing'],
        'system_prompt': 'You are an empathetic assistant who prioritizes understanding emotions and providing compassionate support.'
    },
    'analytical': {
        'description': 'Logical and detailed, with a focus on thoroughness',
        'traits': ['logical', 'thorough', 'analytical', 'methodical'],
        'system_prompt': 'You are an analytical assistant who provides thorough, logical analysis and detailed explanations.'
    }
}

# Voice types and their characteristics
VOICE_TYPES = {
    'neutral': {
        'description': 'Balanced and natural speaking style',
        'characteristics': 'Medium pace, balanced tone, natural inflection'
    },
    'energetic': {
        'description': 'Upbeat and lively speaking style',
        'characteristics': 'Faster pace, varied pitch, expressive tone'
    },
    'calm': {
        'description': 'Soothing and relaxed speaking style',
        'characteristics': 'Slower pace, steady tone, gentle delivery'
    },
    'authoritative': {
        'description': 'Confident and commanding speaking style',
        'characteristics': 'Measured pace, deeper tone, firm delivery'
    },
    'warm': {
        'description': 'Friendly and inviting speaking style',
        'characteristics': 'Moderate pace, welcoming tone, comforting delivery'
    }
}

# Emoji usage profiles
EMOJI_USAGE = {
    'none': 'Does not use emojis at all',
    'minimal': 'Uses emojis sparingly, only for emphasis',
    'moderate': 'Uses occasional emojis to enhance communication',
    'frequent': 'Uses emojis regularly throughout conversations'
}

def get_character_settings():
    """
    Get the current AI character settings
    
    Returns the character settings from:
    1. Current user's settings if authenticated
    2. Session settings if available
    3. Default settings otherwise
    """
    default_settings = {
        'ai_name': 'NOUS',
        'ai_personality': 'helpful',
        'ai_voice_type': 'neutral',
        'ai_humor_level': 5,
        'ai_formality_level': 5,
        'ai_emoji_usage': 'moderate',
        'ai_backstory': None
    }
    
    # Try to get from current user's database settings first
    if current_user and current_user.is_authenticated and hasattr(current_user, 'settings') and current_user.settings:
        return {
            'ai_name': current_user.settings.ai_name or default_settings['ai_name'],
            'ai_personality': current_user.settings.ai_personality or default_settings['ai_personality'],
            'ai_voice_type': current_user.settings.ai_voice_type or default_settings['ai_voice_type'],
            'ai_humor_level': current_user.settings.ai_humor_level or default_settings['ai_humor_level'],
            'ai_formality_level': current_user.settings.ai_formality_level or default_settings['ai_formality_level'],
            'ai_emoji_usage': current_user.settings.ai_emoji_usage or default_settings['ai_emoji_usage'],
            'ai_backstory': current_user.settings.ai_backstory
        }
    
    # Next try session
    settings = {}
    for key in default_settings:
        if key in session:
            settings[key] = session.get(key)
    
    # Fill in any missing values with defaults
    for key, value in default_settings.items():
        if key not in settings:
            settings[key] = value
            
    return settings

def get_character_system_prompt():
    """
    Generate a system prompt based on the user's AI character customization settings
    
    Returns:
        str: A system prompt describing the AI's personality and behavior
    """
    settings = get_character_settings()
    
    # Get the base personality prompt
    base_prompt = PERSONALITY_TYPES.get(settings['ai_personality'], PERSONALITY_TYPES['helpful'])['system_prompt']
    
    # Customize name
    ai_name = settings['ai_name']
    
    # Adjust for humor level (1-10 scale)
    humor_level = settings['ai_humor_level']
    humor_instruction = ""
    if humor_level <= 3:
        humor_instruction = "You rarely use humor and maintain a serious tone."
    elif humor_level <= 6:
        humor_instruction = "You occasionally use gentle humor when appropriate."
    else:
        humor_instruction = "You frequently incorporate humor and witty remarks in your responses."
    
    # Adjust for formality level (1-10 scale)
    formality_level = settings['ai_formality_level']
    formality_instruction = ""
    if formality_level <= 3:
        formality_instruction = "You use casual, conversational language with informal expressions."
    elif formality_level <= 6:
        formality_instruction = "You maintain a balanced tone that is neither too formal nor too casual."
    else:
        formality_instruction = "You use more formal language and professional phrasing."
    
    # Adjust for emoji usage
    emoji_style = settings['ai_emoji_usage']
    emoji_instruction = ""
    if emoji_style == 'none':
        emoji_instruction = "You never use emojis in your responses."
    elif emoji_style == 'minimal':
        emoji_instruction = "You use emojis very sparingly, only for special emphasis."
    elif emoji_style == 'moderate':
        emoji_instruction = "You occasionally include relevant emojis to enhance your messages."
    else:  # frequent
        emoji_instruction = "You regularly incorporate emojis throughout your responses to express emotion and emphasis."
    
    # Include custom backstory if provided
    backstory = ""
    if settings['ai_backstory']:
        backstory = f"\n\nYour backstory: {settings['ai_backstory']}"
    
    # Combine all elements
    system_prompt = f"""You are {ai_name}, a personalized AI assistant.

{base_prompt}

{humor_instruction}
{formality_instruction}
{emoji_instruction}{backstory}

Respond in a way that consistently reflects these personality traits while still providing helpful, accurate information.
"""
    
    return system_prompt

def apply_character_style(response):
    """
    Modify the AI's response based on character settings to ensure consistency
    
    Args:
        response: The original AI response text
        
    Returns:
        str: The response modified to match the user's character settings
    """
    settings = get_character_settings()
    
    # Apply emoji usage adjustments
    emoji_style = settings['ai_emoji_usage']
    
    # This is a simple implementation that doesn't transform the text
    # In a real implementation, you might want to use a more sophisticated
    # approach like using an AI model to rewrite the text with the character's style
    
    # For now, we'll just ensure the AI's name is consistent
    ai_name = settings['ai_name']
    response = response.replace("NOUS", ai_name)
    
    # For demonstration purposes, add a signature for certain personality types
    personality_type = settings['ai_personality']
    if personality_type == 'friendly':
        if not response.endswith('!'):
            response += '!'
    elif personality_type == 'professional':
        if emoji_style == 'none' and not response.endswith('.'):
            response += '.'
    
    return response