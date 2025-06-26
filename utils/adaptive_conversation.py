"""
Adaptive conversation module for adjusting response complexity based on user preferences.
This module helps customize AI responses to match the user's preferred difficulty level.
"""

import os
import re
import logging
from flask import session, g
from flask_login import current_user

# Initialize with default difficulty
_current_difficulty = "intermediate"

def set_difficulty(difficulty_level):
    """Set the current conversation difficulty level globally"""
    global _current_difficulty
    _current_difficulty = difficulty_level
    logging.debug(f"Conversation difficulty set to: {difficulty_level}")

def get_current_difficulty():
    """
    Get the current conversation difficulty level

    Returns the difficulty level from:
    1. Global variable if set via set_difficulty()
    2. Current user's settings if authenticated
    3. Session settings if available
    4. Default to "intermediate" otherwise
    """
    global _current_difficulty

    # Try to get from current user's database settings first
    if current_user and current_user.is_authenticated and hasattr(current_user, 'settings') and current_user.settings:
        return current_user.settings.conversation_difficulty

    # Next try session
    if 'conversation_difficulty' in session:
        return session.get('conversation_difficulty')

    # Fall back to the global variable
    return _current_difficulty

def get_difficulty_context():
    """
    Returns a system context instruction based on current difficulty level
    This can be added to AI prompts to guide response complexity
    """
    difficulty = get_current_difficulty()

    if difficulty == "beginner":
        return """
        Please explain everything in very simple terms. Avoid technical jargon.
        Break down complex concepts into basic explanations.
        Use analogies and examples from everyday life.
        If you must use a technical term, define it immediately afterward.
        Assume no prior knowledge of the subject matter.
        """
    elif difficulty == "intermediate":
        return """
        Use everyday language and explain moderately complex concepts.
        You can use basic technical terms but define specialized ones.
        Provide some detail but avoid overwhelming with complexity.
        Assume basic familiarity with the subject matter.
        """
    elif difficulty == "advanced":
        return """
        You can use technical terms and assume familiarity with the domain.
        Provide detailed explanations and don't oversimplify.
        Only explain very specialized terminology.
        Assume good background knowledge of the subject.
        """
    elif difficulty == "expert":
        return """
        Use specialized terminology and advanced concepts freely.
        Provide technical details and nuanced explanations.
        No need to explain standard terminology in the field.
        Assume expert-level knowledge of the subject.
        """

    # Default if none of the above match
    return ""

def adapt_response(response, explain_technical_terms=True):
    """
    Adapt an AI-generated response to match the user's preferred difficulty level

    Args:
        response: The original AI response text
        explain_technical_terms: Whether to add explanations for technical terms (for beginner mode)

    Returns:
        str: The adapted response with appropriate complexity level
    """
    difficulty = get_current_difficulty()

    # For intermediate and above, return as is
    if difficulty in ["intermediate", "advanced", "expert"]:
        return response

    # For beginner level, perform transformations
    if difficulty == "beginner":
        # Simplify sentence structure
        simplified = _simplify_sentences(response)

        # Add explanations for technical terms if requested
        if explain_technical_terms:
            simplified = _add_term_explanations(simplified)

        return simplified

    # Default case - return original response
    return response

def _simplify_sentences(text):
    """Split complex sentences into simpler ones"""
    # Replace semicolons with periods
    text = re.sub(r';\s*', '. ', text)

    # Break up sentences with multiple commas
    sentences = re.split(r'(?<=[.!?])\s+', text)
    simplified_sentences = []

    for sentence in sentences:
        # If a sentence has multiple clauses with commas, consider breaking it up
        if sentence.count(',') > 2:
            parts = re.split(r',\s*', sentence)
            if len(parts) > 3:
                # Reconstruct as separate sentences when appropriate
                new_sentences = []
                current_sentence = parts[0]

                for part in parts[1:]:
                    # If part seems like it could be a standalone sentence, make it one
                    if len(part.split()) > 3 and part[0].isalpha() and part[0].isupper():
                        new_sentences.append(current_sentence + '.')
                        current_sentence = part
                    else:
                        current_sentence += ', ' + part

                new_sentences.append(current_sentence)
                simplified_sentences.extend(new_sentences)
            else:
                simplified_sentences.append(sentence)
        else:
            simplified_sentences.append(sentence)

    return ' '.join(simplified_sentences)

def _add_term_explanations(text):
    """Add explanations for technical terms"""
    # This is a simplified version - in a real implementation,
    # you might want to use an AI call to identify and explain technical terms

    # List of common technical terms and their simple explanations
    technical_terms = {
        'API': 'an interface that lets different software systems communicate',
        'algorithm': 'a step-by-step procedure for calculations or problem-solving',
        'bandwidth': 'the amount of data that can be transferred in a given time',
        'database': 'an organized collection of information',
        'encryption': 'the process of encoding data to prevent unauthorized access',
        'firewall': 'a security system that monitors and controls network traffic',
        'JSON': 'a format for storing and exchanging data',
        'latency': 'the delay before data transfer begins',
        'neural network': 'a computer system modeled on the human brain',
        'protocol': 'a set of rules for data exchange',
        'server': 'a computer that provides services to other computers',
        'SQL': 'a language used to communicate with databases',
        'UI': 'user interface, what you see and interact with on screen',
        'UX': 'user experience, how a person feels when using a product',
        'VPN': 'a service that hides your internet activity',
    }

    # Simple replacement of technical terms with explanations
    for term, explanation in technical_terms.items():
        # Case-insensitive search, preserve original capitalization
        pattern = re.compile(re.escape(term), re.IGNORECASE)

        # Only add explanation for first occurrence
        match = pattern.search(text)
        if match:
            orig_term = match.group(0)  # The term as it appears in the text
            replacement = f"{orig_term} ({explanation})"
            text = pattern.sub(replacement, text, count=1)

    return text