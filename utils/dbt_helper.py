import os
import logging
import requests
import json
from flask import session
from datetime import datetime
from models import (
    db, DBTSkillLog, DBTDiaryCard, DBTSkillCategory, 
    DBTSkillRecommendation, DBTSkillChallenge, DBTCrisisResource, DBTEmotionTrack
)

# Helper functions for DBT chatbot functionality

# OpenRouter API configuration
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model configuration for different tasks to balance quality and cost
MODELS = {
    # High-capability models for complex reasoning tasks
    "high_capability": "gpt-4o",  # Best quality for complex tasks
    
    # Medium-capability models for standard tasks
    "medium_capability": "gpt-4o-mini",  # Good balance of quality and cost
    
    # Lower-cost models for simpler tasks
    "basic_capability": "meta-llama/llama-3-8b-instruct",  # Cost-effective for simple tasks
    
    # Default model if none specified
    "default": "gpt-4o-mini"
}

# Check OpenRouter availability
if not OPENROUTER_KEY:
    logging.warning("No OpenRouter API key found. AI features will be limited.")

# ——— DETAILED PROMPT TEMPLATES ———
PROMPTS = {
    "skills_on_demand": """
You are a compassionate DBT coach. The user says: "{text}"
1. Identify the single DBT skill most fitting for their need.
2. Explain why this skill matches their situation (1–2 sentences).
3. Provide clear, step-by-step instructions on how to do it, referencing core DBT principles briefly.
""",

    "diary_card": """
You are an expert DBT diary card generator. Based on the user's description: "{text}"
Produce a structured diary card entry including:
- Date (today's date)
- Mood rating (0–5)
- Triggers they noted
- Urges they felt
- DBT skill they used (if any)
- A short reflective note (1–2 sentences)
""",

    "validate": """
You are skilled in DBT validation. The user shares: "{text}"
1. Mirror back their feelings ("It makes sense…").
2. Normalize why it's valid to feel that way.
3. End with a brief empathic statement of support.
""",

    "distress": """
The user is in crisis and needs a Distress Tolerance skill. They say: "{text}"
Guide them through the TIPP skill:
- Temperature: how to safely change body temperature
- Intense exercise: quick movement suggestion
- Paced breathing: steps and timing
- Progressive muscle relaxation: brief walkthrough
Keep it concise and actionable.
""",

    "chain_analysis": """
You are guiding a DBT chain analysis. The user describes a behavior: "{text}"
Ask one question at a time in this order:
1. Vulnerability factors
2. Prompting event
3. Interpretation
4. Emotions
5. Body sensations
6. Actions
7. Consequences
After each question, wait for their response before proceeding.
""",

    "wise_mind": """
Help the user access Wise Mind. They share: "{text}"
1. Ask what their emotional mind says.
2. Ask what their rational mind says.
3. Guide them to merge both into a balanced Wise Mind statement.
""",

    "radical_acceptance": """
Detect resistance to reality in: "{text}"
1. Define radical acceptance.
2. Provide empathic examples.
3. Invite them to try saying "I accept…" about the unchangeable fact.
4. Offer a brief mantra or phrase to practice.
""",

    "interpersonal": """
User scenario: "{text}"
Coach them through the DEAR MAN skill:
- Describe the situation
- Express feelings
- Assert needs
- Reinforce positive outcome
- Remain Mindful
- Appear confident
- Negotiate if needed
Provide a filled-in message example.
""",

    "dialectic": """
User statement: "{text}"
1. Acknowledge the truth in their perspective.
2. Offer the valid counter-truth.
3. Synthesize both into one balanced dialectical statement.
""",

    "trigger_map": """
User shared: "{text}"
1. Identify potential trigger patterns.
2. Explain how these triggers might connect to emotional responses.
3. Recommend a targeted DBT skill to cope with this specific trigger pattern.
""",

    "skill_of_day": """
You are a DBT coach delivering a daily skill:
1. Name one important DBT skill.
2. Explain its purpose (1–2 sentences).
3. Give a one-sentence challenge to practice it today.
""",

    "edit_message": """
Edit the user's message to weave in {target_skill} and a {tone} tone.
Original message:
\"\"\"
{original}
\"\"\"
Ensure it:
- Reflects DBT skill principles
- Validates emotion
- Maintains clarity and intent
""",

    "advise": """
User situation: "{text}"
1. Validate their experience.
2. Recommend specific DBT skills to apply.
3. Offer concrete next steps (1–3 bullet points).
"""
}


