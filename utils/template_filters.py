"""
Template Filters Module

This module provides custom template filters for Jinja2 templates.
These filters enhance template functionality with common formatting and data manipulation operations.

@module utils.template_filters
@author NOUS Development Team
"""

import json
from datetime import datetime
from markupsafe import Markup


def register_template_filters(app):
    """
    Register all template filters with the Flask application.
    
    Args:
        app: Flask application instance
    """
    @app.template_filter('from_json')
    def from_json(value):
        """
        Parse JSON strings into Python objects.
        
        Args:
            value: JSON string to parse
            
        Returns:
            Parsed Python object or empty list on error
        """
        if value:
            try:
                return json.loads(value)
            except:
                return []
        return []
    
    @app.template_filter('nl2br')
    def nl2br(value):
        """
        Convert newlines to HTML line breaks.
        
        Args:
            value: Text with newlines
            
        Returns:
            HTML-safe string with <br> tags
        """
        if value:
            # Ensure value is a string and escape HTML characters
            value = str(value)
            value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            value = value.replace('\n', Markup('<br>'))
            return Markup(value)
        return ""
    
    @app.template_filter('datetime_format')
    def datetime_format(value, format='%Y-%m-%d %H:%M'):
        """
        Format a datetime object to a string.
        
        Args:
            value: Datetime object
            format: String format (default: '%Y-%m-%d %H:%M')
            
        Returns:
            Formatted date string or empty string if None
        """
        if value:
            return value.strftime(format)
        return ""
    
    @app.template_filter('currency')
    def currency_format(value):
        """
        Format a number as currency.
        
        Args:
            value: Number to format
            
        Returns:
            Formatted currency string (e.g., $123.45)
        """
        if value is not None:
            return f"${value:,.2f}"
        return "$0.00"
    
    @app.template_filter('truncate_with_ellipsis')
    def truncate_with_ellipsis(value, length=50):
        """
        Truncate text and add ellipsis if it exceeds a certain length.
        
        Args:
            value: Text to truncate
            length: Maximum length (default: 50)
            
        Returns:
            Truncated text with ellipsis or original text
        """
        if value and isinstance(value, str) and len(value) > length:
            return value[:length-3] + "..."
        return value
    
    @app.template_filter('timeago')
    def timeago(value):
        """
        Convert a datetime to a "time ago" string.
        
        Args:
            value: Datetime object
            
        Returns:
            String like "2 hours ago", "3 days ago", etc.
        """
        if not value:
            return ""
            
        now = datetime.now()
        diff = now - value
        
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2419200:
            weeks = int(seconds // 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            return value.strftime("%Y-%m-%d") 