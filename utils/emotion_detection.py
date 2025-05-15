"""
Emotion detection from voice and text interactions.
This module analyzes user input to detect emotions and improve response personalization.
"""

import json
import logging
import re
from typing import Dict, List, Tuple, Optional
import datetime
from flask import current_app

# Import OpenAI client from the ai_helper module
try:
    from utils.ai_helper import client as openai_client
    OPENAI_AVAILABLE = True
except (ImportError, AttributeError):
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI client not available for emotion detection")

# Emotion categories with their descriptions and associated keywords/phrases
EMOTION_CATEGORIES = {
    "happiness": {
        "description": "Feelings of joy, contentment, satisfaction",
        "keywords": ["happy", "excited", "great", "awesome", "love", "enjoy", "wonderful", "glad", "pleasure", "delighted"],
        "voice_traits": ["higher pitch", "energetic tone", "faster pace", "animated delivery"]
    },
    "sadness": {
        "description": "Feelings of sorrow, disappointment, grief",
        "keywords": ["sad", "disappointed", "upset", "unhappy", "down", "depressed", "miserable", "heartbroken", "sorry", "regret"],
        "voice_traits": ["lower pitch", "slow pace", "monotone", "quieter volume", "sighing"]
    },
    "anger": {
        "description": "Feelings of displeasure, hostility, frustration",
        "keywords": ["angry", "mad", "frustrat", "annoyed", "irritated", "furious", "hate", "resent", "outraged", "infuriated"],
        "voice_traits": ["higher volume", "faster pace", "sharp tone", "clipped words", "emphasis"]
    },
    "fear": {
        "description": "Feelings of anxiety, worry, nervousness",
        "keywords": ["afraid", "scared", "worried", "anxious", "terrified", "nervous", "frightened", "concerned", "panic", "dread"],
        "voice_traits": ["wavering voice", "higher pitch", "quicker pace", "hesitations", "trembling"]
    },
    "surprise": {
        "description": "Feelings of astonishment, amazement, shock",
        "keywords": ["surprised", "shocked", "amazed", "wow", "unexpected", "astonished", "incredible", "unbelievable", "startled", "stunned"],
        "voice_traits": ["higher pitch", "abrupt changes", "gasps", "pauses"]
    },
    "confusion": {
        "description": "Feelings of uncertainty, puzzlement, lack of clarity",
        "keywords": ["confused", "unsure", "not understand", "puzzled", "unclear", "lost", "perplexed", "bewildered", "doubt", "uncertain"],
        "voice_traits": ["frequent pauses", "restarts", "questioning tone", "slower pace"]
    },
    "neutral": {
        "description": "No strong emotion detected",
        "keywords": [],
        "voice_traits": ["even tone", "moderate pace", "consistent volume", "regular rhythm"]
    }
}

def detect_emotion_from_text(text: str) -> Tuple[str, float]:
    """
    Detect emotion from text using keyword analysis
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (emotion_name, confidence_score)
    """
    if not text:
        return ("neutral", 0.5)
    
    text = text.lower()
    scores = {emotion: 0.0 for emotion in EMOTION_CATEGORIES.keys()}
    
    # Check for emotion keywords
    for emotion, data in EMOTION_CATEGORIES.items():
        if emotion == "neutral":
            continue  # Skip neutral as it's the fallback
            
        for keyword in data["keywords"]:
            # Count occurrences of keyword (partial match for word stems)
            matches = re.findall(r'\b' + re.escape(keyword) + r'[a-z]*\b', text)
            scores[emotion] += len(matches) * 0.2  # Weight each occurrence
    
    # Check for emotional punctuation and formatting
    if "!" in text:
        exclamation_count = text.count("!")
        # Distribute among appropriate emotions based on context
        if any(kw in text for kw in EMOTION_CATEGORIES["happiness"]["keywords"]):
            scores["happiness"] += exclamation_count * 0.1
        elif any(kw in text for kw in EMOTION_CATEGORIES["anger"]["keywords"]):
            scores["anger"] += exclamation_count * 0.1
        elif any(kw in text for kw in EMOTION_CATEGORIES["surprise"]["keywords"]):
            scores["surprise"] += exclamation_count * 0.1
        
    # Check for question marks (potential confusion)
    if "?" in text:
        question_count = text.count("?")
        if question_count > 1:
            scores["confusion"] += question_count * 0.1
    
    # Find the highest scoring emotion
    if max(scores.values()) > 0:
        top_emotion = max(scores.items(), key=lambda x: x[1])
        # Normalize confidence score to 0-1 range (capped at 0.9 due to simplistic approach)
        confidence = min(0.9, top_emotion[1])
        return (top_emotion[0], confidence)
    
    # Default to neutral if no emotions detected
    return ("neutral", 0.5)