def call_router(prompt_key, capability_level="medium_capability", **kwargs):
    """
    Call OpenRouter with the specified prompt and arguments
    
    Args:
        prompt_key: Key to select the prompt template from PROMPTS
        capability_level: Level of model capability required for task
                        ("high_capability", "medium_capability", "basic_capability")
        **kwargs: Arguments to format the prompt template
        
    Returns:
        dict: Response from the language model or error message
    """
    if not OPENROUTER_KEY:
        return {"error": "OpenRouter API key not configured"}
        
    try:
        # Format the prompt with the provided arguments
        prompt = PROMPTS[prompt_key].format(**kwargs)
        
        # Select appropriate model based on task complexity
        model = MODELS.get(capability_level, MODELS["default"])
        
        # Prepare the request
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nous.chat",  # Identify your application
            "X-Title": "NOUS DBT Assistant"  # Add context about your application
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000  # Adjust based on expected response length
        }
        
        # Call the API
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=data,
            timeout=30  # Set a reasonable timeout
        )
        
        # Check for errors and handle them appropriately
        if response.status_code != 200:
            error_message = f"OpenRouter API error: {response.status_code}"
            try:
                error_detail = response.json()
                error_message += f" - {error_detail.get('error', {}).get('message', '')}"
            except:
                pass
                
            logging.error(error_message)
            
            # If we get a 429 or 500+ error, try with a simpler model
            if response.status_code in [429] or response.status_code >= 500:
                if capability_level != "basic_capability":
                    logging.info(f"Rate limited or server error, trying with basic capability model")
                    return call_router(prompt_key, "basic_capability", **kwargs)
            
            return {"error": error_message}
            
        # Parse the successful response
        result = response.json()
        
        if not result.get("choices"):
            logging.error("No response from LLM")
            return {"error": "No response received from language model"}
            
        return {"response": result["choices"][0]["message"]["content"].strip()}
        
    except Exception as e:
        logging.error(f"Error calling OpenRouter: {str(e)}")
        # Attempt fallback to a different model if available
        if capability_level != "basic_capability":
            logging.info(f"Attempting fallback to basic capability model")
            return call_router(prompt_key, "basic_capability", **kwargs)
        return {"error": f"Error: {str(e)}"}


# Database interaction functions

def log_dbt_skill(session_obj, skill_name, category, situation=None, effectiveness=None, notes=None):
    """
    Log a DBT skill usage
    
    Args:
        session_obj: Flask session object
        skill_name: Name of the skill used
        category: Category of the skill (from DBTSkillCategory)
        situation: Description of when/how the skill was used
        effectiveness: Rating from 1-5 of how effective the skill was
        notes: Additional notes
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
        
        # Create a new skill log entry
        skill_log = DBTSkillLog()
        skill_log.user_id = user_id
        skill_log.skill_name = skill_name
        skill_log.category = category
        skill_log.situation = situation
        skill_log.effectiveness = effectiveness
        skill_log.notes = notes
        skill_log.created_at = datetime.utcnow()
        
        db.session.add(skill_log)
        db.session.commit()
        
        return {"status": "success", "message": f"Skill '{skill_name}' logged successfully", "id": skill_log.id}
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error logging DBT skill: {str(e)}")
        return {"status": "error", "message": f"Error logging skill: {str(e)}"}


def get_skill_logs(session_obj, limit=10):
    """
    Get recent DBT skill logs for the user
    
    Args:
        session_obj: Flask session object
        limit: Maximum number of logs to retrieve
        
    Returns:
        list: List of skill logs
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return []
        
        logs = DBTSkillLog.query.filter_by(user_id=user_id)\
            .order_by(DBTSkillLog.created_at.desc())\
            .limit(limit).all()
            
        return [log.to_dict() for log in logs]
    
    except Exception as e:
        logging.error(f"Error retrieving DBT skill logs: {str(e)}")
        return []


