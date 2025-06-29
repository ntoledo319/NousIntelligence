"""
CBT Helper - Comprehensive Cognitive Behavioral Therapy Support

This module provides comprehensive CBT functionality including:
- Thought record processing and cognitive restructuring
- Cognitive bias identification and correction
- Behavioral experiments and activity scheduling
- Mood tracking and analysis
- Coping skills library and management
- Goal setting and progress tracking
"""

import os
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from flask import session
from sqlalchemy import and_, or_, desc, func

# Import database models
from models.health_models import (
    CBTThoughtRecord, CBTCognitiveBias, CBTBehaviorExperiment,
    CBTActivitySchedule, CBTMoodLog, CBTCopingSkill, CBTSkillUsage, CBTGoal
)
from database import db

# AI service for CBT guidance
import openai

# Configure logging
logger = logging.getLogger(__name__)

# OpenRouter API configuration
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
if not OPENROUTER_KEY:
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-or-"):
        OPENROUTER_KEY = openai_key

OPENROUTER_API_URL = "https://openrouter.ai/api/v1"

# Create OpenAI client for CBT assistance
client = None
if OPENROUTER_KEY:
    openai.api_key = OPENROUTER_KEY
    openai.base_url = OPENROUTER_API_URL

# Common cognitive biases with descriptions
COGNITIVE_BIASES = {
    "all_or_nothing": {
        "name": "All-or-Nothing Thinking",
        "description": "Seeing things in black and white with no middle ground",
        "examples": ["I'm a complete failure", "This is perfect or terrible"],
        "reframe": "Look for the gray areas and partial successes"
    },
    "catastrophizing": {
        "name": "Catastrophizing",
        "description": "Imagining the worst possible outcome",
        "examples": ["This will be a disaster", "Everything will go wrong"],
        "reframe": "What's the most likely realistic outcome?"
    },
    "mind_reading": {
        "name": "Mind Reading",
        "description": "Assuming you know what others are thinking",
        "examples": ["They think I'm stupid", "She doesn't like me"],
        "reframe": "I can't read minds - what evidence do I actually have?"
    },
    "fortune_telling": {
        "name": "Fortune Telling",
        "description": "Predicting negative outcomes without evidence",
        "examples": ["I'll never succeed", "This will definitely fail"],
        "reframe": "I can't predict the future - let me focus on what I can control"
    },
    "emotional_reasoning": {
        "name": "Emotional Reasoning",
        "description": "Believing something is true because you feel it",
        "examples": ["I feel guilty, so I must have done something wrong"],
        "reframe": "Feelings aren't facts - what's the actual evidence?"
    },
    "should_statements": {
        "name": "Should Statements",
        "description": "Using 'should', 'must', or 'have to' excessively",
        "examples": ["I should be perfect", "They must approve of me"],
        "reframe": "Replace 'should' with 'prefer' or 'would like'"
    },
    "labeling": {
        "name": "Labeling",
        "description": "Defining yourself or others with negative labels",
        "examples": ["I'm an idiot", "They're selfish"],
        "reframe": "Focus on specific behaviors rather than global labels"
    },
    "personalization": {
        "name": "Personalization",
        "description": "Taking responsibility for things outside your control",
        "examples": ["It's all my fault", "I made them angry"],
        "reframe": "What parts are actually within my control?"
    },
    "mental_filter": {
        "name": "Mental Filter",
        "description": "Focusing only on negative details",
        "examples": ["The whole day was ruined by one mistake"],
        "reframe": "What positive aspects am I overlooking?"
    },
    "disqualifying_positive": {
        "name": "Disqualifying the Positive",
        "description": "Dismissing positive experiences as unimportant",
        "examples": ["That compliment doesn't count", "I just got lucky"],
        "reframe": "Positive experiences are valid and meaningful"
    }
}

