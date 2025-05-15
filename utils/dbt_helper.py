import os
import logging
import requests
import json
from flask import session
from datetime import datetime
from models import db, DBTSkillLog, DBTDiaryCard, DBTSkillCategory

# Helper functions for DBT chatbot functionality

# OpenRouter API configuration
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
DEFAULT_MODEL = "gpt-4o"  # Default to gpt-4o if not specified
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

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


def call_router(prompt_key, **kwargs):
    """Call OpenRouter with the specified prompt and arguments"""
    if not OPENROUTER_KEY:
        return {"error": "OpenRouter API key not configured"}
        
    try:
        # Format the prompt with the provided arguments
        prompt = PROMPTS[prompt_key].format(**kwargs)
        
        # Prepare the request
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        # Call the API
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return {"error": f"API Error: {response.status_code}"}
            
        result = response.json()
        
        if not result.get("choices"):
            logging.error("No response from LLM")
            return {"error": "No response received from language model"}
            
        return {"response": result["choices"][0]["message"]["content"].strip()}
        
    except Exception as e:
        logging.error(f"Error calling OpenRouter: {str(e)}")
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