def create_diary_card(session_obj, mood_rating, triggers=None, urges=None, skills_used=None, reflection=None):
    """
    Create a new DBT diary card
    
    Args:
        session_obj: Flask session object
        mood_rating: Rating from 0-5
        triggers: What triggered emotions
        urges: Urges felt
        skills_used: Skills used
        reflection: Reflection notes
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
        
        # Create a new diary card
        diary_card = DBTDiaryCard()
        diary_card.user_id = user_id
        diary_card.date = datetime.utcnow().date()
        diary_card.mood_rating = mood_rating
        diary_card.triggers = triggers
        diary_card.urges = urges
        diary_card.skills_used = skills_used
        diary_card.reflection = reflection
        diary_card.created_at = datetime.utcnow()
        
        db.session.add(diary_card)
        db.session.commit()
        
        return {"status": "success", "message": "Diary card created successfully", "id": diary_card.id}
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating DBT diary card: {str(e)}")
        return {"status": "error", "message": f"Error creating diary card: {str(e)}"}


def get_diary_cards(session_obj, limit=10):
    """
    Get recent DBT diary cards for the user
    
    Args:
        session_obj: Flask session object
        limit: Maximum number of cards to retrieve
        
    Returns:
        list: List of diary cards
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return []
        
        cards = DBTDiaryCard.query.filter_by(user_id=user_id)\
            .order_by(DBTDiaryCard.date.desc())\
            .limit(limit).all()
            
        return [card.to_dict() for card in cards]
    
    except Exception as e:
        logging.error(f"Error retrieving DBT diary cards: {str(e)}")
        return []


# === Personalized Skill Recommendations ===