# CBT Coping Skills Library
DEFAULT_COPING_SKILLS = [
    {
        "skill_name": "Deep Breathing (4-7-8 Technique)",
        "category": "relaxation",
        "description": "A calming breathing technique to reduce anxiety and stress",
        "instructions": "1. Inhale through nose for 4 counts\n2. Hold breath for 7 counts\n3. Exhale through mouth for 8 counts\n4. Repeat 3-4 times",
        "duration_minutes": 5,
        "difficulty_level": 1,
        "effectiveness_situations": ["anxiety", "panic", "stress", "insomnia"]
    },
    {
        "skill_name": "5-4-3-2-1 Grounding Technique",
        "category": "grounding",
        "description": "Sensory grounding technique to reduce anxiety and stay present",
        "instructions": "Name:\n• 5 things you can see\n• 4 things you can touch\n• 3 things you can hear\n• 2 things you can smell\n• 1 thing you can taste",
        "duration_minutes": 10,
        "difficulty_level": 1,
        "effectiveness_situations": ["anxiety", "panic", "dissociation", "overwhelm"]
    },
    {
        "skill_name": "Progressive Muscle Relaxation",
        "category": "relaxation",
        "description": "Systematic tensing and relaxing of muscle groups",
        "instructions": "1. Start with toes, tense for 5 seconds then relax\n2. Move up through legs, abdomen, arms, shoulders, face\n3. Notice the contrast between tension and relaxation\n4. End with whole body relaxation",
        "duration_minutes": 15,
        "difficulty_level": 2,
        "effectiveness_situations": ["stress", "anxiety", "insomnia", "tension"]
    },
    {
        "skill_name": "Thought Challenging",
        "category": "cognitive",
        "description": "Systematic examination of negative thoughts for accuracy",
        "instructions": "1. Identify the negative thought\n2. Ask: What evidence supports this?\n3. Ask: What evidence contradicts this?\n4. Generate a balanced, realistic thought\n5. Notice how your mood changes",
        "duration_minutes": 10,
        "difficulty_level": 3,
        "effectiveness_situations": ["depression", "anxiety", "self-criticism", "worry"]
    },
    {
        "skill_name": "STOP Technique",
        "category": "behavioral",
        "description": "Pause and respond rather than react impulsively",
        "instructions": "S - Stop what you're doing\nT - Take a breath\nO - Observe thoughts, feelings, sensations\nP - Proceed with awareness and intention",
        "duration_minutes": 2,
        "difficulty_level": 1,
        "effectiveness_situations": ["anger", "impulsivity", "conflict", "stress"]
    },
    {
        "skill_name": "Behavioral Activation",
        "category": "behavioral",
        "description": "Engaging in meaningful activities to improve mood",
        "instructions": "1. Choose one small, enjoyable activity\n2. Schedule it for a specific time\n3. Focus on the process, not outcomes\n4. Notice mood before and after\n5. Build on small successes",
        "duration_minutes": 30,
        "difficulty_level": 2,
        "effectiveness_situations": ["depression", "low motivation", "isolation", "apathy"]
    },
    {
        "skill_name": "Mindful Observation",
        "category": "grounding",
        "description": "Non-judgmental awareness of present moment experience",
        "instructions": "1. Choose an object to observe\n2. Notice colors, textures, shapes, shadows\n3. If mind wanders, gently return to observing\n4. Stay curious and non-judgmental\n5. Continue for 5-10 minutes",
        "duration_minutes": 10,
        "difficulty_level": 2,
        "effectiveness_situations": ["anxiety", "rumination", "stress", "overwhelm"]
    },
    {
        "skill_name": "Problem-Solving Steps",
        "category": "cognitive",
        "description": "Structured approach to addressing problems",
        "instructions": "1. Define the problem clearly\n2. Brainstorm all possible solutions\n3. Evaluate pros and cons of each\n4. Choose the best option\n5. Make a plan and take action\n6. Evaluate results",
        "duration_minutes": 20,
        "difficulty_level": 3,
        "effectiveness_situations": ["overwhelm", "indecision", "stress", "conflict"]
    },
    {
        "skill_name": "Self-Compassion Break",
        "category": "cognitive",
        "description": "Treating yourself with kindness during difficult times",
        "instructions": "1. Acknowledge: 'This is a moment of suffering'\n2. Normalize: 'Suffering is part of life'\n3. Offer kindness: 'May I be kind to myself'\n4. Place hands on heart or give yourself a hug\n5. Speak to yourself as you would a good friend",
        "duration_minutes": 5,
        "difficulty_level": 2,
        "effectiveness_situations": ["self-criticism", "shame", "failure", "disappointment"]
    },
    {
        "skill_name": "Values-Based Action",
        "category": "behavioral",
        "description": "Acting in alignment with your core values",
        "instructions": "1. Identify your core values\n2. Ask: 'What would acting on this value look like?'\n3. Choose one small action aligned with that value\n4. Take the action, regardless of mood\n5. Notice the sense of meaning and purpose",
        "duration_minutes": 15,
        "difficulty_level": 3,
        "effectiveness_situations": ["lack of purpose", "depression", "difficult decisions", "low motivation"]
    }
]

