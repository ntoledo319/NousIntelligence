import os
import logging
import json
from flask import session
from datetime import datetime, timedelta
from models import db, DBTEmotionTrack

# Emotion tracking and regulation functions

def log_emotion(session_obj, emotion_name, intensity, trigger=None,
                body_sensations=None, thoughts=None, urges=None, opposite_action=None):
    """
    Log an emotion experience

    Args:
        session_obj: Flask session object
        emotion_name: Name of the emotion
        intensity: Intensity level (1-10)
        trigger: What triggered the emotion
        body_sensations: Physical sensations experienced
        thoughts: Thoughts associated with the emotion
        urges: Action urges experienced
        opposite_action: Opposite action taken (if any)

    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}

        # Create new emotion tracking entry
        emotion = DBTEmotionTrack()
        emotion.user_id = user_id
        emotion.emotion_name = emotion_name
        emotion.intensity = min(max(intensity, 1), 10)  # Ensure 1-10 range
        emotion.trigger = trigger
        emotion.body_sensations = body_sensations
        emotion.thoughts = thoughts
        emotion.urges = urges
        emotion.opposite_action = opposite_action
        emotion.date_recorded = datetime.utcnow()
        emotion.created_at = datetime.utcnow()

        db.session.add(emotion)
        db.session.commit()

        return {
            "status": "success",
            "message": f"Emotion '{emotion_name}' logged successfully",
            "id": emotion.id
        }

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error logging emotion: {str(e)}")
        return {"status": "error", "message": f"Error logging emotion: {str(e)}"}


def get_emotion_history(session_obj, limit=10, emotion_name=None, days=30):
    """
    Get emotion tracking history

    Args:
        session_obj: Flask session object
        limit: Maximum number of entries to retrieve
        emotion_name: Optional filter for specific emotion
        days: Number of days to look back

    Returns:
        list: Emotion tracking entries
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return []

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Query emotions
        query = DBTEmotionTrack.query.filter_by(user_id=user_id)\
            .filter(DBTEmotionTrack.date_recorded >= start_date)

        if emotion_name:
            query = query.filter_by(emotion_name=emotion_name)

        emotions = query.order_by(DBTEmotionTrack.date_recorded.desc())\
            .limit(limit).all()

        return [emotion.to_dict() for emotion in emotions]

    except Exception as e:
        logging.error(f"Error retrieving emotion history: {str(e)}")
        return []