def analyze_skill_effectiveness(session_obj):
    """
    Analyze the effectiveness of skills the user has logged
    and update recommendations accordingly
    
    Args:
        session_obj: Flask session object
        
    Returns:
        dict: Summary of analysis
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
        
        # Get all skill logs for user
        skill_logs = DBTSkillLog.query.filter_by(user_id=user_id)\
            .order_by(DBTSkillLog.created_at.desc()).all()
            
        if not skill_logs:
            return {"status": "info", "message": "Not enough skill data for analysis"}
            
        # Group by skill name and category, calculate average effectiveness
        skill_stats = {}
        for log in skill_logs:
            key = f"{log.skill_name}|{log.category}"
            if key not in skill_stats:
                skill_stats[key] = {
                    "skill_name": log.skill_name,
                    "category": log.category,
                    "total_effectiveness": 0,
                    "count": 0,
                    "effectiveness_ratings": [],
                    "situations": []
                }
            
            if log.effectiveness:
                skill_stats[key]["total_effectiveness"] += log.effectiveness
                skill_stats[key]["count"] += 1
                skill_stats[key]["effectiveness_ratings"].append(log.effectiveness)
            
            if log.situation:
                skill_stats[key]["situations"].append(log.situation)
        
        # Calculate averages and update/create recommendations
        updated_count = 0
        for key, stats in skill_stats.items():
            if stats["count"] == 0:
                continue
                
            avg_effectiveness = stats["total_effectiveness"] / stats["count"]
            confidence_score = min(0.4 + (stats["count"] * 0.1), 0.95)  # More uses = higher confidence
            
            # Extract common situation types using AI
            situation_types = extract_situation_types(stats["situations"]) if stats["situations"] else ["general"]
            
            # Update recommendations for each situation type
            for situation_type in situation_types:
                # Check if recommendation already exists
                recommendation = DBTSkillRecommendation.query.filter_by(
                    user_id=user_id,
                    skill_name=stats["skill_name"],
                    situation_type=situation_type
                ).first()
                
                if recommendation:
                    # Update existing recommendation
                    recommendation.avg_effectiveness = avg_effectiveness
                    recommendation.times_used = stats["count"]
                    recommendation.confidence_score = confidence_score
                    recommendation.updated_at = datetime.utcnow()
                else:
                    # Create new recommendation
                    recommendation = DBTSkillRecommendation()
                    recommendation.user_id = user_id
                    recommendation.skill_name = stats["skill_name"]
                    recommendation.category = stats["category"]
                    recommendation.situation_type = situation_type
                    recommendation.avg_effectiveness = avg_effectiveness
                    recommendation.times_used = stats["count"]
                    recommendation.confidence_score = confidence_score
                    recommendation.created_at = datetime.utcnow()
                    recommendation.updated_at = datetime.utcnow()
                    
                    db.session.add(recommendation)
                
                updated_count += 1
        
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Updated {updated_count} skill recommendations",
            "skill_count": len(skill_stats)
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error analyzing skill effectiveness: {str(e)}")
        return {"status": "error", "message": f"Error analyzing skills: {str(e)}"}


def extract_situation_types(situations, max_types=3):
    """
    Use AI to extract common situation types from user's situations
    
    Args:
        situations: List of situation descriptions
        max_types: Maximum number of situation types to extract
        
    Returns:
        list: Common situation types
    """
    if not situations:
        return ["general"]
        
    try:
        # Prepare text for AI analysis
        combined_text = "\n".join(situations[:10])  # Limit to 10 situations to avoid token limits
        
        prompt = f"""
        Based on the following descriptions of situations in which DBT skills were used,
        identify the most common {max_types} situation types or triggers.
        Provide your answer as a comma-separated list of short phrases (2-3 words each).
        
        Example categories: interpersonal conflict, emotion regulation, distress tolerance,
        anxiety triggers, rejection sensitivity, self-criticism, etc.
        
        Situations:
        {combined_text}
        
        Respond with ONLY the comma-separated list, no additional text.
        """
        
        response = call_router_direct(prompt)
        
        if not response or "error" in response:
            return ["general"]
            
        # Parse the response
        situation_types = [
            s.strip().lower() for s in response.split(",")
            if len(s.strip()) > 0
        ]
        
        # Limit to max_types
        return situation_types[:max_types]
        
    except Exception as e:
        logging.error(f"Error extracting situation types: {str(e)}")
        return ["general"]


def call_router_direct(prompt, capability_level="medium_capability"):
    """
    Simple version of call_router for internal use
    
    Args:
        prompt: The prompt to send to the model
        capability_level: Level of model capability required for task
        
    Returns:
        str: Model response text or None if failed
    """
    if not OPENROUTER_KEY:
        return None
        
    try:
        # Select appropriate model based on task complexity
        model = MODELS.get(capability_level, MODELS["default"])
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nous.chat",
            "X-Title": "NOUS DBT Assistant"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            logging.warning(f"OpenRouter API error: {response.status_code}")
            
            # Try with a simpler model if we hit rate limits or server errors
            if (response.status_code in [429] or response.status_code >= 500) and capability_level != "basic_capability":
                logging.info("Attempting fallback to basic capability model")
                return call_router_direct(prompt, "basic_capability")
                
            return None
            
        result = response.json()
        
        if not result.get("choices"):
            return None
            
        return result["choices"][0]["message"]["content"].strip()
        
    except Exception as e:
        logging.error(f"Error in direct router call: {str(e)}")
        # Try with a simpler model if we encounter an error
        if capability_level != "basic_capability":
            logging.info("Attempting fallback to basic capability model after exception")
            return call_router_direct(prompt, "basic_capability")
        return None


def get_skill_recommendations(session_obj, situation_description=None, limit=5):
    """
    Get personalized skill recommendations based on past effectiveness
    
    Args:
        session_obj: Flask session object
        situation_description: Description of the current situation
        limit: Maximum number of recommendations to return
        
    Returns:
        list: Recommended skills
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return []
        
        # If we have a situation description, try to match it to known situation types
        if situation_description:
            situation_type = identify_situation_type(situation_description)
            
            # First try to get recommendations specific to this situation type
            recommendations = DBTSkillRecommendation.query.filter_by(
                user_id=user_id,
                situation_type=situation_type
            ).order_by(
                DBTSkillRecommendation.avg_effectiveness.desc(),
                DBTSkillRecommendation.confidence_score.desc()
            ).limit(limit).all()
            
            # If not enough recommendations, supplement with generic ones
            if len(recommendations) < limit:
                additional_count = limit - len(recommendations)
                additional_recs = DBTSkillRecommendation.query.filter_by(
                    user_id=user_id
                ).filter(
                    DBTSkillRecommendation.situation_type != situation_type
                ).order_by(
                    DBTSkillRecommendation.avg_effectiveness.desc()
                ).limit(additional_count).all()
                
                recommendations.extend(additional_recs)
        else:
            # If no situation provided, return top recommendations overall
            recommendations = DBTSkillRecommendation.query.filter_by(
                user_id=user_id
            ).order_by(
                DBTSkillRecommendation.avg_effectiveness.desc(),
                DBTSkillRecommendation.confidence_score.desc()
            ).limit(limit).all()
        
        # If user has no recommendation history, return some predefined defaults
        if not recommendations:
            return get_default_recommendations()
            
        return [rec.to_dict() for rec in recommendations]
        
    except Exception as e:
        logging.error(f"Error getting skill recommendations: {str(e)}")
        return get_default_recommendations()


