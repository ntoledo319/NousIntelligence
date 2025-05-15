"""
Adaptive Conversation module for handling different levels of conversation difficulty.
This module helps tailor responses to the user's preferred level of complexity.
"""
from flask import session
from flask_login import current_user
from models import UserSettings, ConversationDifficulty

# Default difficulty if user is not logged in or has no preference set
DEFAULT_DIFFICULTY = ConversationDifficulty.INTERMEDIATE.value

def get_current_difficulty():
    """
    Get the current user's conversation difficulty preference.
    Returns the difficulty level as a string.
    """
    # If user is logged in, get their settings
    if current_user and current_user.is_authenticated:
        # If user has settings, return their difficulty
        if hasattr(current_user, 'settings') and current_user.settings:
            return current_user.settings.conversation_difficulty
        # Otherwise return default
        return DEFAULT_DIFFICULTY
    
    # For anonymous users, check session
    if 'conversation_difficulty' in session:
        return session['conversation_difficulty']
    
    # Default fallback
    return DEFAULT_DIFFICULTY

def set_difficulty(difficulty_level):
    """
    Set the conversation difficulty for the current user or session.
    
    Args:
        difficulty_level (str): One of the ConversationDifficulty enum values
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate input
    try:
        difficulty = ConversationDifficulty(difficulty_level)
    except ValueError:
        # Invalid difficulty level
        return False
    
    # For logged-in users, update database
    if current_user and current_user.is_authenticated:
        from app import db
        
        # Create settings if they don't exist
        if not current_user.settings:
            settings = UserSettings()
            settings.user_id = current_user.id
            db.session.add(settings)
        else:
            settings = current_user.settings
        
        # Update difficulty
        settings.conversation_difficulty = difficulty.value
        db.session.commit()
    else:
        # For anonymous users, store in session
        session['conversation_difficulty'] = difficulty.value
    
    return True

def adapt_response(response, explain_technical_terms=True):
    """
    Adapt a response based on the current conversation difficulty.
    
    Args:
        response (str): The original response text
        explain_technical_terms (bool): Whether to explain technical terms for lower difficulties
    
    Returns:
        str: The adapted response
    """
    difficulty = get_current_difficulty()
    
    # No adaptation needed for intermediate (default) or advanced/expert
    if difficulty in [ConversationDifficulty.INTERMEDIATE.value, 
                     ConversationDifficulty.ADVANCED.value,
                     ConversationDifficulty.EXPERT.value]:
        return response
    
    # For beginner level, simplify and add explanations
    if difficulty == ConversationDifficulty.BEGINNER.value:
        # For now, just add a simpler introduction
        simplified = "I'll explain this in simple terms: \n\n" + response
        
        # Future enhancement: Use AI to actually simplify the language
        return simplified
    
    # Default fallback
    return response

def get_difficulty_context():
    """
    Get additional context to add to AI prompts based on current difficulty.
    
    Returns:
        str: Context string to add to AI prompts
    """
    difficulty = get_current_difficulty()
    
    if difficulty == ConversationDifficulty.BEGINNER.value:
        return """
        Please explain everything in very simple terms. Avoid technical jargon,
        and when you must use a technical term, explain what it means. Use short
        sentences and simple language. Imagine you're explaining to someone with
        no background in this topic.
        """
    elif difficulty == ConversationDifficulty.INTERMEDIATE.value:
        return """
        Use everyday language and explain moderately technical concepts.
        You can use some domain-specific terms, but provide context where helpful.
        """
    elif difficulty == ConversationDifficulty.ADVANCED.value:
        return """
        You can use technical terms and assume familiarity with the domain.
        No need to explain basic concepts, but do explain advanced or specialized
        information.
        """
    elif difficulty == ConversationDifficulty.EXPERT.value:
        return """
        Use specialized terminology and advanced concepts freely. Assume deep
        domain knowledge and expertise. Be precise and technical rather than
        simplified.
        """
    
    # Default fallback
    return ""