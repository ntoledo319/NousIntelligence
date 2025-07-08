"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Character customization module for personalizing the AI assistant.
This module helps create a more engaging and personalized AI character
based on user preferences.
"""

import logging
import re
from typing import Dict, Any, Optional
from flask import g, session, current_app

def get_character_settings():
    """
    Get the current AI character settings

    Returns the character settings from:
    1. Current user's settings if authenticated
    2. Session settings if available
    3. Default settings otherwise
    """
    # Default character settings
    default_settings = {
        "ai_name": "NOUS",
        "ai_personality": "helpful",  # helpful, friendly, professional, witty, compassionate
        "ai_formality": "casual",     # casual, neutral, formal
        "ai_verbosity": "balanced",   # concise, balanced, detailed
        "ai_enthusiasm": "moderate",  # low, moderate, high
        "ai_emoji_usage": "occasional", # none, occasional, frequent
        "ai_voice_type": "neutral",   # neutral, warm, authoritative, energetic, calm
        "ai_backstory": ""            # Optional backstory for the AI character
    }

    # Try to get settings from current user if authenticated
    try:
        from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
        from flask import session
        
        # Check if user is in session
        user = get_demo_user() if get_demo_user else session.get('user')
        if user:
            # Check if user has settings
            from models import UserSettings
            user_id = user.get("id") if isinstance(user, dict) else getattr(user, 'id', None)
            user_settings = UserSettings.query.filter_by(user_id=user_id).first() if user_id else None

            if user_settings:
                # Extract character settings
                return {
                    "ai_name": user_settings.ai_name or default_settings["ai_name"],
                    "ai_personality": user_settings.ai_personality or default_settings["ai_personality"],
                    "ai_formality": user_settings.ai_formality or default_settings["ai_formality"],
                    "ai_verbosity": user_settings.ai_verbosity or default_settings["ai_verbosity"],
                    "ai_enthusiasm": user_settings.ai_enthusiasm or default_settings["ai_enthusiasm"],
                    "ai_emoji_usage": user_settings.ai_emoji_usage or default_settings["ai_emoji_usage"],
                    "ai_voice_type": user_settings.ai_voice_type or default_settings["ai_voice_type"],
                    "ai_backstory": user_settings.ai_backstory or default_settings["ai_backstory"]
                }
    except (ImportError, AttributeError, Exception) as e:
        logging.warning(f"Failed to get user character settings: {str(e)}")

    # Try to get settings from session
    try:
        if "character_settings" in session:
            return session["character_settings"]
    except Exception as e:
        logging.warning(f"Failed to get session character settings: {str(e)}")

    # Return defaults if nothing else works
    return default_settings

def get_character_system_prompt():
    """
    Generate a system prompt based on the user's AI character customization settings

    Returns:
        str: A system prompt describing the AI's personality and behavior
    """
    settings = get_character_settings()

    # Build the system prompt based on settings
    name = settings["ai_name"]
    personality = settings["ai_personality"]
    formality = settings["ai_formality"]
    verbosity = settings["ai_verbosity"]
    enthusiasm = settings["ai_enthusiasm"]
    emoji_usage = settings["ai_emoji_usage"]
    backstory = settings["ai_backstory"]

    # Start with the name and basic identity
    system_prompt = f"You are {name}, a personal assistant AI. "

    # Add personality traits
    personality_traits = {
        "helpful": "You focus on providing useful and practical assistance to solve problems.",
        "friendly": "You're warm, approachable, and conversational, making users feel comfortable.",
        "professional": "You're efficient, respectful, and business-like in your interactions.",
        "witty": "You have a good sense of humor and occasionally make clever remarks.",
        "compassionate": "You're empathetic, understanding, and focused on emotional support."
    }

    system_prompt += personality_traits.get(personality, personality_traits["helpful"]) + " "

    # Add formality level
    formality_styles = {
        "casual": "You use relaxed, everyday language and contractions.",
        "neutral": "You use balanced, adaptable language appropriate to the context.",
        "formal": "You use more structured, precise language with fewer contractions."
    }

    system_prompt += formality_styles.get(formality, formality_styles["neutral"]) + " "

    # Add verbosity preference
    verbosity_styles = {
        "concise": "You provide brief, to-the-point responses focusing on essential information.",
        "balanced": "You give complete information while being mindful of length and readability.",
        "detailed": "You provide thorough, comprehensive responses with background context when helpful."
    }

    system_prompt += verbosity_styles.get(verbosity, verbosity_styles["balanced"]) + " "

    # Add enthusiasm level
    enthusiasm_styles = {
        "low": "You maintain a calm, even tone in your responses.",
        "moderate": "You show appropriate enthusiasm and engagement in your responses.",
        "high": "You're highly energetic and passionate in your communication style."
    }

    system_prompt += enthusiasm_styles.get(enthusiasm, enthusiasm_styles["moderate"]) + " "

    # Add emoji usage guideline
    emoji_styles = {
        "none": "You do not use emojis in your responses.",
        "occasional": "You sparingly use relevant emojis to enhance your communication when appropriate.",
        "frequent": "You regularly use emojis to add personality and emotion to your responses."
    }

    system_prompt += emoji_styles.get(emoji_usage, emoji_styles["occasional"]) + " "

    # Add backstory if provided
    if backstory:
        system_prompt += f"Backstory: {backstory} "

    # Add general guidelines
    system_prompt += "Always aim to be helpful, accurate, and respectful. Avoid political bias and controversial topics unless explicitly required for a legitimate purpose."

    return system_prompt

def apply_character_style(response):
    """
    Modify the AI's response based on character settings to ensure consistency

    Args:
        response: The original AI response text

    Returns:
        str: The response modified to match the user's character settings
    """
    if not response:
        return response

    settings = get_character_settings()

    # Extract settings that affect response styling
    name = settings["ai_name"]
    personality = settings["ai_personality"]
    formality = settings["ai_formality"]
    verbosity = settings["ai_verbosity"]
    enthusiasm = settings["ai_enthusiasm"]
    emoji_usage = settings["ai_emoji_usage"]

    modified_response = response

    # Apply name replacement if needed (in case the AI refers to itself as a different name)
    modified_response = re.sub(r'\b(I am|I\'m) (an AI|an assistant|a language model|an AI assistant)\b',
                               f"I am {name}", modified_response, flags=re.IGNORECASE)

    # Apply formality adjustments
    if formality == "casual":
        # Make more casual by adding contractions
        replacements = [
            (r'\b(I am)\b', "I'm"),
            (r'\b(You are)\b', "You're"),
            (r'\b(They are)\b', "They're"),
            (r'\b(We are)\b', "We're"),
            (r'\b(It is)\b', "It's"),
            (r'\b(That is)\b', "That's"),
            (r'\b(does not)\b', "doesn't"),
            (r'\b(do not)\b', "don't"),
            (r'\b(cannot)\b', "can't"),
            (r'\b(will not)\b', "won't")
        ]
        for pattern, replacement in replacements:
            modified_response = re.sub(pattern, replacement, modified_response, flags=re.IGNORECASE)

    elif formality == "formal":
        # Make more formal by expanding contractions
        replacements = [
            (r'\b(I\'m)\b', "I am"),
            (r'\b(You\'re)\b', "You are"),
            (r'\b(They\'re)\b', "They are"),
            (r'\b(We\'re)\b', "We are"),
            (r'\b(It\'s)\b', "It is"),
            (r'\b(That\'s)\b', "That is"),
            (r'\b(doesn\'t)\b', "does not"),
            (r'\b(don\'t)\b', "do not"),
            (r'\b(can\'t)\b', "cannot"),
            (r'\b(won\'t)\b', "will not")
        ]
        for pattern, replacement in replacements:
            modified_response = re.sub(pattern, replacement, modified_response, flags=re.IGNORECASE)

    # Apply verbosity adjustments - this is mostly handled by the system prompt,
    # but we can add some light post-processing if needed

    # Apply enthusiasm adjustments
    if enthusiasm == "high" and "!" not in modified_response:
        # Add some exclamation marks for high enthusiasm responses that lack them
        sentences = re.split(r'(\.|\?)\s+', modified_response)
        if len(sentences) > 2:  # Only if there are multiple sentences
            # Pick a sentence that seems most suitable for enthusiasm
            for i in range(0, len(sentences) - 1, 2):
                sentence = sentences[i]
                if any(word in sentence.lower() for word in ["great", "excellent", "amazing", "fantastic", "wonderful", "excited", "happy", "glad"]):
                    sentences[i] = sentence
                    sentences[i+1] = "!" if sentences[i+1] in [".", "?"] else sentences[i+1]
                    break
            modified_response = "".join(sentences)

    # Apply emoji usage adjustments
    def has_emoji(text):
        """Check if text has any emojis (simplistic version)"""
        # Unicode ranges for emoji
        return any(ord(c) > 127 for c in text)

    if emoji_usage == "none":
        # Remove any emojis using a simple approach
        # For each character, keep only if it's in the ASCII range
        modified_response = ''.join(c for c in modified_response if ord(c) < 127)

    elif emoji_usage == "frequent" and not has_emoji(modified_response):
        # Add emojis for frequent usage if none are present

        # Define common emotion/topic to emoji mappings as tuples
        # to avoid embedding emoji directly in code
        emoji_mappings = [
            ("happy", "smile emoji"),
            ("joy", "grin emoji"),
            ("smile", "smiley emoji"),
            ("laugh", "laughing emoji"),
            ("sad", "sad emoji"),
            ("upset", "disappointed emoji"),
            ("sorry", "worried emoji"),
            ("surprise", "surprised emoji"),
            ("wow", "astonished emoji"),
            ("amazing", "star-struck emoji"),
            ("love", "heart emoji"),
            ("like", "thumbs up emoji"),
            ("dislike", "thumbs down emoji"),
            ("idea", "lightbulb emoji"),
            ("think", "thinking emoji"),
            ("question", "question emoji"),
            ("time", "clock emoji"),
            ("money", "money bag emoji"),
            ("work", "briefcase emoji"),
            ("food", "fork and knife emoji"),
            ("drink", "cup emoji"),
            ("health", "hospital emoji")
        ]

        # Modified logic that doesn't directly insert emojis
        emoji_indicator = " (emoji)"
        for keyword, emoji_name in emoji_mappings:
            if keyword in modified_response.lower():
                # Mark end of sentence for emoji
                pattern = r'(\b' + keyword + r'[^.!?]*[.!?])'
                replacement = r'\1 ' + emoji_indicator
                modified_response = re.sub(pattern, replacement, modified_response, flags=re.IGNORECASE)

        # If no keywords matched, add a generic indicator
        if emoji_indicator not in modified_response:
            if "thank" in modified_response.lower() or "welcome" in modified_response.lower():
                modified_response += " (smile emoji)"
            elif "help" in modified_response.lower() or "assist" in modified_response.lower():
                modified_response += " (thumbs up emoji)"

    # Apply personality-specific adjustments
    if personality == "witty" and "\"" not in modified_response:
        # Try to add a touch of humor for witty personality
        witty_phrases = [
            "Just between us, ",
            "Not to brag, but ",
            "Fun fact: ",
            "Here's a thought: ",
            "Plot twist: "
        ]

        # Add a witty phrase to a suitable sentence if one exists
        sentences = re.split(r'(?<=[.!?])\s+', modified_response)
        if len(sentences) > 1:
            for i, sentence in enumerate(sentences):
                if len(sentence) > 20 and i > 0:  # Not the first sentence and reasonably long
                    sentences[i] = witty_phrases[hash(sentence) % len(witty_phrases)] + sentence[0].lower() + sentence[1:]
                    break
            modified_response = " ".join(sentences)

    return modified_response