def identify_situation_type(situation_description):
    """
    Use AI to identify the situation type from a description
    
    Args:
        situation_description: Description of the situation
        
    Returns:
        str: Identified situation type
    """
    try:
        prompt = f"""
        Based on this description of a situation:
        "{situation_description}"
        
        Identify the most fitting DBT situation type or trigger category.
        Provide your answer as a single short phrase (2-3 words).
        
        Example categories: interpersonal conflict, emotion regulation, distress tolerance,
        anxiety triggers, rejection sensitivity, self-criticism, etc.
        
        Respond with ONLY the category phrase, no additional text.
        """
        
        response = call_router_direct(prompt)
        
        if not response:
            return "general"
            
        # Clean up the response
        situation_type = response.strip().lower()
        
        # Limit length
        if len(situation_type) > 100:
            situation_type = situation_type[:100]
            
        return situation_type
        
    except Exception as e:
        logging.error(f"Error identifying situation type: {str(e)}")
        return "general"


def get_default_recommendations():
    """Return a list of default skill recommendations"""
    return [
        {
            'skill_name': 'Mindfulness',
            'category': 'Mindfulness',
            'situation_type': 'general',
            'confidence_score': 0.5,
            'avg_effectiveness': 4.0
        },
        {
            'skill_name': 'TIPP Skills',
            'category': 'Distress Tolerance',
            'situation_type': 'crisis',
            'confidence_score': 0.5,
            'avg_effectiveness': 4.2
        },
        {
            'skill_name': 'DEAR MAN',
            'category': 'Interpersonal Effectiveness',
            'situation_type': 'interpersonal conflict',
            'confidence_score': 0.5,
            'avg_effectiveness': 3.8
        },
        {
            'skill_name': 'Opposite Action',
            'category': 'Emotion Regulation',
            'situation_type': 'intense emotions',
            'confidence_score': 0.5,
            'avg_effectiveness': 3.9
        },
        {
            'skill_name': 'Radical Acceptance',
            'category': 'Distress Tolerance',
            'situation_type': 'unchangeable situation',
            'confidence_score': 0.5,
            'avg_effectiveness': 4.1
        }
    ]


# === DBT Skill Challenges ===

def get_available_challenges(session_obj, category=None):
    """
    Get available skill challenges for the user
    
    Args:
        session_obj: Flask session object
        category: Optional category filter
        
    Returns:
        list: Available challenges
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return []
        
        query = DBTSkillChallenge.query.filter_by(user_id=user_id)
        
        if category:
            query = query.filter_by(skill_category=category)
            
        challenges = query.order_by(
            DBTSkillChallenge.is_completed,
            DBTSkillChallenge.difficulty
        ).all()
        
        if not challenges:
            # If no challenges yet, create some defaults
            create_default_challenges(session_obj)
            
            # Query again
            query = DBTSkillChallenge.query.filter_by(user_id=user_id)
            if category:
                query = query.filter_by(skill_category=category)
                
            challenges = query.order_by(
                DBTSkillChallenge.is_completed,
                DBTSkillChallenge.difficulty
            ).all()
        
        return [challenge.to_dict() for challenge in challenges]
        
    except Exception as e:
        logging.error(f"Error getting skill challenges: {str(e)}")
        return []


def create_challenge(session_obj, name, description, category, difficulty=1):
    """
    Create a new skill challenge
    
    Args:
        session_obj: Flask session object
        name: Challenge name
        description: Challenge description
        category: Skill category from DBTSkillCategory
        difficulty: Difficulty level (1-5)
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
            
        # Check if challenge with same name already exists
        existing = DBTSkillChallenge.query.filter_by(
            user_id=user_id,
            challenge_name=name
        ).first()
        
        if existing:
            return {"status": "error", "message": f"Challenge '{name}' already exists"}
            
        # Create new challenge
        challenge = DBTSkillChallenge()
        challenge.user_id = user_id
        challenge.challenge_name = name
        challenge.description = description
        challenge.skill_category = category
        challenge.difficulty = min(max(difficulty, 1), 5)  # Ensure 1-5 range
        challenge.is_completed = False
        challenge.progress = 0
        challenge.start_date = datetime.utcnow()
        challenge.created_at = datetime.utcnow()
        
        db.session.add(challenge)
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Challenge '{name}' created successfully",
            "id": challenge.id
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating skill challenge: {str(e)}")
        return {"status": "error", "message": f"Error creating challenge: {str(e)}"}