def get_user_id():
    """Get current user ID from session"""
    return session.get('user_id') if session else None

# ===== THOUGHT RECORD FUNCTIONS =====

def create_thought_record(user_session, situation: str, automatic_thought: str, 
                         emotion: Optional[str] = None, emotion_intensity: Optional[int] = None) -> Dict:
    """Create a new thought record entry"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        thought_record = CBTThoughtRecord(
            user_id=user_id,
            situation=situation,
            automatic_thought=automatic_thought,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        db.session.add(thought_record)
        db.session.commit()
        
        return {
            "success": True,
            "id": thought_record.id,
            "message": "Thought record created successfully",
            "data": thought_record.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error creating thought record: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

def complete_thought_record(record_id: int, evidence_for: Optional[str] = None, 
                          evidence_against: Optional[str] = None, balanced_thought: Optional[str] = None,
                          new_emotion: Optional[str] = None, new_emotion_intensity: Optional[int] = None) -> Dict:
    """Complete a thought record with cognitive restructuring"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        record = CBTThoughtRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return {"error": "Thought record not found", "success": False}

        # Update the record
        if evidence_for is not None:
            record.evidence_for = evidence_for
        if evidence_against is not None:
            record.evidence_against = evidence_against
        if balanced_thought is not None:
            record.balanced_thought = balanced_thought
        if new_emotion is not None:
            record.new_emotion = new_emotion
        if new_emotion_intensity is not None:
            record.new_emotion_intensity = new_emotion_intensity

        db.session.commit()
        
        return {
            "success": True,
            "message": "Thought record completed successfully",
            "data": record.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error completing thought record: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

def get_thought_records(user_session, limit: int = 10) -> List[Dict]:
    """Get user's thought records"""
    try:
        user_id = get_user_id()
        if not user_id:
            return []

        records = CBTThoughtRecord.query.filter_by(user_id=user_id)\
                                       .order_by(desc(CBTThoughtRecord.created_at))\
                                       .limit(limit).all()
        
        return [record.to_dict() for record in records]
        
    except Exception as e:
        logger.error(f"Error getting thought records: {e}")
        return []

def analyze_thought_patterns(user_session) -> Dict:
    """Analyze user's thought patterns and identify common cognitive biases"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated"}

        # Get recent thought records
        records = CBTThoughtRecord.query.filter_by(user_id=user_id)\
                                       .order_by(desc(CBTThoughtRecord.created_at))\
                                       .limit(50).all()
        
        if not records:
            return {"message": "No thought records found for analysis"}

        # Analyze for cognitive biases using AI
        if OPENROUTER_KEY:
            thoughts = [f"Situation: {r.situation}\nThought: {r.automatic_thought}" 
                       for r in records[:10]]
            
            analysis_prompt = f"""
            Analyze these thought records for common cognitive biases. 
            
            Thoughts to analyze:
            {chr(10).join(thoughts)}
            
            Identify:
            1. The most common cognitive biases present
            2. Recurring thought patterns
            3. Specific recommendations for cognitive restructuring
            
            Provide a compassionate, helpful analysis.
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    max_tokens=800
                )
                
                ai_analysis = response.choices[0].message.content
                
                return {
                    "success": True,
                    "total_records": len(records),
                    "analysis_period": "Last 50 entries",
                    "ai_analysis": ai_analysis
                }
                
            except Exception as e:
                logger.error(f"AI analysis error: {e}")
                return {"error": "AI analysis temporarily unavailable"}
        
        return {
            "success": True,
            "total_records": len(records),
            "message": "Basic analysis completed - AI analysis requires API key"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing thought patterns: {e}")
        return {"error": str(e)}

# ===== COGNITIVE BIAS FUNCTIONS =====

def identify_cognitive_bias(thought_text: str) -> List[Dict]:
    """Identify potential cognitive biases in a thought"""
    identified_biases = []
    
    thought_lower = thought_text.lower()
    
    # Simple keyword-based detection
    bias_keywords = {
        "all_or_nothing": ["always", "never", "completely", "totally", "everyone", "nobody"],
        "catastrophizing": ["disaster", "terrible", "awful", "worst", "horrible", "catastrophe"],
        "mind_reading": ["they think", "he thinks", "she thinks", "everyone thinks"],
        "fortune_telling": ["will never", "always will", "definitely will", "bound to"],
        "should_statements": ["should", "must", "have to", "ought to", "supposed to"],
        "labeling": ["i am a", "i'm a", "he is a", "she is a", "they are"]
    }
    
    for bias_type, keywords in bias_keywords.items():
        if any(keyword in thought_lower for keyword in keywords):
            bias_info = COGNITIVE_BIASES.get(bias_type, {})
            identified_biases.append({
                "bias_type": bias_type,
                "name": bias_info.get("name", bias_type),
                "description": bias_info.get("description", ""),
                "reframe_suggestion": bias_info.get("reframe", "")
            })
    
    return identified_biases

def log_cognitive_bias(user_session, bias_type: str, example_thought: str) -> Dict:
    """Log a cognitive bias occurrence"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        # Check if this bias type already exists for user
        existing_bias = CBTCognitiveBias.query.filter_by(
            user_id=user_id, bias_type=bias_type
        ).first()
        
        if existing_bias:
            # Update existing record
            existing_bias.frequency_count += 1
            existing_bias.last_occurred = datetime.utcnow()
            existing_bias.example_thought = example_thought
        else:
            # Create new record
            bias_info = COGNITIVE_BIASES.get(bias_type, {})
            existing_bias = CBTCognitiveBias(
                user_id=user_id,
                bias_type=bias_type,
                description=bias_info.get("description", ""),
                example_thought=example_thought,
                reframe_suggestion=bias_info.get("reframe", ""),
                frequency_count=1
            )
            db.session.add(existing_bias)
        
        db.session.commit()
        
        return {
            "success": True,
            "message": "Cognitive bias logged successfully",
            "data": existing_bias.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error logging cognitive bias: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

# ===== MOOD TRACKING FUNCTIONS =====

def log_mood(user_session, primary_emotion: str, emotion_intensity: int,
             triggers: Optional[str] = None, thoughts: Optional[str] = None, 
             coping_strategy_used: Optional[str] = None, effectiveness_rating: Optional[int] = None) -> Dict:
    """Log a mood entry"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        mood_log = CBTMoodLog(
            user_id=user_id,
            primary_emotion=primary_emotion,
            emotion_intensity=emotion_intensity,
            triggers=triggers,
            thoughts=thoughts,
            coping_strategy_used=coping_strategy_used,
            effectiveness_rating=effectiveness_rating
        )
        
        db.session.add(mood_log)
        db.session.commit()
        
        return {
            "success": True,
            "message": "Mood logged successfully",
            "data": mood_log.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error logging mood: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

def get_mood_trends(user_session, days: int = 30) -> Dict:
    """Analyze mood trends over time"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated"}

        # Get mood logs from the last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        mood_logs = CBTMoodLog.query.filter(
            and_(CBTMoodLog.user_id == user_id,
                 CBTMoodLog.created_at >= cutoff_date)
        ).order_by(CBTMoodLog.date, CBTMoodLog.time_of_day).all()
        
        if not mood_logs:
            return {"message": f"No mood data found in the last {days} days"}

        # Calculate trends
        emotions = [log.primary_emotion for log in mood_logs if log.primary_emotion]
        intensities = [log.emotion_intensity for log in mood_logs if log.emotion_intensity]
        
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        avg_intensity = sum(intensities) / len(intensities) if intensities else 0
        
        # Identify patterns
        patterns = []
        if avg_intensity > 7:
            patterns.append("High emotional intensity - consider stress management techniques")
        elif avg_intensity < 4:
            patterns.append("Low emotional intensity - consider mood-boosting activities")
        
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        
        return {
            "success": True,
            "period": f"Last {days} days",
            "total_entries": len(mood_logs),
            "average_intensity": round(avg_intensity, 1),
            "most_common_emotion": most_common_emotion,
            "emotion_breakdown": emotion_counts,
            "patterns": patterns,
            "data": [log.to_dict() for log in mood_logs]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing mood trends: {e}")
        return {"error": str(e)}

# ===== COPING SKILLS FUNCTIONS =====

def initialize_default_coping_skills():
    """Initialize default coping skills if they don't exist"""
    try:
        # Check if default skills already exist
        existing_count = CBTCopingSkill.query.filter_by(user_id=None).count()
        if existing_count > 0:
            return  # Already initialized
        
        for skill_data in DEFAULT_COPING_SKILLS:
            skill = CBTCopingSkill(
                user_id=None,  # System skill
                skill_name=skill_data["skill_name"],
                category=skill_data["category"],
                description=skill_data["description"],
                instructions=skill_data["instructions"],
                duration_minutes=skill_data["duration_minutes"],
                difficulty_level=skill_data["difficulty_level"],
                effectiveness_situations=json.dumps(skill_data["effectiveness_situations"]),
                is_custom=False
            )
            db.session.add(skill)
        
        db.session.commit()
        logger.info("Default CBT coping skills initialized")
        
    except Exception as e:
        logger.error(f"Error initializing default coping skills: {e}")
        db.session.rollback()

def get_coping_skills(user_session, category: Optional[str] = None, situation: Optional[str] = None) -> List[Dict]:
    """Get coping skills, optionally filtered by category or situation"""
    try:
        user_id = get_user_id()
        
        # Get both system skills and user's custom skills
        query = CBTCopingSkill.query.filter(
            or_(CBTCopingSkill.user_id == None, CBTCopingSkill.user_id == user_id)
        )
        
        if category:
            query = query.filter(CBTCopingSkill.category == category)
        
        if situation:
            # Filter by situation if provided
            query = query.filter(CBTCopingSkill.effectiveness_situations.contains(situation))
        
        skills = query.order_by(CBTCopingSkill.average_effectiveness.desc()).all()
        
        return [skill.to_dict() for skill in skills]
        
    except Exception as e:
        logger.error(f"Error getting coping skills: {e}")
        return []

def recommend_coping_skill(user_session, situation: str, current_emotion: Optional[str] = None, 
                          intensity: Optional[int] = None) -> Dict:
    """Recommend a coping skill based on current situation and emotion"""
    try:
        # Get relevant skills
        all_skills = get_coping_skills(user_session)
        
        # Simple recommendation logic
        if current_emotion:
            emotion_lower = current_emotion.lower()
            
            # Emotional state-based recommendations
            if any(word in emotion_lower for word in ["anxious", "panic", "worry"]):
                recommended_categories = ["grounding", "relaxation"]
            elif any(word in emotion_lower for word in ["sad", "depressed", "down"]):
                recommended_categories = ["behavioral", "cognitive"]
            elif any(word in emotion_lower for word in ["angry", "frustrated", "irritated"]):
                recommended_categories = ["behavioral", "grounding"]
            else:
                recommended_categories = ["grounding", "cognitive"]
        else:
            recommended_categories = ["grounding", "relaxation"]
        
        # Filter by recommended categories
        recommended_skills = [
            skill for skill in all_skills 
            if skill.get("category") in recommended_categories
        ]
        
        if not recommended_skills:
            recommended_skills = all_skills
        
        # Sort by effectiveness and difficulty
        if intensity and intensity >= 8:
            # High intensity - recommend easier skills
            recommended_skills.sort(key=lambda x: (x.get("difficulty_level", 5), -x.get("average_effectiveness", 0)))
        else:
            # Normal intensity - balance effectiveness and difficulty
            recommended_skills.sort(key=lambda x: -x.get("average_effectiveness", 0))
        
        top_skill = recommended_skills[0] if recommended_skills else None
        
        return {
            "success": True,
            "recommended_skill": top_skill,
            "alternative_skills": recommended_skills[1:4],  # Next 3 options
            "total_available": len(all_skills)
        }
        
    except Exception as e:
        logger.error(f"Error recommending coping skill: {e}")
        return {"error": str(e)}

def log_skill_usage(user_session, skill_id: int, situation: Optional[str] = None,
                   mood_before: Optional[int] = None, mood_after: Optional[int] = None,
                   effectiveness_rating: Optional[int] = None, duration_used: Optional[int] = None,
                   notes: Optional[str] = None) -> Dict:
    """Log usage of a coping skill"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        # Verify skill exists
        skill = CBTCopingSkill.query.get(skill_id)
        if not skill:
            return {"error": "Skill not found", "success": False}

        # Log the usage
        usage = CBTSkillUsage(
            user_id=user_id,
            skill_id=skill_id,
            situation=situation,
            mood_before=mood_before,
            mood_after=mood_after,
            effectiveness_rating=effectiveness_rating,
            duration_used=duration_used,
            notes=notes
        )
        
        db.session.add(usage)
        
        # Update skill statistics
        skill.usage_count += 1
        if effectiveness_rating:
            # Update average effectiveness
            if skill.average_effectiveness == 0:
                skill.average_effectiveness = effectiveness_rating
            else:
                # Simple moving average
                skill.average_effectiveness = (skill.average_effectiveness + effectiveness_rating) / 2
        
        db.session.commit()
        
        return {
            "success": True,
            "message": "Skill usage logged successfully",
            "data": usage.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error logging skill usage: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

# ===== BEHAVIORAL EXPERIMENT FUNCTIONS =====

def create_behavior_experiment(user_session, belief_to_test: str, experiment_description: str,
                             predicted_outcome: Optional[str] = None, confidence_before: Optional[int] = None,
                             planned_date: Optional[str] = None) -> Dict:
    """Create a new behavioral experiment"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        experiment = CBTBehaviorExperiment(
            user_id=user_id,
            belief_to_test=belief_to_test,
            experiment_description=experiment_description,
            predicted_outcome=predicted_outcome,
            confidence_before=confidence_before,
            planned_date=datetime.strptime(planned_date, "%Y-%m-%d").date() if planned_date else None
        )
        
        db.session.add(experiment)
        db.session.commit()
        
        return {
            "success": True,
            "message": "Behavioral experiment created successfully",
            "data": experiment.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error creating behavioral experiment: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

def complete_behavior_experiment(experiment_id: int, actual_outcome: str,
                               confidence_after: Optional[int] = None, lessons_learned: Optional[str] = None) -> Dict:
    """Complete a behavioral experiment with results"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        experiment = CBTBehaviorExperiment.query.filter_by(
            id=experiment_id, user_id=user_id
        ).first()
        
        if not experiment:
            return {"error": "Experiment not found", "success": False}

        experiment.actual_outcome = actual_outcome
        experiment.confidence_after = confidence_after
        experiment.lessons_learned = lessons_learned
        experiment.status = "completed"
        experiment.completed_date = date.today()
        
        db.session.commit()
        
        return {
            "success": True,
            "message": "Behavioral experiment completed successfully",
            "data": experiment.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error completing behavioral experiment: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

# ===== ACTIVITY SCHEDULING FUNCTIONS =====

def schedule_activity(user_session, activity_name: str, category: str, scheduled_date: str,
                     scheduled_time: Optional[str] = None, duration_minutes: Optional[int] = None,
                     difficulty_level: Optional[int] = None, predicted_mood: Optional[int] = None) -> Dict:
    """Schedule a behavioral activation activity"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        activity = CBTActivitySchedule(
            user_id=user_id,
            activity_name=activity_name,
            category=category,
            scheduled_date=datetime.strptime(scheduled_date, "%Y-%m-%d").date(),
            scheduled_time=datetime.strptime(scheduled_time, "%H:%M").time() if scheduled_time else None,
            duration_minutes=duration_minutes,
            difficulty_level=difficulty_level,
            predicted_mood=predicted_mood
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return {
            "success": True,
            "message": "Activity scheduled successfully",
            "data": activity.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error scheduling activity: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

def complete_activity(activity_id: int, actual_mood_before: Optional[int] = None,
                     actual_mood_after: Optional[int] = None, completion_status: str = "completed",
                     notes: Optional[str] = None) -> Dict:
    """Mark an activity as completed with mood ratings"""
    try:
        user_id = get_user_id()
        if not user_id:
            return {"error": "User not authenticated", "success": False}

        activity = CBTActivitySchedule.query.filter_by(
            id=activity_id, user_id=user_id
        ).first()
        
        if not activity:
            return {"error": "Activity not found", "success": False}

        activity.actual_mood_before = actual_mood_before
        activity.actual_mood_after = actual_mood_after
        activity.completion_status = completion_status
        activity.notes = notes
        
        db.session.commit()
        
        return {
            "success": True,
            "message": "Activity completed successfully",
            "data": activity.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error completing activity: {e}")
        db.session.rollback()
        return {"error": str(e), "success": False}

# ===== AI-POWERED CBT ASSISTANCE =====

def cbt_ai_assistant(user_input: str, context: str = "general") -> Dict:
    """AI-powered CBT assistance and guidance"""
    if not OPENROUTER_KEY:
        return {"error": "AI assistance requires API key configuration"}
    
    try:
        # Context-specific prompts
        system_prompts = {
            "thought_challenging": """You are a skilled CBT therapist assistant. Help the user examine their thought using the CBT thought challenging technique. Guide them through:
1. Identifying the specific thought
2. Examining evidence for and against the thought
3. Considering alternative perspectives
4. Developing a more balanced thought
Be compassionate, non-judgmental, and use Socratic questioning.""",
            
            "cognitive_biases": """You are a CBT expert specializing in cognitive biases. Help the user identify potential cognitive distortions in their thinking and provide gentle guidance on reframing. Focus on education and self-discovery rather than telling them what to think.""",
            
            "coping_skills": """You are a CBT skills trainer. Provide specific, actionable coping strategies based on the user's situation. Offer step-by-step instructions and explain why each technique might be helpful.""",
            
            "behavioral_activation": """You are a behavioral activation specialist. Help the user identify meaningful activities that align with their values and could improve their mood. Focus on small, achievable steps.""",
            
            "general": """You are a compassionate CBT assistant. Provide supportive, evidence-based guidance using CBT principles. Remember that you are not providing therapy, but educational support and skills training."""
        }
        
        system_prompt = system_prompts.get(context, system_prompts["general"])
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "success": True,
            "response": ai_response,
            "context": context
        }
        
    except Exception as e:
        logger.error(f"CBT AI assistant error: {e}")
        return {"error": "AI assistant temporarily unavailable"}

# Initialize default coping skills on module import
try:
    initialize_default_coping_skills()
except Exception as e:
    logger.error(f"Error initializing CBT module: {e}")