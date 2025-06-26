"""
Setup wizard module for NOUS assistant
Handles customization and personalization of the assistant
"""

import os
import json
import logging
from datetime import datetime
from flask import current_app

from app import db
from models import AssistantProfile, UserSettings, User

logger = logging.getLogger(__name__)

def get_assistant_profile(user_id=None):
    """
    Get the assistant profile for the user
    Creates a default profile if none exists

    Args:
        user_id: User identifier

    Returns:
        AssistantProfile object
    """
    if not user_id:
        # Return default profile if no user ID provided
        default_profile = AssistantProfile.query.filter_by(is_default=True).first()
        if default_profile:
            return default_profile
        else:
            return create_default_assistant_profile()

    # Try to get user's custom profile
    user_profile = AssistantProfile.query.filter_by(user_id=user_id).first()

    if user_profile:
        return user_profile

    # If user has no profile, return default
    default_profile = AssistantProfile.query.filter_by(is_default=True).first()
    if default_profile:
        return default_profile
    else:
        return create_default_assistant_profile()

def create_default_assistant_profile():
    """
    Create and return the default assistant profile

    Returns:
        AssistantProfile object
    """
    try:
        default_profile = AssistantProfile()
        default_profile.name = "NOUS"
        default_profile.display_name = "NOUS Assistant"
        default_profile.tagline = "Your personal AI assistant"
        default_profile.description = "NOUS is a personal AI assistant designed to help you with a variety of tasks including weather forecasting, shopping, health tracking, and more."
        default_profile.primary_color = "#6f42c1"  # Purple
        default_profile.theme = "dark"
        default_profile.personality = "friendly"
        default_profile.is_default = True

        db.session.add(default_profile)
        db.session.commit()

        logger.info("Created default assistant profile")
        return default_profile
    except Exception as e:
        logger.error(f"Error creating default profile: {str(e)}")
        db.session.rollback()
        # Return a non-persisted default profile
        profile = AssistantProfile()
        profile.name = "NOUS"
        profile.display_name = "NOUS Assistant"
        profile.primary_color = "#6f42c1"
        profile.theme = "dark"
        profile.personality = "friendly"
        profile.is_default = True
        return profile

def customize_assistant(user_id, data):
    """
    Create or update a customized assistant profile for the user

    Args:
        user_id: User identifier
        data: Dictionary with customization options

    Returns:
        AssistantProfile object
    """
    if not user_id:
        logger.error("Cannot customize assistant: No user ID provided")
        return None

    try:
        # Check if user already has a profile
        profile = AssistantProfile.query.filter_by(user_id=user_id).first()

        if not profile:
            # Create new profile
            profile = AssistantProfile()
            profile.user_id = user_id
            profile.is_default = False

        # Update profile with data
        if 'name' in data and data['name']:
            profile.name = data['name']

        if 'display_name' in data and data['display_name']:
            profile.display_name = data['display_name']

        if 'tagline' in data:
            profile.tagline = data['tagline']

        if 'description' in data:
            profile.description = data['description']

        if 'primary_color' in data and data['primary_color']:
            profile.primary_color = data['primary_color']

        if 'theme' in data:
            profile.theme = data['theme']

        if 'personality' in data:
            profile.personality = data['personality']

        # Handle logo upload if present
        if 'logo_data' in data and data['logo_data']:
            # In a real app you'd save this to a file and store the path
            # For simplicity, we'll just store the base64 data in this example
            profile.logo_path = data['logo_data']

        db.session.add(profile)
        db.session.commit()

        logger.info(f"Customized assistant profile for user {user_id}")
        return profile
    except Exception as e:
        logger.error(f"Error customizing assistant profile: {str(e)}")
        db.session.rollback()
        return None

def initialize_user_settings(user_id):
    """
    Initialize user settings with default values

    Args:
        user_id: User identifier

    Returns:
        UserSettings object
    """
    if not user_id:
        logger.error("Cannot initialize user settings: No user ID provided")
        return None

    try:
        # Check if user already has settings
        settings = UserSettings.query.filter_by(user_id=user_id).first()

        if settings:
            return settings

        # Create new settings with default values
        settings = UserSettings()
        settings.user_id = user_id

        db.session.add(settings)
        db.session.commit()

        # Reload the settings to ensure all fields are populated
        settings = UserSettings.query.filter_by(user_id=user_id).first()

        logger.info(f"Initialized settings for user {user_id}")
        return settings
    except Exception as e:
        logger.error(f"Error initializing user settings: {str(e)}")
        db.session.rollback()
        return None

def delete_customization(user_id):
    """
    Delete user's custom profile and revert to default

    Args:
        user_id: User identifier

    Returns:
        True if successful, False otherwise
    """
    if not user_id:
        logger.error("Cannot delete customization: No user ID provided")
        return False

    try:
        # Delete user's custom profile
        profile = AssistantProfile.query.filter_by(user_id=user_id).first()

        if profile:
            db.session.delete(profile)
            db.session.commit()
            logger.info(f"Deleted custom profile for user {user_id}")
            return True
        else:
            logger.info(f"No custom profile found for user {user_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting custom profile: {str(e)}")
        db.session.rollback()
        return False

def get_personality_options():
    """
    Get available assistant personality options

    Returns:
        List of personality options with descriptions
    """
    return [
        {
            'id': 'friendly',
            'name': 'Friendly & Approachable',
            'description': 'Warm, personable, and conversational. Uses casual language and focuses on building rapport.'
        },
        {
            'id': 'professional',
            'name': 'Professional & Efficient',
            'description': 'Formal, direct, and business-like. Focuses on clear information and efficient responses.'
        },
        {
            'id': 'supportive',
            'name': 'Supportive & Encouraging',
            'description': 'Empathetic, positive, and motivational. Provides emotional support and encouragement.'
        },
        {
            'id': 'technical',
            'name': 'Technical & Precise',
            'description': 'Detailed, analytical, and fact-focused. Uses technical terminology and provides in-depth information.'
        },
        {
            'id': 'creative',
            'name': 'Creative & Imaginative',
            'description': 'Expressive, artistic, and original. Offers unique perspectives and creative solutions.'
        },
        {
            'id': 'witty',
            'name': 'Witty & Humorous',
            'description': 'Light-hearted, clever, and amusing. Brings appropriate humor to interactions.'
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
    if not user_id:
        logger.error("Cannot get setup progress: No user ID provided")
        return {
            'has_started_setup': False,
            'has_completed_setup': False,
            'current_step': 'welcome',
            'next_step': 'welcome',
            'completed_steps': [],
            'remaining_steps': ['welcome', 'personalize', 'preferences', 'features', 'complete']
        }

    try:
        # Get user settings
        settings = UserSettings.query.filter_by(user_id=user_id).first()

        if not settings:
            # Create user settings
            settings = UserSettings()
            settings.user_id = user_id
            db.session.add(settings)
            db.session.commit()

        # Initialize progress data
        all_steps = ['welcome', 'personalize', 'preferences', 'features', 'complete']

        if not settings.setup_progress:
            # No progress yet
            return {
                'has_started_setup': False,
                'has_completed_setup': False,
                'current_step': 'welcome',
                'next_step': 'welcome',
                'completed_steps': [],
                'remaining_steps': all_steps,
                'percent_complete': 0
            }

        # Parse progress data
        progress_data = json.loads(settings.setup_progress)
        completed_steps = progress_data.get('completed_steps', [])
        setup_completed = progress_data.get('setup_completed', False)

        # Determine current step and next step
        if setup_completed:
            current_step = 'complete'
            next_step = None
        elif not completed_steps:
            current_step = 'welcome'
            next_step = 'welcome'
        else:
            current_step = completed_steps[-1]
            next_index = all_steps.index(current_step) + 1
            next_step = all_steps[next_index] if next_index < len(all_steps) else 'complete'

        # Calculate remaining steps
        remaining_steps = [step for step in all_steps if step not in completed_steps]
        if setup_completed:
            remaining_steps = []

        # Calculate percent complete
        if setup_completed:
            percent_complete = 100
        else:
            percent_complete = (len(completed_steps) / len(all_steps)) * 100

        return {
            'has_started_setup': len(completed_steps) > 0,
            'has_completed_setup': setup_completed,
            'current_step': current_step,
            'next_step': next_step,
            'completed_steps': completed_steps,
            'remaining_steps': remaining_steps,
            'percent_complete': percent_complete
        }
    except Exception as e:
        logger.error(f"Error getting setup progress: {str(e)}")
        all_steps = ['welcome', 'personalize', 'preferences', 'features', 'complete']
        return {
            'has_started_setup': False,
            'has_completed_setup': False,
            'current_step': 'welcome',
            'next_step': 'welcome',
            'completed_steps': [],
            'remaining_steps': all_steps,
            'percent_complete': 0
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
    if not user_id:
        logger.error("Cannot update setup progress: No user ID provided")
        return None

    try:
        # Get user settings
        settings = UserSettings.query.filter_by(user_id=user_id).first()

        if not settings:
            # Create user settings
            settings = UserSettings()
            settings.user_id = user_id
            db.session.add(settings)

        # Initialize or parse progress data
        if not settings.setup_progress:
            progress_data = {
                'completed_steps': [],
                'setup_completed': False,
                'started_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
        else:
            progress_data = json.loads(settings.setup_progress)
            progress_data['updated_at'] = datetime.utcnow().isoformat()

        # Update completed steps
        if step_completed and step_completed not in progress_data['completed_steps']:
            progress_data['completed_steps'].append(step_completed)

        # Update setup completed flag
        if setup_completed:
            progress_data['setup_completed'] = True
            progress_data['completed_at'] = datetime.utcnow().isoformat()

        # Save progress data
        settings.setup_progress = json.dumps(progress_data)
        db.session.commit()

        logger.info(f"Updated setup progress for user {user_id}")

        # Get updated progress info
        return get_setup_progress(user_id)
    except Exception as e:
        logger.error(f"Error updating setup progress: {str(e)}")
        db.session.rollback()
        return None