def update_challenge_progress(session_obj, challenge_id, progress):
    """
    Update a challenge's progress
    
    Args:
        session_obj: Flask session object
        challenge_id: ID of the challenge
        progress: Progress percentage (0-100)
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
            
        # Find the challenge
        challenge = DBTSkillChallenge.query.filter_by(
            id=challenge_id,
            user_id=user_id
        ).first()
        
        if not challenge:
            return {"status": "error", "message": "Challenge not found"}
            
        # Update progress
        progress = min(max(progress, 0), 100)  # Ensure 0-100 range
        challenge.progress = progress
        
        # Mark as completed if 100%
        if progress == 100:
            challenge.is_completed = True
            challenge.completed_date = datetime.utcnow()
            
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Challenge progress updated to {progress}%",
            "completed": challenge.is_completed
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating challenge progress: {str(e)}")
        return {"status": "error", "message": f"Error updating progress: {str(e)}"}


def mark_challenge_completed(session_obj, challenge_id):
    """
    Mark a challenge as completed
    
    Args:
        session_obj: Flask session object
        challenge_id: ID of the challenge
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
            
        # Find the challenge
        challenge = DBTSkillChallenge.query.filter_by(
            id=challenge_id,
            user_id=user_id
        ).first()
        
        if not challenge:
            return {"status": "error", "message": "Challenge not found"}
            
        # Mark as completed
        challenge.is_completed = True
        challenge.progress = 100
        challenge.completed_date = datetime.utcnow()
            
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Challenge '{challenge.challenge_name}' marked as completed"
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error completing challenge: {str(e)}")
        return {"status": "error", "message": f"Error completing challenge: {str(e)}"}


