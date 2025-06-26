"""
Settings Cache Utility

This module provides caching functionality for system settings to reduce database load.
It caches frequently accessed system settings in memory for better performance.

@module utils.settings_cache
@description Cache utility for system settings
"""

import logging
import time
from typing import Dict, Any, Optional, Union
from flask import current_app, g
from app_factory import db

logger = logging.getLogger(__name__)

# In-memory cache for system settings
_settings_cache: Dict[str, Dict[str, Any]] = {}
# Cache expiration time in seconds (10 minutes - increased to reduce cache misses)
_cache_ttl = 600
# Flag to track if cache has been initialized
_cache_initialized = False

def get_system_setting(key: str, default: Any = None) -> Any:
    """
    Get a system setting value with caching

    Args:
        key: Setting key
        default: Default value if not found

    Returns:
        Setting value or default if not found
    """
    # Check if we have a cached version first
    cached = _get_from_cache(key)
    if cached is not None:
        return cached

    # Get from database
    try:
        from models import SystemSettings
        start_time = time.time()
        setting = SystemSettings.query.filter_by(key=key).first()
        query_time = time.time() - start_time

        # Log slow queries
        if query_time > 0.1:
            logger.warning(f"Slow system setting lookup: {key} in {query_time:.3f}s")

        # Cache the result
        if setting:
            value = setting.value
            _add_to_cache(key, value)
            return value
    except Exception as e:
        logger.error(f"Error getting system setting {key}: {str(e)}")

    return default

def set_system_setting(key: str, value: Any, description: Optional[str] = "") -> bool:
    """
    Set a system setting value with cache update

    Args:
        key: Setting key
        value: Setting value
        description: Optional description (defaults to empty string)

    Returns:
        True if successful, False otherwise
    """
    try:

        # Update or create setting
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            # Import needed for type checking
            # Create a new system settings instance properly
            setting = SystemSettings()
            setting.key = key
            setting.value = str(value)
            if description:  # Only set if not empty
                setting.description = description
            db.session.add(setting)

        db.session.commit()

        # Update cache
        _add_to_cache(key, value)

        return True
    except Exception as e:
        logger.error(f"Error setting system setting {key}: {str(e)}")
        db.session.rollback()
        return False

def clear_settings_cache() -> None:
    """Clear the settings cache"""
    _settings_cache.clear()
    logger.info("Settings cache cleared")

def _get_from_cache(key: str) -> Optional[Any]:
    """
    Get a value from the cache

    Args:
        key: Cache key

    Returns:
        Cached value or None if not found or expired
    """
    if key in _settings_cache:
        entry = _settings_cache[key]

        # Check expiration
        if entry['expires_at'] > time.time():
            return entry['value']

        # Remove expired entry
        del _settings_cache[key]

    return None

def _add_to_cache(key: str, value: Any) -> None:
    """
    Add a value to the cache

    Args:
        key: Cache key
        value: Value to cache
    """
    _settings_cache[key] = {
        'value': value,
        'expires_at': time.time() + _cache_ttl
    }

# Initialize cache with commonly used settings
def initialize_settings_cache() -> None:
    """Initialize the settings cache with commonly used settings - optimized batch loading"""
    global _cache_initialized

    # Skip if already initialized to prevent duplicate work
    if _cache_initialized:
        logger.debug("Settings cache already initialized, skipping")
        return

    try:

        # Create default settings if they don't exist
        _ensure_default_settings_exist()

        # Get all settings in a single query with timeout protection
        start_time = time.time()
        # Add limit to query to ensure it completes quickly
        all_settings = SystemSettings.query.limit(100).all()
        query_time = time.time() - start_time

        # Cache all settings
        for setting in all_settings:
            _add_to_cache(setting.key, setting.value)

        if query_time > 0.1:
            logger.warning(f"Slow initial settings load: {query_time:.3f}s for {len(all_settings)} settings")

        logger.info(f"Settings cache initialized with {len(all_settings)} entries")
        _cache_initialized = True
    except Exception as e:
        # Fallback to individual loading if batch load fails
        common_settings = [
            'session_timeout',
            'require_https',
            'maintenance_mode',
            'app_version'
        ]

        # Create these settings with defaults if they don't exist
        for key in common_settings:
            _ensure_setting_exists(key)

        loaded_count = 0
        for key in common_settings:
            value = get_system_setting(key)
            if value is not None:
                loaded_count += 1
                # No need to add to cache as get_system_setting does that

        logger.info(f"Settings cache initialized with {loaded_count} entries (fallback mode)")
        logger.warning(f"Batch loading failed: {str(e)}")
        _cache_initialized = True

def _ensure_default_settings_exist():
    """Ensure default settings exist in the database"""
    defaults = {
        'session_timeout': ('3600', 'Session timeout in seconds'),
        'require_https': ('true', 'Whether to require HTTPS for all requests'),
        'maintenance_mode': ('false', 'Whether the system is in maintenance mode'),
        'app_version': ('1.0.0', 'Application version number')
    }

    for key, (value, description) in defaults.items():
        _ensure_setting_exists(key, value, description)

def _ensure_setting_exists(key, default_value=None, description=None):
    """Ensure a specific setting exists in the database"""
    try:
        setting = SystemSettings.query.filter_by(key=key).first()
        if not setting:
            setting = SystemSettings()
            setting.key = key
            setting.value = default_value
            if description:
                setting.description = description
            db.session.add(setting)
            db.session.commit()
            logger.info(f"Created default system setting: {key}")
    except Exception as e:
        logger.error(f"Error ensuring system setting {key} exists: {str(e)}")
        # Don't roll back as this is a non-critical operation