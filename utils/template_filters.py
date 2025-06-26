"""
Template Filters Module

This module provides custom template filters for the application templates.

@module utils.template_filters
@description Custom template filters for Jinja templates
"""

import logging
import datetime
from flask import Flask

logger = logging.getLogger(__name__)

def register_template_filters(app: Flask):
    """
    Register custom template filters for the application

    Args:
        app: Flask application instance
    """

    @app.template_filter('format_date')
    def format_date(value, format='%B %d, %Y'):
        """
        Format a date object or date string to a human-readable format

        Args:
            value: datetime object or date string
            format: date format string

        Returns:
            Formatted date string
        """
        if not value:
            return ''

        if isinstance(value, str):
            try:
                # Try to parse ISO format first
                value = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try to parse date-only format
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    return value

        if isinstance(value, datetime.datetime):
            return value.strftime(format)

        return value

    @app.template_filter('format_datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format a datetime with both date and time."""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return value
        return value.strftime(format)

    @app.template_filter('time_ago')
    def time_ago(value):
        """
        Format a datetime to a relative time string like "3 hours ago"

        Args:
            value: datetime object or date string

        Returns:
            Relative time string
        """
        if not value:
            return ''

        if isinstance(value, str):
            try:
                value = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value

        now = datetime.datetime.now(value.tzinfo) if value.tzinfo else datetime.datetime.utcnow()
        diff = now - value

        if diff.days > 365:
            years = diff.days // 365
            return f"{years} {'year' if years == 1 else 'years'} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} {'month' if months == 1 else 'months'} ago"
        elif diff.days > 0:
            return f"{diff.days} {'day' if diff.days == 1 else 'days'} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        else:
            return "just now"

    @app.template_filter('truncate_text')
    def truncate_text(value, length=100):
        """Truncate text to the specified length with ellipsis."""
        if value is None:
            return ""
        if len(value) <= length:
            return value
        return value[:length] + "..."

    @app.template_filter('truncate_words')
    def truncate_words(s, length=30, suffix='...'):
        """
        Truncate a string to a certain number of words

        Args:
            s: String to truncate
            length: Maximum number of words
            suffix: String to append if truncated

        Returns:
            Truncated string
        """
        if not s:
            return ''

        words = s.split()
        if len(words) <= length:
            return s

        return ' '.join(words[:length]) + suffix

    @app.template_filter('markdown')
    def markdown_filter(value):
        """Convert markdown text to HTML."""
        if value is None:
            return ""
        try:
            import markdown
            return markdown.markdown(value)
        except ImportError:
            logger.warning("Markdown package not installed, returning raw text")
            return value

    logger.info("Registered custom template filters")