def reset_challenge(session_obj, challenge_id):
    """
    Reset a challenge to start again
    
    Args:
        session_obj: Flask session object
        challenge_id: ID of the challenge
        
    Returns:
        dict: Status of the operation
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
            
        # Find the challenge
        challenge = DBTSkillChallenge.query.filter_by(
            id=challenge_id,
            user_id=user_id
        ).first()
        
        if not challenge:
            return {"status": "error", "message": "Challenge not found"}
            
        # Reset challenge
        challenge.is_completed = False
        challenge.progress = 0
        challenge.start_date = datetime.utcnow()
        challenge.completed_date = None
            
        db.session.commit()
        
        return {
            "status": "success", 
            "message": f"Challenge '{challenge.challenge_name}' has been reset"
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error resetting challenge: {str(e)}")
        return {"status": "error", "message": f"Error resetting challenge: {str(e)}"}


def create_default_challenges(session_obj):
    """
    Create a set of default skill challenges for a new user
    
    Args:
        session_obj: Flask session object
        
    Returns:
        int: Number of challenges created
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return 0
            
        # Check if user already has challenges
        existing = DBTSkillChallenge.query.filter_by(user_id=user_id).count()
        if existing > 0:
            return 0  # Don't create defaults if user already has challenges
            
        # Default challenges
        default_challenges = [
            # Mindfulness challenges
            {
                "name": "One-Minute Mindfulness",
                "description": "Practice mindfulness for just one minute, 3 times today. Focus on your breath and notice when your mind wanders.",
                "category": "Mindfulness",
                "difficulty": 1
            },
            {
                "name": "Mindful Tea/Coffee",
                "description": "Drink a cup of tea or coffee mindfully, paying attention to the temperature, taste, and sensations.",
                "category": "Mindfulness",
                "difficulty": 1
            },
            {
                "name": "5 Senses Observation",
                "description": "Notice 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
                "category": "Mindfulness",
                "difficulty": 2
            },
            
            # Distress Tolerance challenges
            {
                "name": "TIPP Skill Practice",
                "description": "Next time you feel emotionally overwhelmed, use the TIPP skill: Temperature change (cold water on face), Intense exercise, Paced breathing, and Progressive muscle relaxation.",
                "category": "Distress Tolerance",
                "difficulty": 2
            },
            {
                "name": "Radical Acceptance Journal",
                "description": "Write about something you're struggling to accept. Practice saying 'I accept that...' even though you don't like it.",
                "category": "Distress Tolerance",
                "difficulty": 3
            },
            {
                "name": "Self-Soothe Kit",
                "description": "Create a self-soothe kit with items that appeal to your five senses - something to see, touch, hear, smell, and taste that brings comfort.",
                "category": "Distress Tolerance",
                "difficulty": 2
            },
            
            # Emotion Regulation challenges
            {
                "name": "Opposite Action",
                "description": "Identify an emotion that isn't helpful in a situation, then do the opposite action. For example, if feeling withdrawn, reach out to someone.",
                "category": "Emotion Regulation",
                "difficulty": 3
            },
            {
                "name": "Emotion Name It to Tame It",
                "description": "When you feel an intense emotion, name it specifically (not just 'bad' or 'upset'). Notice how naming it affects the intensity.",
                "category": "Emotion Regulation",
                "difficulty": 2
            },
            {
                "name": "PLEASE Skills Day",
                "description": "For one day, follow all the PLEASE skills: treat PhysicaL illness, Eat balanced, Avoid mood-altering substances, Sleep balanced, Exercise.",
                "category": "Emotion Regulation",
                "difficulty": 4
            },
            
            # Interpersonal Effectiveness challenges
            {
                "name": "DEAR MAN Practice",
                "description": "Use the DEAR MAN skill (Describe, Express, Assert, Reinforce, stay Mindful, Appear confident, Negotiate) in a conversation where you need to ask for something.",
                "category": "Interpersonal Effectiveness",
                "difficulty": 4
            },
            {
                "name": "Validation Practice",
                "description": "In three different conversations today, practice validating the other person's feelings or perspective before sharing your own.",
                "category": "Interpersonal Effectiveness",
                "difficulty": 3
            },
            {
                "name": "FAST Self-Respect",
                "description": "In a challenging interaction, practice the FAST skills: be Fair, no Apologies for existing, Stick to values, be Truthful.",
                "category": "Interpersonal Effectiveness",
                "difficulty": 3
            }
        ]
        
        # Create each challenge
        created_count = 0
        for challenge in default_challenges:
            new_challenge = DBTSkillChallenge()
            new_challenge.user_id = user_id
            new_challenge.challenge_name = challenge["name"]
            new_challenge.description = challenge["description"]
            new_challenge.skill_category = challenge["category"]
            new_challenge.difficulty = challenge["difficulty"]
            new_challenge.is_completed = False
            new_challenge.progress = 0
            new_challenge.start_date = datetime.utcnow()
            new_challenge.created_at = datetime.utcnow()
            
            db.session.add(new_challenge)
            created_count += 1
            
        db.session.commit()
        return created_count
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating default challenges: {str(e)}")
        return 0


