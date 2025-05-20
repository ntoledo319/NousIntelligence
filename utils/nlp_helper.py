"""
Natural Language Processing Helper Functions
===========================================

This module provides utility functions for extracting structured information
from natural language inputs, specifically designed to support chat-based
command interpretation.

These functions help the assistant understand dates, times, durations, emails,
and other structured data within user messages.
"""

import re
import datetime
from typing import List, Optional, Any, Tuple
import dateutil.parser
from dateutil.relativedelta import relativedelta

def extract_datetime(text: str) -> Optional[datetime.datetime]:
    """
    Extract date and time information from natural language text
    
    Args:
        text: Natural language text containing date/time information
        
    Returns:
        Extracted datetime object or None if no valid datetime found
    """
    # Try to identify common date/time patterns
    now = datetime.datetime.now()
    
    # Check for specific date patterns
    # Tomorrow
    if re.search(r'\btomorrow\b', text, re.IGNORECASE):
        result = now + datetime.timedelta(days=1)
        # Look for time info
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                hour += 12
            if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                hour = 0
            result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return result
    
    # Today
    if re.search(r'\btoday\b', text, re.IGNORECASE):
        result = now
        # Look for time info
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                hour += 12
            if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                hour = 0
            result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return result
    
    # Next [day of week]
    days = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2, 'weds': 2,
        'thursday': 3, 'thu': 3, 'thur': 3, 'thurs': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }
    
    for day_name, day_index in days.items():
        pattern = rf'\bnext\s+{day_name}\b'
        if re.search(pattern, text, re.IGNORECASE):
            # Calculate days until the next occurrence of this day
            current_day = now.weekday()
            days_ahead = day_index - current_day
            if days_ahead <= 0:  # Target day is today or earlier in the week
                days_ahead += 7
            result = now + datetime.timedelta(days=days_ahead)
            # Look for time info
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                    hour += 12
                if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                    hour = 0
                result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return result
    
    # This [day of week]
    for day_name, day_index in days.items():
        pattern = rf'\bthis\s+{day_name}\b'
        if re.search(pattern, text, re.IGNORECASE):
            # Calculate days until this day
            current_day = now.weekday()
            days_ahead = day_index - current_day
            if days_ahead < 0:  # Target day is earlier in the week
                days_ahead += 7
            result = now + datetime.timedelta(days=days_ahead)
            # Look for time info
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                    hour += 12
                if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                    hour = 0
                result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return result
    
    # Just a day of the week (assume upcoming)
    for day_name, day_index in days.items():
        pattern = rf'\b{day_name}\b'
        if re.search(pattern, text, re.IGNORECASE):
            # Calculate days until this day
            current_day = now.weekday()
            days_ahead = day_index - current_day
            if days_ahead <= 0:  # Target day is today or earlier in the week
                days_ahead += 7
            result = now + datetime.timedelta(days=days_ahead)
            # Look for time info
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                    hour += 12
                if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                    hour = 0
                result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return result
    
    # Next week
    if re.search(r'\bnext\s+week\b', text, re.IGNORECASE):
        result = now + datetime.timedelta(days=7)
        # Look for time info
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                hour += 12
            if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                hour = 0
            result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return result
    
    # Specific date formats (MM/DD, MM/DD/YYYY, etc.)
    date_pattern = r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?'
    date_match = re.search(date_pattern, text)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        year = int(date_match.group(3)) if date_match.group(3) else now.year
        if year < 100:
            year += 2000  # Assume 21st century for 2-digit years
        
        try:
            result = datetime.datetime(year, month, day)
            # Look for time info
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                    hour += 12
                if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                    hour = 0
                result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # Default to current time if no time specified
                result = result.replace(hour=now.hour, minute=now.minute, second=0, microsecond=0)
            return result
        except ValueError:
            # Invalid date, try other patterns
            pass
    
    # Month name patterns
    months = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    for month_name, month_num in months.items():
        pattern = rf'\b{month_name}\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(\d{{2,4}}))?'
        month_match = re.search(pattern, text, re.IGNORECASE)
        if month_match:
            day = int(month_match.group(1))
            year = int(month_match.group(2)) if month_match.group(2) else now.year
            if year < 100:
                year += 2000  # Assume 21st century for 2-digit years
            
            try:
                result = datetime.datetime(year, month_num, day)
                # Look for time info
                time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2) or 0)
                    if time_match.group(3) and time_match.group(3).lower() == 'pm' and hour < 12:
                        hour += 12
                    if time_match.group(3) and time_match.group(3).lower() == 'am' and hour == 12:
                        hour = 0
                    result = result.replace(hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    # Default to current time if no time specified
                    result = result.replace(hour=now.hour, minute=now.minute, second=0, microsecond=0)
                return result
            except ValueError:
                # Invalid date, try other patterns
                pass
    
    # If all else fails, try dateutil's parser as a fallback
    try:
        dt = dateutil.parser.parse(text, fuzzy=True)
        return dt
    except (ValueError, dateutil.parser.ParserError):
        return None

def extract_duration(text: str) -> Optional[int]:
    """
    Extract duration in minutes from natural language text
    
    Args:
        text: Natural language text containing duration information
        
    Returns:
        Duration in minutes or None if no valid duration found
    """
    # Look for X hours Y minutes format
    hours_mins_pattern = r'(\d+)\s*(?:hour|hr)s?(?:\s*and)?\s*(\d+)\s*(?:minute|min)s?'
    match = re.search(hours_mins_pattern, text, re.IGNORECASE)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours * 60 + minutes
    
    # Look for just hours
    hours_pattern = r'(\d+)\s*(?:hour|hr)s?'
    match = re.search(hours_pattern, text, re.IGNORECASE)
    if match:
        hours = int(match.group(1))
        return hours * 60
    
    # Look for just minutes
    mins_pattern = r'(\d+)\s*(?:minute|min)s?'
    match = re.search(mins_pattern, text, re.IGNORECASE)
    if match:
        minutes = int(match.group(1))
        return minutes
    
    # Look for "half an hour", "an hour", etc.
    special_patterns = {
        r'half\s*(?:an)?\s*hour': 30,
        r'an\s*hour': 60,
        r'hour\s*and\s*(?:a\s*)?half': 90,
        r'one\s*hour': 60,
        r'two\s*hours': 120,
        r'three\s*hours': 180
    }
    
    for pattern, value in special_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return value
    
    return None

def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text
    
    Args:
        text: Text containing email addresses
        
    Returns:
        List of extracted email addresses
    """
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    emails = re.findall(email_pattern, text)
    return emails 