def analyze_emotion_with_ai(text: str) -> Tuple[str, float]:
    """
    Use OpenAI to detect emotion from text with higher accuracy
    
    Args:
        text: The text to analyze
        
    Returns:
        Tuple of (emotion_name, confidence_score)
    """
    if not OPENAI_AVAILABLE or not openai_client:
        # Fall back to keyword-based detection
        return detect_emotion_from_text(text)
    
    try:
        system_prompt = """Analyze the emotional content of the following text. 
        Determine the primary emotion expressed and provide a confidence score from 0.0 to 1.0.
        Limit your emotion classification to one of these categories: happiness, sadness, anger, fear, surprise, confusion, neutral.
        
        Respond with a JSON object in this format:
        {"emotion": "emotion_name", "confidence": 0.85, "reasoning": "brief explanation"}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Extract and validate emotion and confidence
        emotion = result.get("emotion", "neutral").lower()
        confidence = float(result.get("confidence", 0.5))
        
        # Ensure emotion is one of our categories
        if emotion not in EMOTION_CATEGORIES:
            emotion = "neutral"
            
        # Ensure confidence is within range
        confidence = max(0.0, min(1.0, confidence))
        
        return (emotion, confidence)
        
    except Exception as e:
        logging.error(f"Error using AI for emotion detection: {str(e)}")
        # Fall back to keyword-based detection
        return detect_emotion_from_text(text)

def analyze_voice_audio(audio_data, user_id: str) -> Dict:
    """
    Analyze voice audio for emotion markers
    
    Args:
        audio_data: The raw audio data or file path
        user_id: The user ID for tracking purposes
        
    Returns:
        Dict containing emotion analysis results
    """
    # In a real implementation, this would use audio processing libraries
    # like librosa, pyAudioAnalysis, or cloud APIs like Google's Speech-to-Text
    # with sentiment analysis or Azure's Speech Services
    
    # This is a placeholder implementation that defaults to a neutral detection
    # A real implementation would analyze pitch, tone, speed, volume variations, etc.
    
    # For demonstration, we'll return a default result
    return {
        "emotion": "neutral",
        "confidence": 0.5,
        "audio_features": {
            "pitch": "medium",
            "speed": "normal",
            "volume": "medium"
        }
    }

def log_emotion(user_id: str, emotion: str, confidence: float, source: str, details: Optional[str] = None):
    """
    Log detected emotion to the database for future personalization
    
    Args:
        user_id: The user's ID
        emotion: The detected emotion
        confidence: Confidence score (0-1)
        source: Source of the emotion detection ('text', 'voice', 'image')
        details: Optional additional details
    """
    from models import db, UserEmotionLog
    
    try:
        # Create a new emotion log entry
        emotion_log = UserEmotionLog(
            user_id=user_id,
            emotion=emotion,
            confidence=confidence,
            source=source,
            details=details,
            timestamp=datetime.datetime.utcnow()
        )
        
        # Add to database and commit
        db.session.add(emotion_log)
        db.session.commit()
        
        logging.debug(f"Logged emotion for user {user_id}: {emotion} ({confidence:.2f}) from {source}")
        
    except Exception as e:
        logging.error(f"Failed to log emotion: {str(e)}")
        db.session.rollback()

def get_recent_emotions(user_id: str, limit: int = 5) -> List[Dict]:
    """
    Get a user's recent emotion logs
    
    Args:
        user_id: The user's ID
        limit: Maximum number of emotions to retrieve
        
    Returns:
        List of emotion log dictionaries
    """
    from models import UserEmotionLog
    
    try:
        # Query the most recent emotion logs
        emotion_logs = UserEmotionLog.query.filter_by(
            user_id=user_id
        ).order_by(
            UserEmotionLog.timestamp.desc()
        ).limit(limit).all()
        
        # Convert to dictionaries
        result = []
        for log in emotion_logs:
            result.append({
                "emotion": log.emotion,
                "confidence": log.confidence,
                "source": log.source,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details
            })
            
        return result
        
    except Exception as e:
        logging.error(f"Error retrieving emotion logs: {str(e)}")
        return []

def get_emotional_state_summary(user_id: str) -> str:
    """
    Generate a summary of the user's recent emotional state for AI context
    
    Args:
        user_id: The user's ID
        
    Returns:
        String summarizing the user's emotional state
    """
    emotions = get_recent_emotions(user_id, limit=10)
    
    if not emotions:
        return ""
    
    # Count occurrences of each emotion
    emotion_counts = {}
    for e in emotions:
        emotion = e["emotion"]
        if emotion in emotion_counts:
            emotion_counts[emotion] += 1
        else:
            emotion_counts[emotion] = 1
    
    # Find the dominant emotion
    dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
    
    # Get the most recent emotion
    most_recent = emotions[0]["emotion"]
    
    # Generate a summary
    if dominant_emotion[0] == most_recent:
        return f"User has been consistently {dominant_emotion[0]} recently."
    else:
        return f"User has been mostly {dominant_emotion[0]} recently, but is currently {most_recent}."

def process_user_message(user_id: str, message: str, is_voice: bool = False) -> Dict:
    """
    Process a user message to detect emotional content and log it
    
    Args:
        user_id: The user's ID
        message: The text message
        is_voice: Whether this message was from voice input
        
    Returns:
        Dict with emotion detection results
    """
    # Detect emotion from the text
    if OPENAI_AVAILABLE and openai_client:
        emotion, confidence = analyze_emotion_with_ai(message)
    else:
        emotion, confidence = detect_emotion_from_text(message)
    
    # Log the detected emotion
    source = "voice" if is_voice else "text"
    log_emotion(user_id, emotion, confidence, source)
    
    return {
        "emotion": emotion,
        "confidence": confidence,
        "is_voice": is_voice,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }