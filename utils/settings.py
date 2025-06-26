"""
Settings Utility

This module provides functions for retrieving and managing application settings.
It handles retrieving settings from the database with fallback to defaults.

@module utils.settings
@description System settings utility functions
"""

import logging
from typing import Any, Dict, Union, Optional
from models import SystemSettings, db

# Configure logging
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_SETTINGS = {
    # Security settings
    'session_timeout': 60,  # minutes
    'max_login_attempts': 5,
    'password_min_length': 12,
    'account_lockout_duration': 15,  # minutes
    'require_https': True,
    'enable_audit_logging': True,

    # Email settings
    'email_from_name': 'NOUS Application',
    'email_from_address': 'noreply@mynous.app',

    # Feature flags
    'enable_beta_features': False,
    'enable_social_login': True,
    'enable_registration': True,

    # UI settings
    'default_theme': 'light',
    'show_welcome_message': True,
}

def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting from the database with fallback to default

    Args:
        key: The setting key to retrieve
        default: The default value if not found (overrides DEFAULT_SETTINGS)

    Returns:
        The setting value (typed appropriately)
    """
    try:
        # First check the database
        setting = SystemSettings.query.filter_by(key=key).first()

        if setting and setting.value is not None:
            return _convert_value_type(setting.value, key)

        # Fall back to default or DEFAULT_SETTINGS
        if default is not None:
            return default

        # Check DEFAULT_SETTINGS
        if key in DEFAULT_SETTINGS:
            return DEFAULT_SETTINGS[key]

        # Nothing found
        logger.warning(f"Setting '{key}' not found, returning None")
        return None

    except Exception as e:
        logger.error(f"Error retrieving setting '{key}': {str(e)}")

        # Fall back to defaults in case of error
        if default is not None:
            return default
        elif key in DEFAULT_SETTINGS:
            return DEFAULT_SETTINGS[key]
        return None

def get_all_settings() -> Dict[str, Any]:
    """Get all settings as a dictionary

    Returns:
        Dictionary of all settings with values
    """
    result = dict(DEFAULT_SETTINGS)  # Start with defaults

    try:
        # Overlay with database settings
        db_settings = SystemSettings.query.all()
        for setting in db_settings:
            result[setting.key] = _convert_value_type(setting.value, setting.key)
    except Exception as e:
        logger.error(f"Error retrieving all settings: {str(e)}")

    return result

def set_setting(key: str, value: Any, description: Optional[str] = None) -> bool:
    """Set a setting in the database

    Args:
        key: The setting key
        value: The setting value
        description: Optional description for the setting

    Returns:
        Boolean indicating success
    """
    try:
        # Convert value to string for storage
        str_value = str(value)

        # Look for existing setting
        setting = SystemSettings.query.filter_by(key=key).first()

        if setting:
            # Update existing setting
            setting.value = str_value
            if description:
                setting.description = description
        else:
            # Create new setting
            if not description:
                description = f"System setting for {key.replace('_', ' ')}"

            setting = SystemSettings(
                key=key,
                value=str_value,
                description=description
            )
            db.session.add(setting)

        # Commit changes
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error setting '{key}' to '{value}': {str(e)}")
        return False

def _convert_value_type(value_str: str, key: str) -> Any:
    """Convert string value to appropriate type based on default setting

    Args:
        value_str: The string value to convert
        key: The setting key to find the appropriate type

    Returns:
        Converted value
    """
    if key in DEFAULT_SETTINGS:
        default_value = DEFAULT_SETTINGS[key]
        default_type = type(default_value)

        try:
            if default_type == bool:
                return value_str.lower() in ('true', 'yes', '1', 'on')
            elif default_type == int:
                return int(value_str)
            elif default_type == float:
                return float(value_str)
            else:
                return value_str
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert '{key}' value '{value_str}' to type {default_type}")
            return value_str

    # If no default or not a known type, return as is
    return value_str