def get_emotion_stats(session_obj, days=30):
    """
    Get statistics on emotions tracked

    Args:
        session_obj: Flask session object
        days: Number of days to look back

    Returns:
        dict: Emotion statistics
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {}

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Query emotions within date range
        emotions = DBTEmotionTrack.query.filter_by(user_id=user_id)\
            .filter(DBTEmotionTrack.date_recorded >= start_date).all()

        if not emotions:
            return {"status": "info", "message": "No emotion data available"}

        # Calculate statistics
        emotion_counts = {}
        emotion_intensities = {}
        emotion_triggers = {}
        total_intensity = 0
        max_intensity = 0
        max_emotion = None
        opposite_action_count = 0

        for emotion in emotions:
            # Count by emotion name
            name = emotion.emotion_name.lower()
            emotion_counts[name] = emotion_counts.get(name, 0) + 1

            # Track intensities
            if name not in emotion_intensities:
                emotion_intensities[name] = []
            emotion_intensities[name].append(emotion.intensity)

            # Track triggers
            if emotion.trigger:
                trigger = emotion.trigger.lower()
                emotion_triggers[trigger] = emotion_triggers.get(trigger, 0) + 1

            # Track overall intensity
            total_intensity += emotion.intensity
            if emotion.intensity > max_intensity:
                max_intensity = emotion.intensity
                max_emotion = name

            # Count opposite actions
            if emotion.opposite_action:
                opposite_action_count += 1

        # Calculate averages and most common
        avg_intensity = total_intensity / len(emotions)
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        most_common_trigger = max(emotion_triggers.items(), key=lambda x: x[1])[0] if emotion_triggers else None

        # Create emotion averages
        emotion_avg_intensities = {
            name: sum(intensities) / len(intensities)
            for name, intensities in emotion_intensities.items()
        }

        # Calculate opposite action percentage
        opposite_action_pct = (opposite_action_count / len(emotions)) * 100

        return {
            "status": "success",
            "total_entries": len(emotions),
            "emotion_counts": emotion_counts,
            "emotion_avg_intensities": emotion_avg_intensities,
            "most_common_emotion": most_common_emotion,
            "most_common_trigger": most_common_trigger,
            "average_intensity": avg_intensity,
            "highest_intensity": max_intensity,
            "highest_intensity_emotion": max_emotion,
            "opposite_action_percentage": opposite_action_pct,
            "days_analyzed": days
        }

    except Exception as e:
        logging.error(f"Error calculating emotion stats: {str(e)}")
        return {"status": "error", "message": f"Error analyzing emotions: {str(e)}"}


def generate_emotion_insights(session_obj, emotion_name=None):
    """
    Generate personalized insights based on emotion tracking

    Args:
        session_obj: Flask session object
        emotion_name: Optional specific emotion to analyze

    Returns:
        dict: Personalized insights
    """
    try:
        # Get emotion history and stats
        history = get_emotion_history(session_obj, limit=30, emotion_name=emotion_name)
        stats = get_emotion_stats(session_obj)

        if not history or stats.get("status") == "info":
            return {"status": "info", "message": "Not enough emotion data for analysis"}

        # Prepare data for analysis
        emotion_context = f"for the emotion '{emotion_name}'" if emotion_name else "across all emotions"

        # Format history data
        history_text = ""
        for i, entry in enumerate(history[:10]):  # Limit to 10 entries to avoid token limits
            history_text += f"Entry {i+1}: {entry['emotion_name']} (intensity: {entry['intensity']})\n"

            if entry.get('trigger'):
                history_text += f"- Trigger: {entry['trigger']}\n"

            if entry.get('thoughts'):
                history_text += f"- Thoughts: {entry['thoughts']}\n"

            if entry.get('opposite_action'):
                history_text += f"- Opposite action: {entry['opposite_action']}\n"

            history_text += "\n"

        # Format stats data
        stats_text = f"Most common emotion: {stats.get('most_common_emotion', 'unknown')}\n"
        stats_text += f"Most common trigger: {stats.get('most_common_trigger', 'unknown')}\n"
        stats_text += f"Average intensity: {stats.get('average_intensity', 0):.1f}/10\n"
        stats_text += f"Opposite action used: {stats.get('opposite_action_percentage', 0):.1f}% of the time\n"

        # Generate insights with AI
        from utils.dbt_helper import call_router_direct

        prompt = f"""
        Based on this emotion tracking data {emotion_context}, provide 3-5 personalized DBT-based insights and recommendations.

        EMOTION HISTORY:
        {history_text}

        EMOTION STATISTICS:
        {stats_text}

        Your response should include:
        1. Key patterns observed in triggers, thoughts, or body sensations
        2. Specific DBT skills that would be most helpful based on the patterns
        3. Concrete suggestions for emotion regulation or opposite action
        4. One immediate practical step the person could take today

        Format your response with clear headings and bullet points.
        Focus on actionable DBT strategies rather than just observations.
        """

        response = call_router_direct(prompt)

        if not response:
            return {"status": "error", "message": "Could not generate insights"}

        return {
            "status": "success",
            "insights": response,
            "emotion_name": emotion_name,
            "entry_count": len(history),
            "stats": stats
        }

    except Exception as e:
        logging.error(f"Error generating emotion insights: {str(e)}")
        return {"status": "error", "message": f"Error generating insights: {str(e)}"}


def get_opposite_action_suggestion(session_obj, emotion, situation=None):
    """
    Get opposite action suggestions for a specific emotion

    Args:
        session_obj: Flask session object
        emotion: The emotion being experienced
        situation: Optional description of the situation

    Returns:
        dict: Opposite action suggestions
    """
    try:

        # Get any history for this emotion to personalize the response
        history = get_emotion_history(session_obj, limit=5, emotion_name=emotion)

        history_text = ""
        if history:
            history_text = "Based on your past tracking of this emotion:\n"
            for entry in history:
                if entry.get('trigger'):
                    history_text += f"- Previous trigger: {entry['trigger']}\n"
                if entry.get('opposite_action'):
                    history_text += f"- Previous opposite action: {entry['opposite_action']}\n"

        situation_text = f" in this situation: {situation}" if situation else ""

        prompt = f"""
        Provide detailed opposite action suggestions for the emotion of "{emotion}"{situation_text}.

        {history_text}

        Your response should include:
        1. A brief explanation of why opposite action is effective for this emotion
        2. 3-5 specific opposite actions to try, with clear step-by-step instructions
        3. How to know if the opposite action is working
        4. A reminder of when opposite action is appropriate vs. when to validate the emotion instead

        Focus on actionable, concrete steps that follow DBT principles.
        """

        response = call_router_direct(prompt)

        if not response:
            return {"status": "error", "message": "Could not generate opposite action suggestions"}

        return {
            "status": "success",
            "suggestions": response,
            "emotion": emotion
        }

    except Exception as e:
        logging.error(f"Error generating opposite action suggestions: {str(e)}")
        return {"status": "error", "message": f"Error generating suggestions: {str(e)}"}


def identify_emotion(session_obj, body_sensations=None, thoughts=None, situation=None):
    """
    Help identify emotions based on physical sensations, thoughts, or situations

    Args:
        session_obj: Flask session object
        body_sensations: Physical sensations being experienced
        thoughts: Thoughts being experienced
        situation: Description of the situation

    Returns:
        dict: Emotion identification results
    """
    try:

        # Need at least one input
        if not body_sensations and not thoughts and not situation:
            return {"status": "error", "message": "Please provide at least one of: body sensations, thoughts, or situation"}

        # Construct the prompt based on available information
        description = ""
        if body_sensations:
            description += f"Body sensations: {body_sensations}\n"
        if thoughts:
            description += f"Thoughts: {thoughts}\n"
        if situation:
            description += f"Situation: {situation}\n"

        prompt = f"""
        Based on the following description, identify the potential primary and secondary emotions being experienced:

        {description}

        Your response should include:
        1. Primary emotion(s) with confidence level (e.g., "Anger - 80% confidence")
        2. Possible secondary emotion(s) with confidence level
        3. Brief explanation for each identified emotion
        4. Suggestions for further clarifying the emotions (what to notice)

        Format as a structured list with clear headings.
        Use the 8 basic emotions as a framework: joy, sadness, fear, anger, surprise, disgust, trust, and anticipation.
        """

        response = call_router_direct(prompt)

        if not response:
            return {"status": "error", "message": "Could not identify emotions"}

        return {
            "status": "success",
            "analysis": response
        }

    except Exception as e:
        logging.error(f"Error identifying emotions: {str(e)}")
        return {"status": "error", "message": f"Error identifying emotions: {str(e)}"}


def check_emotion_vulnerability(session_obj):
    """
    Check for emotional vulnerability factors based on user's history

    Args:
        session_obj: Flask session object

    Returns:
        dict: Vulnerability assessment
    """
    try:

        # Get recent emotion history
        history = get_emotion_history(session_obj, limit=15)

        if not history:
            return {"status": "info", "message": "Not enough emotion data for analysis"}

        # Count high intensity emotions in last few days
        high_intensity_count = 0
        emotion_names = []
        three_days_ago = datetime.utcnow() - timedelta(days=3)

        for entry in history:
            emotion_names.append(entry['emotion_name'])
            entry_date = datetime.fromisoformat(entry['date_recorded'])

            # Check for high intensity emotions in last 3 days
            if entry['intensity'] >= 7 and entry_date >= three_days_ago:
                high_intensity_count += 1

        vulnerability_level = "low"
        if high_intensity_count >= 3:
            vulnerability_level = "high"
        elif high_intensity_count >= 1:
            vulnerability_level = "medium"

        # Generate assessment with AI
        emotions_text = ", ".join(emotion_names[:10])

        prompt = f"""
        Assess vulnerability to emotional dysregulation based on:
        - Recent emotions tracked: {emotions_text}
        - Number of high intensity emotions (7-10) in last 3 days: {high_intensity_count}
        - Current vulnerability level: {vulnerability_level}

        Provide a brief assessment including:
        1. Current vulnerability status and what it means
        2. Top 3 PLEASE skills to focus on right now (from DBT)
        3. One specific self-care suggestion

        Keep the response concise (under 200 words) and action-oriented.
        """

        response = call_router_direct(prompt)

        if not response:
            return {
                "status": "partial",
                "message": "Could not generate detailed assessment",
                "vulnerability_level": vulnerability_level,
                "high_intensity_count": high_intensity_count
            }

        return {
            "status": "success",
            "assessment": response,
            "vulnerability_level": vulnerability_level,
            "high_intensity_count": high_intensity_count
        }

    except Exception as e:
        logging.error(f"Error checking emotional vulnerability: {str(e)}")
        return {"status": "error", "message": f"Error checking vulnerability: {str(e)}"}