def generate_personalized_challenge(session_obj, category=None):
    """
    Generate a personalized skill challenge based on user's skill history
    
    Args:
        session_obj: Flask session object
        category: Optional specific category to focus on
        
    Returns:
        dict: Generated challenge details
    """
    try:
        user_id = session_obj.get("user_id")
        if not user_id:
            return {"status": "error", "message": "User not logged in"}
        
        # If category is not specified, determine best category 
        # based on user's least practiced skills
        if not category:
            # Count skill logs by category
            category_counts = {}
            for cat in [c.value for c in DBTSkillCategory]:
                count = DBTSkillLog.query.filter_by(
                    user_id=user_id,
                    category=cat
                ).count()
                category_counts[cat] = count
            
            # Find the least used category (or random if all equal)
            if category_counts:
                min_count = min(category_counts.values())
                min_categories = [cat for cat, count in category_counts.items() 
                                if count == min_count]
                if min_categories:
                    import random
                    category = random.choice(min_categories)
        
        # Generate a custom challenge with AI
        challenge = generate_challenge_with_ai(category)
        
        if not challenge:
            return {"status": "error", "message": "Could not generate a challenge"}
            
        # Save the generated challenge
        result = create_challenge(
            session_obj,
            challenge["name"],
            challenge["description"],
            challenge["category"],
            challenge["difficulty"]
        )
        
        if result["status"] != "success":
            return result
            
        return {
            "status": "success",
            "message": "New personalized challenge created",
            "challenge": challenge,
            "id": result["id"]
        }
        
    except Exception as e:
        logging.error(f"Error generating personalized challenge: {str(e)}")
        return {"status": "error", "message": f"Error generating challenge: {str(e)}"}


def generate_challenge_with_ai(category=None):
    """
    Use AI to generate a skill challenge
    
    Args:
        category: Optional skill category to focus on
        
    Returns:
        dict: Challenge details
    """
    try:
        category_text = f"in the '{category}' category" if category else "in any DBT skill category"
        
        prompt = f"""
        Create a new DBT skill practice challenge {category_text}.
        
        Respond with a JSON object in this format:
        {{
            "name": "Short challenge name (3-5 words)",
            "description": "Detailed description of the challenge (2-3 sentences)",
            "category": "The DBT skill category (Mindfulness, Distress Tolerance, Emotion Regulation, or Interpersonal Effectiveness)",
            "difficulty": A number from 1-5 (1=easiest, 5=hardest)
        }}
        
        Make the challenge specific, actionable, and something that can be completed in 1-3 days.
        """
        
        response = call_router_direct(prompt)
        
        if not response:
            return None
        
        try:
            challenge = json.loads(response)
            
            # Validate required fields
            required = ["name", "description", "category", "difficulty"]
            for field in required:
                if field not in challenge:
                    return None
                    
            # Ensure difficulty is in range
            if not isinstance(challenge["difficulty"], int):
                challenge["difficulty"] = int(float(challenge["difficulty"]))
                
            challenge["difficulty"] = min(max(challenge["difficulty"], 1), 5)
            
            return challenge
            
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON response: {response}")
            return None
            
    except Exception as e:
        logging.error(f"Error generating challenge with AI: {str(e)}")
        return None


# DBT Chatbot API functions

def skills_on_demand(text):
    """Suggest the most appropriate DBT skill for the user's situation"""
    return call_router("skills_on_demand", text=text)


def generate_diary_card(text):
    """Generate a DBT diary card from the user's description"""
    return call_router("diary_card", text=text)


def validate_experience(text):
    """Validate the user's experience using DBT validation techniques"""
    return call_router("validate", text=text)


def distress_tolerance(text):
    """Provide distress tolerance skills for crisis situations"""
    return call_router("distress", text=text)


def chain_analysis(text):
    """Guide the user through a DBT chain analysis"""
    return call_router("chain_analysis", text=text)


def wise_mind(text):
    """Help the user access their wise mind"""
    return call_router("wise_mind", text=text)


def radical_acceptance(text):
    """Guide the user through radical acceptance"""
    return call_router("radical_acceptance", text=text)


def interpersonal_effectiveness(text):
    """Coach the user through interpersonal effectiveness skills"""
    return call_router("interpersonal", text=text)


def dialectic_generator(text):
    """Generate a dialectical perspective on the user's situation"""
    return call_router("dialectic", text=text)


def trigger_map(text):
    """Identify trigger patterns and recommend coping skills"""
    return call_router("trigger_map", text=text)


def skill_of_the_day():
    """Provide a random DBT skill of the day"""
    return call_router("skill_of_day")


def edit_message(original, target_skill, tone):
    """Edit a message to incorporate a specific DBT skill and tone"""
    return call_router("edit_message", original=original, target_skill=target_skill, tone=tone)


def advise(text):
    """Provide DBT advice for the user's situation"""
    return call_router("advise", text=text)