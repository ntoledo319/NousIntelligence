"""
Setup wizard module for NOUS assistant
Handles customization and personalization of the assistant
"""

import os
import json
import logging
from datetime import datetime
import base64

# Import models and database
from models import db, AssistantProfile, UserSettings

def get_assistant_profile(user_id=None):
    """
    Get the assistant profile for the user
    Creates a default profile if none exists
    
    Args:
        user_id: User identifier
        
    Returns:
        AssistantProfile object
    """
    try:
        # If user_id is None, get the default assistant profile
        if user_id is None:
            profile = AssistantProfile.query.filter_by(is_default=True).first()
            if profile:
                return profile
                
        # Otherwise get the user's customized profile
        else:
            profile = AssistantProfile.query.filter_by(user_id=user_id).first()
            if profile:
                return profile
            
            # If user doesn't have a profile, check for default
            profile = AssistantProfile.query.filter_by(is_default=True).first()
            if profile:
                return profile
        
        # If no profile exists at all, create the default
        return create_default_assistant_profile()
        
    except Exception as e:
        logging.error(f"Error getting assistant profile: {str(e)}")
        return create_default_assistant_profile()
        
def create_default_assistant_profile():
    """
    Create and return the default assistant profile
    
    Returns:
        AssistantProfile object
    """
    try:
        # Check if default profile already exists
        default_profile = AssistantProfile.query.filter_by(is_default=True).first()
        if default_profile:
            return default_profile
            
        # Create a new default profile
        profile = AssistantProfile(
            name="NOUS",
            display_name="NOUS",
            tagline="Your Personal Assistant",
            description="NOUS is a comprehensive personal assistant designed to help you with a variety of tasks.",
            primary_color="#6f42c1",
            is_default=True,
            theme="dark",
            personality="friendly",
            logo_path="img/IMG_4875.jpeg"
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return profile
    except Exception as e:
        logging.error(f"Error creating default profile: {str(e)}")
        # If we can't create one in the database, return a temporary object
        return AssistantProfile(
            name="NOUS",
            display_name="NOUS",
            tagline="Your Personal Assistant",
            primary_color="#6f42c1",
            theme="dark",
            personality="friendly",
            logo_path="img/IMG_4875.jpeg"
        )

def customize_assistant(user_id, data):
    """
    Create or update a customized assistant profile for the user
    
    Args:
        user_id: User identifier
        data: Dictionary with customization options
        
    Returns:
        AssistantProfile object
    """
    try:
        # Check if user already has a profile
        profile = AssistantProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            # Create a new profile based on the default
            default_profile = get_assistant_profile()
            
            profile = AssistantProfile(
                user_id=user_id,
                name=default_profile.name,
                display_name=default_profile.display_name,
                tagline=default_profile.tagline,
                description=default_profile.description,
                primary_color=default_profile.primary_color,
                theme=default_profile.theme,
                personality=default_profile.personality,
                logo_path=default_profile.logo_path,
                is_default=False
            )
            
            db.session.add(profile)
        
        # Update with new data
        if 'name' in data and data['name']:
            profile.name = data['name']
            
        if 'display_name' in data and data['display_name']:
            profile.display_name = data['display_name']
            
        if 'tagline' in data and data['tagline']:
            profile.tagline = data['tagline']
            
        if 'description' in data and data['description']:
            profile.description = data['description']
            
        if 'primary_color' in data and data['primary_color']:
            profile.primary_color = data['primary_color']
            
        if 'theme' in data and data['theme']:
            profile.theme = data['theme']
            
        if 'personality' in data and data['personality']:
            profile.personality = data['personality']
        
        # Handle logo upload if present
        if 'logo_data' in data and data['logo_data']:
            # Save logo to static folder
            try:
                # Get data after base64 prefix
                img_data = data['logo_data'].split('base64,')[1]
                img_bytes = base64.b64decode(img_data)
                
                # Create a unique filename using timestamp
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"logo_{user_id}_{timestamp}.png"
                filepath = os.path.join('static', 'img', 'profiles', filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Save the file
                with open(filepath, 'wb') as f:
                    f.write(img_bytes)
                
                # Update logo path
                profile.logo_path = f"img/profiles/{filename}"
            except Exception as e:
                logging.error(f"Error saving logo: {str(e)}")
        
        db.session.commit()
        return profile
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error customizing assistant: {str(e)}")
        return get_assistant_profile(user_id)

def delete_customization(user_id):
    """
    Delete user's custom profile and revert to default
    
    Args:
        user_id: User identifier
        
    Returns:
        True if successful, False otherwise
    """
    try:
        profile = AssistantProfile.query.filter_by(user_id=user_id).first()
        
        if profile:
            # If profile has a custom logo, delete the file
            if profile.logo_path and 'profiles/' in profile.logo_path:
                try:
                    filepath = os.path.join('static', profile.logo_path)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    logging.error(f"Error removing logo file: {str(e)}")
            
            # Delete the profile
            db.session.delete(profile)
            db.session.commit()
            
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting customization: {str(e)}")
        return False

def get_personality_options():
    """
    Get available assistant personality options
    
    Returns:
        List of personality options with descriptions
    """
    return [
        {
            "id": "friendly",
            "name": "Friendly & Casual",
            "description": "Warm, approachable, and conversational. Uses casual language and adds a touch of humor."
        },
        {
            "id": "professional",
            "name": "Professional & Efficient",
            "description": "Formal, focused on efficiency and clarity. Direct and concise responses."
        },
        {
            "id": "encouraging",
            "name": "Encouraging & Supportive",
            "description": "Positive, motivational tone. Offers encouragement and celebrates achievements."
        },
        {
            "id": "knowledgeable",
            "name": "Knowledgeable & Informative",
            "description": "Educational focus, provides context and background information. Detail-oriented."
        },
        {
            "id": "empathetic",
            "name": "Empathetic & Understanding",
            "description": "Compassionate and emotionally aware. Shows understanding of challenges and concerns."
        }
    ]

def get_setup_progress(user_id):
    """
    Get the setup progress for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with setup progress information
    """
    try:
        # Check if user has settings
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            return {
                "has_completed_setup": False,
                "steps_completed": [],
                "next_step": "welcome"
            }
            
        # Parse setup progress
        setup_progress = {}
        
        if settings.setup_progress:
            try:
                setup_progress = json.loads(settings.setup_progress)
            except:
                setup_progress = {}
        
        # Check if setup is complete
        has_completed_setup = setup_progress.get("setup_completed", False)
        
        # Get completed steps
        steps_completed = setup_progress.get("steps_completed", [])
        
        # Determine next step
        all_steps = ["welcome", "personalize", "preferences", "features", "complete"]
        next_step = None
        
        for step in all_steps:
            if step not in steps_completed:
                next_step = step
                break
                
        if not next_step and not has_completed_setup:
            next_step = "complete"
            
        return {
            "has_completed_setup": has_completed_setup,
            "steps_completed": steps_completed,
            "next_step": next_step,
            "progress_percentage": min(100, int(len(steps_completed) / len(all_steps) * 100))
        }
    except Exception as e:
        logging.error(f"Error getting setup progress: {str(e)}")
        return {
            "has_completed_setup": False, 
            "steps_completed": [],
            "next_step": "welcome",
            "progress_percentage": 0
        }

def update_setup_progress(user_id, step_completed, setup_completed=False):
    """
    Update the setup progress for a user
    
    Args:
        user_id: User identifier
        step_completed: Step that was completed
        setup_completed: Whether the entire setup is complete
        
    Returns:
        Dictionary with updated setup progress
    """
    try:
        # Get or create user settings
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            from models import User
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}
                
            settings = UserSettings(user_id=user_id)
            db.session.add(settings)
        
        # Parse existing setup progress
        setup_progress = {}
        
        if settings.setup_progress:
            try:
                setup_progress = json.loads(settings.setup_progress)
            except:
                setup_progress = {}
        
        # Update steps completed
        steps_completed = setup_progress.get("steps_completed", [])
        
        if step_completed and step_completed not in steps_completed:
            steps_completed.append(step_completed)
            
        setup_progress["steps_completed"] = steps_completed
        
        # Update setup completed flag if specified
        if setup_completed:
            setup_progress["setup_completed"] = True
        
        # Save back to settings
        settings.setup_progress = json.dumps(setup_progress)
        db.session.commit()
        
        # Return updated progress
        return get_setup_progress(user_id)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating setup progress: {str(e)}")
        return {"error": str(e)}