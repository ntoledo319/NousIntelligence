"""
Alcoholics Anonymous recovery helper functions
Features:
- Meeting finder via Meeting Guide API
- Daily reflections and inventory
- Sponsor contact and logging
- Recovery statistics and streaks
- Nightly inventory and spot-checks
- Crisis resources
- Mindfulness tools
"""

import os
import json
import logging
import random
import datetime
import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta

from flask import session
from sqlalchemy import func, desc

# Import db from app_factory instead of app to avoid circular imports
from app_factory import db

# Import or create AA recovery models
# This approach avoids circular imports 
class AASettings:
    """User settings for AA recovery features"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.sponsor_name = kwargs.get('sponsor_name')
        self.sponsor_phone = kwargs.get('sponsor_phone')
        self.backup_contact_name = kwargs.get('backup_contact_name')
        self.backup_contact_phone = kwargs.get('backup_contact_phone')
        self.home_group = kwargs.get('home_group')
        self.sober_date = kwargs.get('sober_date')
        self.show_sober_days = kwargs.get('show_sober_days', True)
        self.track_honesty_streaks = kwargs.get('track_honesty_streaks', True)
        self.track_pain_flares = kwargs.get('track_pain_flares', False)  # Opt-in feature
        self.daily_reflection_time = kwargs.get('daily_reflection_time', "07:00")
        self.nightly_inventory_time = kwargs.get('nightly_inventory_time', "21:00")
        self.spot_checks_per_day = kwargs.get('spot_checks_per_day', 3)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sponsor_name': self.sponsor_name,
            'sponsor_phone': self.sponsor_phone,
            'backup_contact_name': self.backup_contact_name,
            'backup_contact_phone': self.backup_contact_phone,
            'home_group': self.home_group,
            'sober_date': self.sober_date.isoformat() if self.sober_date else None,
            'show_sober_days': self.show_sober_days,
            'track_honesty_streaks': self.track_honesty_streaks,
            'track_pain_flares': self.track_pain_flares,
            'daily_reflection_time': self.daily_reflection_time,
            'nightly_inventory_time': self.nightly_inventory_time,
            'spot_checks_per_day': self.spot_checks_per_day,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AARecoveryLog:
    """Log of recovery activities and entries"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.log_type = kwargs.get('log_type')
        self.content = kwargs.get('content')
        self.category = kwargs.get('category')
        self.is_honest_admit = kwargs.get('is_honest_admit', False)
        self.timestamp = kwargs.get('timestamp')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'log_type': self.log_type,
            'content': self.content,
            'category': self.category,
            'is_honest_admit': self.is_honest_admit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAMeetingLog:
    """Log of AA meetings attended"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.meeting_name = kwargs.get('meeting_name')
        self.meeting_type = kwargs.get('meeting_type')
        self.meeting_id = kwargs.get('meeting_id')
        self.date_attended = kwargs.get('date_attended')
        self.pre_meeting_reflection = kwargs.get('pre_meeting_reflection')
        self.post_meeting_reflection = kwargs.get('post_meeting_reflection')
        self.post_meeting_honest_admit = kwargs.get('post_meeting_honest_admit')
        self.created_at = kwargs.get('created_at')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meeting_name': self.meeting_name,
            'meeting_type': self.meeting_type,
            'meeting_id': self.meeting_id,
            'date_attended': self.date_attended.isoformat() if self.date_attended else None,
            'pre_meeting_reflection': self.pre_meeting_reflection,
            'post_meeting_reflection': self.post_meeting_reflection,
            'post_meeting_honest_admit': self.post_meeting_honest_admit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AANightlyInventory:
    """Nightly 10th Step inventory entries"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.date = kwargs.get('date')
        self.resentful = kwargs.get('resentful')
        self.selfish = kwargs.get('selfish')
        self.dishonest = kwargs.get('dishonest')
        self.afraid = kwargs.get('afraid')
        self.secrets = kwargs.get('secrets')
        self.apologies_needed = kwargs.get('apologies_needed')
        self.gratitude = kwargs.get('gratitude')
        self.surrender = kwargs.get('surrender')
        self.wrong_actions = kwargs.get('wrong_actions')
        self.amends_owed = kwargs.get('amends_owed')
        self.help_plan = kwargs.get('help_plan')
        self.completed = kwargs.get('completed', False)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'resentful': self.resentful,
            'selfish': self.selfish,
            'dishonest': self.dishonest,
            'afraid': self.afraid,
            'secrets': self.secrets,
            'apologies_needed': self.apologies_needed,
            'gratitude': self.gratitude,
            'surrender': self.surrender,
            'wrong_actions': self.wrong_actions,
            'amends_owed': self.amends_owed,
            'help_plan': self.help_plan,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AASpotCheck:
    """Spot-check inventory responses"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id') 
        self.user_id = kwargs.get('user_id')
        self.check_type = kwargs.get('check_type')
        self.question = kwargs.get('question')
        self.response = kwargs.get('response')
        self.rating = kwargs.get('rating')
        self.trigger = kwargs.get('trigger')
        self.timestamp = kwargs.get('timestamp')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'check_type': self.check_type,
            'question': self.question,
            'response': self.response,
            'rating': self.rating,
            'trigger': self.trigger,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AASponsorCall:
    """Log of calls to sponsor or backup contact"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.contact_type = kwargs.get('contact_type')
        self.pre_call_admission = kwargs.get('pre_call_admission')
        self.post_call_admission = kwargs.get('post_call_admission')
        self.timestamp = kwargs.get('timestamp')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_type': self.contact_type,
            'pre_call_admission': self.pre_call_admission,
            'post_call_admission': self.post_call_admission,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAMindfulnessLog:
    """Log of mindfulness and CBT exercises used"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.exercise_type = kwargs.get('exercise_type')
        self.exercise_name = kwargs.get('exercise_name')
        self.notes = kwargs.get('notes')
        self.timestamp = kwargs.get('timestamp')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_type': self.exercise_type,
            'exercise_name': self.exercise_name,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAAchievement:
    """Achievements and badges earned by users"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.badge_id = kwargs.get('badge_id')
        self.badge_name = kwargs.get('badge_name')
        self.badge_description = kwargs.get('badge_description')
        self.earned_date = kwargs.get('earned_date')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'earned_date': self.earned_date.isoformat() if self.earned_date else None
        }



# Load static data
def load_json_file(filename):
    """Load a JSON file from the static/aa_data directory"""
    try:
        file_path = os.path.join('static', 'aa_data', filename)
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading {filename}: {str(e)}")
        return {}

# Meeting Guide API
def find_meetings(zip_code, radius=25, day=None, time=None, types=None) -> Dict[str, Any]:
    """
    Find AA meetings using the Meeting Guide API
    
    Args:
        zip_code: Zip/postal code to search near
        radius: Search radius in miles (default: 25)
        day: Optional day filter (0-6, where 0 is Sunday)
        time: Optional time filter (HH:MM in 24-hour format)
        types: Optional meeting types filter (list of strings)
        
    Returns:
        Dict with meeting results
    """
    try:
        # Meeting Guide API endpoint
        url = "https://api.meetingguide.org/v1/meetings"
        
        # Build parameters
        params = {
            "postal_code": zip_code
        }
        
        if radius:
            params["distance"] = radius
            
        # Make API request
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return {"error": f"API error: {response.status_code}", "meetings": []}
            
        # Parse response
        meetings = response.json()
        
        # Apply any additional filters (Meeting Guide API doesn't support all filters)
        if day is not None or time is not None or types:
            filtered_meetings = []
            for meeting in meetings:
                # Day filter
                if day is not None and meeting.get("day") != day:
                    continue
                    
                # Time filter (approximate - compares start times)
                if time is not None:
                    meeting_time = meeting.get("time", "")
                    if time not in meeting_time:
                        continue
                        
                # Types filter
                if types:
                    meeting_types = meeting.get("types", [])
                    if not any(t in meeting_types for t in types):
                        continue
                        
                filtered_meetings.append(meeting)
                
            return {"meetings": filtered_meetings}
            
        return {"meetings": meetings}
        
    except Exception as e:
        logging.error(f"Error finding meetings: {str(e)}")
        return {"error": str(e), "meetings": []}
        
def log_meeting_attendance(user_id, meeting_id, meeting_name, meeting_type, 
                         date_attended, pre_reflection=None, reflection=None,
                         honest_admit=None) -> Dict[str, Any]:
    """
    Log attendance at an AA meeting
    
    Args:
        user_id: User ID
        meeting_id: Meeting ID (from Meeting Guide API)
        meeting_name: Meeting name
        meeting_type: Meeting type (in_person, online, phone)
        date_attended: Date attended
        pre_reflection: Optional pre-meeting reflection
        reflection: Optional post-meeting reflection
        honest_admit: Optional honesty admission
        
    Returns:
        Dict with result status
    """
    try:
        meeting_log = AAMeetingLog(
            user_id=user_id,
            meeting_id=meeting_id,
            meeting_name=meeting_name,
            meeting_type=meeting_type,
            date_attended=date_attended,
            pre_meeting_reflection=pre_reflection,
            post_meeting_reflection=reflection,
            post_meeting_honest_admit=honest_admit
        )
        
        db.session.add(meeting_log)
        db.session.commit()
        
        # Check if this merits a badge
        meeting_count = AAMeetingLog.query.filter_by(user_id=user_id).count()
        
        badges = []
        if meeting_count == 1:
            badges.append(add_achievement(user_id, "first_meeting", "First Meeting", "Attended your first logged AA meeting"))
        elif meeting_count == 10:
            badges.append(add_achievement(user_id, "ten_meetings", "Ten Meetings", "Attended 10 AA meetings"))
        elif meeting_count == 30:
            badges.append(add_achievement(user_id, "thirty_meetings", "Fellowship Milestone", "Attended 30 AA meetings"))
        elif meeting_count == 90:
            badges.append(add_achievement(user_id, "ninety_meetings", "90 in 90", "Completed 90 meetings"))
            
        return {
            "success": True, 
            "meeting_id": meeting_log.id,
            "new_badges": badges,
            "meeting_count": meeting_count
        }
        
    except Exception as e:
        logging.error(f"Error logging meeting attendance: {str(e)}")
        return {"success": False, "error": str(e)}

# Daily Reflections
def get_daily_reflection(user_id=None, reflection_type="morning") -> Dict[str, Any]:
    """
    Get a daily reflection for morning or evening
    
    Args:
        user_id: Optional user ID to track if they've seen this reflection
        reflection_type: Type of reflection (morning or evening)
        
    Returns:
        Dict with reflection content
    """
    try:
        reflections = load_json_file("reflections.json")
        
        if not reflections or reflection_type not in reflections:
            return {"error": "Reflections not found"}
            
        # Get a random reflection
        reflection = random.choice(reflections[reflection_type])
        
        # Log that this user has seen this reflection
        if user_id:
            try:
                reflection_content = reflection.get("content", reflection.get("prompt", ""))
                if reflection_content:
                    log = AARecoveryLog(
                        user_id=user_id,
                        log_type="daily_reflection",
                        content=reflection_content,
                        category=reflection_type
                    )
                    db.session.add(log)
                    db.session.commit()
            except Exception as log_error:
                logging.error(f"Error logging reflection: {str(log_error)}")
        
        return reflection
        
    except Exception as e:
        logging.error(f"Error getting daily reflection: {str(e)}")
        return {"error": str(e)}

def log_reflection_response(user_id, reflection_content, response_content, is_honest_admit=False) -> Dict[str, Any]:
    """
    Log a user's response to a reflection
    
    Args:
        user_id: User ID
        reflection_content: The reflection they responded to
        response_content: User's response text
        is_honest_admit: Whether this counts as an honesty admission
        
    Returns:
        Dict with result status
    """
    try:
        log = AARecoveryLog(
            user_id=user_id,
            log_type="reflection_response",
            content=f"Reflection: {reflection_content}\n\nResponse: {response_content}",
            is_honest_admit=is_honest_admit
        )
        
        db.session.add(log)
        db.session.commit()
        
        badges = []
        if is_honest_admit:
            # Check if this is their first honest admission
            admission_count = AARecoveryLog.query.filter_by(
                user_id=user_id, 
                is_honest_admit=True
            ).count()
            
            if admission_count == 1:
                badges.append(add_achievement(user_id, "first_admit", "First Honest Admission", "Made your first honest admission"))
            elif admission_count == 10:
                badges.append(add_achievement(user_id, "ten_admits", "Honesty Streak", "Made 10 honest admissions"))
            elif admission_count == 30:
                badges.append(add_achievement(user_id, "thirty_admits", "Rigorous Honesty", "Made 30 honest admissions"))
        
        return {
            "success": True, 
            "log_id": log.id,
            "new_badges": badges
        }
        
    except Exception as e:
        logging.error(f"Error logging reflection response: {str(e)}")
        return {"success": False, "error": str(e)}

# Sponsor Contact
def register_sponsor(user_id, sponsor_name, sponsor_phone,
                  backup_name=None, backup_phone=None) -> Dict[str, Any]:
    """
    Register or update sponsor information
    
    Args:
        user_id: User ID
        sponsor_name: Sponsor's name
        sponsor_phone: Sponsor's phone number
        backup_name: Optional backup contact name
        backup_phone: Optional backup contact phone
        
    Returns:
        Dict with result status
    """
    try:
        # Check if settings already exist
        settings = AASettings.query.filter_by(user_id=user_id).first()
        
        if settings:
            # Update existing settings
            settings.sponsor_name = sponsor_name
            settings.sponsor_phone = sponsor_phone
            
            if backup_name:
                settings.backup_contact_name = backup_name
                
            if backup_phone:
                settings.backup_contact_phone = backup_phone
                
            settings.updated_at = datetime.utcnow()
        else:
            # Create new settings
            settings = AASettings(
                user_id=user_id,
                sponsor_name=sponsor_name,
                sponsor_phone=sponsor_phone,
                backup_contact_name=backup_name,
                backup_contact_phone=backup_phone
            )
            db.session.add(settings)
            
        db.session.commit()
        
        return {"success": True, "settings_id": settings.id}
        
    except Exception as e:
        logging.error(f"Error registering sponsor: {str(e)}")
        return {"success": False, "error": str(e)}

def log_sponsor_call(user_id, contact_type, pre_call_admission=None, post_call_admission=None) -> Dict[str, Any]:
    """
    Log a call to sponsor or backup contact
    
    Args:
        user_id: User ID
        contact_type: Type of contact (sponsor or backup_contact)
        pre_call_admission: What the user admitted before the call
        post_call_admission: What the user admitted during the call
        
    Returns:
        Dict with result status
    """
    try:
        call_log = AASponsorCall(
            user_id=user_id,
            contact_type=contact_type,
            pre_call_admission=pre_call_admission,
            post_call_admission=post_call_admission
        )
        
        db.session.add(call_log)
        db.session.commit()
        
        # Check if this merits a badge
        call_count = AASponsorCall.query.filter_by(user_id=user_id).count()
        
        badges = []
        if call_count == 1:
            badges.append(add_achievement(user_id, "first_call", "First Sponsor Call", "Made your first logged call to your sponsor"))
        elif call_count == 10:
            badges.append(add_achievement(user_id, "ten_calls", "Consistent Connection", "Made 10 calls to your sponsor"))
            
        # Log honesty admission if provided
        if post_call_admission:
            honesty_log = AARecoveryLog(
                user_id=user_id,
                log_type="sponsor_call_admission",
                content=post_call_admission,
                is_honest_admit=True
            )
            db.session.add(honesty_log)
            db.session.commit()
            
        return {
            "success": True, 
            "call_id": call_log.id,
            "new_badges": badges
        }
        
    except Exception as e:
        logging.error(f"Error logging sponsor call: {str(e)}")
        return {"success": False, "error": str(e)}

# Recovery Stats
def get_recovery_stats(user_id) -> Dict[str, Any]:
    """
    Get comprehensive recovery statistics
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with recovery statistics
    """
    try:
        stats = {}
        
        # Get user settings
        settings = AASettings.query.filter_by(user_id=user_id).first()
        
        # Days sober
        if settings and settings.sober_date:
            days_sober = (datetime.utcnow().date() - settings.sober_date.date()).days
            stats["days_sober"] = days_sober
            stats["sober_since"] = settings.sober_date.strftime("%Y-%m-%d")
            
            # Add milestones
            milestones = []
            upcoming_milestones = []
            
            milestone_days = [1, 7, 30, 60, 90, 180, 365, 365*2, 365*3, 365*4, 365*5, 365*10]
            
            for days in milestone_days:
                milestone_date = settings.sober_date + timedelta(days=days)
                
                if days <= days_sober:
                    # Passed milestone
                    milestones.append({
                        "days": days,
                        "date": milestone_date.strftime("%Y-%m-%d"),
                        "passed": True
                    })
                else:
                    # Upcoming milestone
                    days_until = days - days_sober
                    upcoming_milestones.append({
                        "days": days,
                        "date": milestone_date.strftime("%Y-%m-%d"),
                        "days_until": days_until
                    })
            
            stats["milestones"] = milestones
            stats["upcoming_milestones"] = upcoming_milestones
        else:
            stats["days_sober"] = 0
            stats["sober_since"] = None
        
        # Meetings attended
        meeting_count = AAMeetingLog.query.filter_by(user_id=user_id).count()
        stats["meetings_attended"] = meeting_count
        
        # Recent meetings
        recent_meetings = AAMeetingLog.query.filter_by(user_id=user_id) \
            .order_by(AAMeetingLog.date_attended.desc()) \
            .limit(5) \
            .all()
            
        stats["recent_meetings"] = [meeting.to_dict() for meeting in recent_meetings]
        
        # Last meeting date
        if recent_meetings:
            stats["last_meeting"] = recent_meetings[0].date_attended.strftime("%Y-%m-%d")
            stats["days_since_meeting"] = (datetime.utcnow().date() - recent_meetings[0].date_attended.date()).days
        else:
            stats["last_meeting"] = None
            stats["days_since_meeting"] = None
            
        # Honesty streak
        honest_admits = AARecoveryLog.query.filter_by(
            user_id=user_id, 
            is_honest_admit=True
        ).order_by(AARecoveryLog.timestamp.desc()).all()
        
        stats["total_honest_admits"] = len(honest_admits)
        
        if honest_admits:
            stats["last_admission_date"] = honest_admits[0].timestamp.strftime("%Y-%m-%d")
            stats["days_since_admission"] = (datetime.utcnow().date() - honest_admits[0].timestamp.date()).days
            
            # Calculate current streak (consecutive days with admits)
            current_streak = 1
            prev_date = honest_admits[0].timestamp.date()
            
            for admit in honest_admits[1:]:
                admit_date = admit.timestamp.date()
                days_diff = (prev_date - admit_date).days
                
                if days_diff == 1:
                    # Consecutive day
                    current_streak += 1
                    prev_date = admit_date
                elif days_diff == 0:
                    # Same day, continue
                    prev_date = admit_date
                else:
                    # Streak broken
                    break
                    
            stats["current_streak"] = current_streak
        else:
            stats["last_admission_date"] = None
            stats["days_since_admission"] = None
            stats["current_streak"] = 0
            
        # Badges
        badges = AAAchievement.query.filter_by(user_id=user_id).all()
        stats["badges"] = [badge.to_dict() for badge in badges]
        stats["badge_count"] = len(badges)
        
        # Nightly inventories
        inventory_count = AANightlyInventory.query.filter_by(user_id=user_id, completed=True).count()
        stats["inventory_count"] = inventory_count
        
        # Spot checks
        spot_check_count = AASpotCheck.query.filter_by(user_id=user_id).count()
        stats["spot_check_count"] = spot_check_count
        
        # Sponsor calls
        sponsor_call_count = AASponsorCall.query.filter_by(user_id=user_id).count()
        stats["sponsor_call_count"] = sponsor_call_count
        
        # Money saved (estimate)
        if settings and settings.sober_date:
            # Very rough estimate - $10 per day saved
            money_saved = days_sober * 10
            stats["money_saved_estimate"] = money_saved
            
        return stats
        
    except Exception as e:
        logging.error(f"Error getting recovery stats: {str(e)}")
        return {"error": str(e)}

def set_sober_date(user_id, sober_date) -> Dict[str, Any]:
    """
    Set or update user's sober date
    
    Args:
        user_id: User ID
        sober_date: Sobriety date (datetime or string in YYYY-MM-DD format)
        
    Returns:
        Dict with result status
    """
    try:
        # Convert string date if needed
        if isinstance(sober_date, str):
            sober_date = datetime.strptime(sober_date, "%Y-%m-%d")
            
        # Check if settings already exist
        settings = AASettings.query.filter_by(user_id=user_id).first()
        
        if settings:
            # Update existing settings
            settings.sober_date = sober_date
            settings.updated_at = datetime.utcnow()
        else:
            # Create new settings
            settings = AASettings(
                user_id=user_id,
                sober_date=sober_date
            )
            db.session.add(settings)
            
        db.session.commit()
        
        # Calculate days sober
        days_sober = (datetime.utcnow().date() - sober_date.date()).days
        
        # Check if this merits a badge
        badges = []
        if days_sober >= 1:
            badges.append(add_achievement(user_id, "one_day", "One Day Sober", "Achieved one day of sobriety"))
        if days_sober >= 7:
            badges.append(add_achievement(user_id, "one_week", "One Week Sober", "Achieved one week of sobriety"))
        if days_sober >= 30:
            badges.append(add_achievement(user_id, "one_month", "One Month Sober", "Achieved one month of sobriety"))
        if days_sober >= 90:
            badges.append(add_achievement(user_id, "ninety_days", "90 Days Sober", "Achieved 90 days of sobriety"))
        if days_sober >= 365:
            badges.append(add_achievement(user_id, "one_year", "One Year Sober", "Achieved one year of sobriety"))
        
        return {
            "success": True, 
            "days_sober": days_sober,
            "new_badges": badges
        }
        
    except Exception as e:
        logging.error(f"Error setting sober date: {str(e)}")
        return {"success": False, "error": str(e)}

def update_aa_settings(user_id, settings_dict) -> Dict[str, Any]:
    """
    Update AA recovery settings
    
    Args:
        user_id: User ID
        settings_dict: Dictionary of settings to update
        
    Returns:
        Dict with result status
    """
    try:
        # Check if settings already exist
        settings = AASettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            # Create new settings
            settings = AASettings(user_id=user_id)
            db.session.add(settings)
            
        # Update fields from the dictionary
        for key, value in settings_dict.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
                
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {"success": True, "settings": settings.to_dict()}
        
    except Exception as e:
        logging.error(f"Error updating AA settings: {str(e)}")
        return {"success": False, "error": str(e)}

# Nightly Inventory
def get_nightly_inventory_template() -> Dict[str, Any]:
    """
    Get the template for nightly inventory
    
    Returns:
        Dict with inventory template questions
    """
    try:
        template = {
            "questions": [
                {"key": "resentful", "question": "Was I resentful today?", "category": "reflection"},
                {"key": "selfish", "question": "Was I selfish today?", "category": "reflection"},
                {"key": "dishonest", "question": "Was I dishonest today?", "category": "reflection"},
                {"key": "afraid", "question": "Was I afraid today?", "category": "reflection"},
                {"key": "secrets", "question": "Am I keeping any secrets?", "category": "reflection"},
                {"key": "apologies_needed", "question": "Do I need to apologize to anyone?", "category": "reflection"},
                {"key": "gratitude", "question": "What am I grateful for today?", "category": "reflection"},
                {"key": "surrender", "question": "What do I need to surrender?", "category": "reflection"},
                {"key": "wrong_actions", "question": "What did I do wrong today?", "category": "follow_up"},
                {"key": "amends_owed", "question": "Who do I owe an apology to?", "category": "follow_up"},
                {"key": "help_plan", "question": "How will I help someone tomorrow?", "category": "follow_up"}
            ]
        }
        
        return template
        
    except Exception as e:
        logging.error(f"Error getting nightly inventory template: {str(e)}")
        return {"error": str(e)}

def start_nightly_inventory(user_id) -> Dict[str, Any]:
    """
    Start a new nightly inventory
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with new inventory object and template
    """
    try:
        # Check if there's already an incomplete inventory for today
        today = datetime.utcnow().date()
        existing = AANightlyInventory.query.filter_by(
            user_id=user_id,
            date=today,
            completed=False
        ).first()
        
        if existing:
            return {
                "inventory": existing.to_dict(),
                "template": get_nightly_inventory_template(),
                "new": False
            }
            
        # Create new inventory
        inventory = AANightlyInventory(
            user_id=user_id,
            date=today,
            completed=False
        )
        
        db.session.add(inventory)
        db.session.commit()
        
        return {
            "inventory": inventory.to_dict(),
            "template": get_nightly_inventory_template(),
            "new": True
        }
        
    except Exception as e:
        logging.error(f"Error starting nightly inventory: {str(e)}")
        return {"error": str(e)}

def update_nightly_inventory(user_id, inventory_id, field, value) -> Dict[str, Any]:
    """
    Update a field in the nightly inventory
    
    Args:
        user_id: User ID
        inventory_id: Inventory ID
        field: Field to update
        value: New value
        
    Returns:
        Dict with updated inventory
    """
    try:
        # Find the inventory
        inventory = AANightlyInventory.query.filter_by(id=inventory_id, user_id=user_id).first()
        
        if not inventory:
            return {"success": False, "error": "Inventory not found"}
            
        # Update the field
        if hasattr(inventory, field):
            setattr(inventory, field, value)
            inventory.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {"success": True, "inventory": inventory.to_dict()}
        else:
            return {"success": False, "error": f"Invalid field: {field}"}
        
    except Exception as e:
        logging.error(f"Error updating nightly inventory: {str(e)}")
        return {"success": False, "error": str(e)}

def complete_nightly_inventory(user_id, inventory_id) -> Dict[str, Any]:
    """
    Mark a nightly inventory as complete
    
    Args:
        user_id: User ID
        inventory_id: Inventory ID
        
    Returns:
        Dict with result status
    """
    try:
        # Find the inventory
        inventory = AANightlyInventory.query.filter_by(id=inventory_id, user_id=user_id).first()
        
        if not inventory:
            return {"success": False, "error": "Inventory not found"}
            
        # Mark as complete
        inventory.completed = True
        inventory.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Create honesty admission logs for any admitted items
        honest_admits = []
        
        # Check resentful
        if inventory.resentful and inventory.resentful.strip().lower() not in ["no", "none", "n/a"]:
            honest_admits.append(("resentful", inventory.resentful))
            
        # Check selfish
        if inventory.selfish and inventory.selfish.strip().lower() not in ["no", "none", "n/a"]:
            honest_admits.append(("selfish", inventory.selfish))
            
        # Check dishonest
        if inventory.dishonest and inventory.dishonest.strip().lower() not in ["no", "none", "n/a"]:
            honest_admits.append(("dishonest", inventory.dishonest))
            
        # Check afraid
        if inventory.afraid and inventory.afraid.strip().lower() not in ["no", "none", "n/a"]:
            honest_admits.append(("afraid", inventory.afraid))
            
        # Check wrong actions
        if inventory.wrong_actions and inventory.wrong_actions.strip().lower() not in ["no", "none", "n/a"]:
            honest_admits.append(("wrong_actions", inventory.wrong_actions))
            
        # Log honest admissions
        for category, content in honest_admits:
            log = AARecoveryLog(
                user_id=user_id,
                log_type="nightly_inventory",
                content=content,
                category=category,
                is_honest_admit=True
            )
            db.session.add(log)
            
        db.session.commit()
        
        # Check for badges
        inventory_count = AANightlyInventory.query.filter_by(
            user_id=user_id,
            completed=True
        ).count()
        
        badges = []
        if inventory_count == 1:
            badges.append(add_achievement(user_id, "first_inventory", "First Inventory", "Completed your first nightly inventory"))
        elif inventory_count == 7:
            badges.append(add_achievement(user_id, "week_inventory", "Weekly Reflection", "Completed 7 nightly inventories"))
        elif inventory_count == 30:
            badges.append(add_achievement(user_id, "month_inventory", "Monthly Dedication", "Completed 30 nightly inventories"))
            
        # Check honest admit streaks
        admit_count = len(honest_admits)
        if admit_count > 0:
            badge = add_achievement(user_id, "daily_honest", "Daily Honesty", "Made an honest admission in your inventory")
            if badge:
                badges.append(badge)
        
        return {
            "success": True,
            "inventory": inventory.to_dict(),
            "honest_admits": len(honest_admits),
            "new_badges": badges
        }
        
    except Exception as e:
        logging.error(f"Error completing nightly inventory: {str(e)}")
        return {"success": False, "error": str(e)}

# Spot Checks
def get_random_spot_check(user_id=None, category=None) -> Dict[str, Any]:
    """
    Get a random spot check question
    
    Args:
        user_id: Optional user ID to track who's seen this question
        category: Optional category to filter questions
        
    Returns:
        Dict with spot check question
    """
    try:
        spot_checks = load_json_file("spot_checks.json")
        
        if not spot_checks or "questions" not in spot_checks:
            return {"error": "Spot check questions not found"}
            
        questions = spot_checks["questions"]
        
        # Filter by category if provided
        if category:
            filtered_questions = [q for q in questions if q.get("key") == category]
            if filtered_questions:
                questions = filtered_questions
                
        # Get a random question
        question = random.choice(questions)
        
        # Add a timestamp for tracking
        result = question.copy()
        result["timestamp"] = datetime.utcnow().isoformat()
        
        return result
        
    except Exception as e:
        logging.error(f"Error getting spot check: {str(e)}")
        return {"error": str(e)}

def log_spot_check_response(user_id, check_type, question, response, 
                          rating=None, trigger=None) -> Dict[str, Any]:
    """
    Log a response to a spot-check question
    
    Args:
        user_id: User ID
        check_type: Type of check (resentment, selfish, etc.)
        question: The question text
        response: User's response
        rating: Optional rating (0-5) for relevant questions
        trigger: Optional trigger identification
        
    Returns:
        Dict with result status
    """
    try:
        spot_check = AASpotCheck(
            user_id=user_id,
            check_type=check_type,
            question=question,
            response=response,
            rating=rating,
            trigger=trigger
        )
        
        db.session.add(spot_check)
        db.session.commit()
        
        # Determine if this is an honest admission
        is_honest_admit = False
        if check_type in ["resentment", "selfish", "dishonest", "afraid", "anger"] and response:
            # Check if response indicates an admission (not just "no" or "none")
            if response.strip().lower() not in ["no", "none", "n/a"]:
                is_honest_admit = True
                
                # Log the honest admission
                log = AARecoveryLog(
                    user_id=user_id,
                    log_type="spot_check",
                    content=response,
                    category=check_type,
                    is_honest_admit=True
                )
                db.session.add(log)
                db.session.commit()
        
        # Check for badges
        check_count = AASpotCheck.query.filter_by(user_id=user_id).count()
        
        badges = []
        if check_count == 1:
            badges.append(add_achievement(user_id, "first_spot_check", "First Spot-Check", "Completed your first spot-check inventory"))
        elif check_count == 10:
            badges.append(add_achievement(user_id, "ten_spot_checks", "Consistent Awareness", "Completed 10 spot-check inventories"))
        elif check_count == 50:
            badges.append(add_achievement(user_id, "fifty_spot_checks", "Vigilant Self-Awareness", "Completed 50 spot-check inventories"))
            
        return {
            "success": True, 
            "spot_check_id": spot_check.id,
            "is_honest_admit": is_honest_admit,
            "new_badges": badges
        }
        
    except Exception as e:
        logging.error(f"Error logging spot check response: {str(e)}")
        return {"success": False, "error": str(e)}

# Crisis Resources
def get_crisis_resources() -> Dict[str, Any]:
    """
    Get crisis resources and helpline information
    
    Returns:
        Dict with crisis resources
    """
    resources = {
        "helplines": [
            {
                "name": "SAMHSA's National Helpline",
                "description": "24/7, 365-day-a-year treatment referral and information service for individuals and families facing mental and/or substance use disorders.",
                "phone": "1-800-662-HELP (4357)",
                "website": "https://www.samhsa.gov/find-help/national-helpline"
            },
            {
                "name": "National Suicide Prevention Lifeline",
                "description": "24/7, free and confidential support for people in distress, prevention and crisis resources.",
                "phone": "988 or 1-800-273-TALK (8255)",
                "website": "https://988lifeline.org/"
            },
            {
                "name": "Crisis Text Line",
                "description": "Text HOME to 741741 from anywhere in the USA to text with a trained Crisis Counselor.",
                "phone": "Text HOME to 741741",
                "website": "https://www.crisistextline.org/"
            }
        ],
        "aa_resources": [
            {
                "name": "Alcoholics Anonymous",
                "description": "Find local AA meetings and resources.",
                "website": "https://www.aa.org/"
            },
            {
                "name": "AA Online Intergroup",
                "description": "Find online AA meetings.",
                "website": "https://aa-intergroup.org/"
            }
        ],
        "immediate_actions": [
            "Call your sponsor immediately",
            "Go to an AA meeting (in-person or online)",
            "Read the Big Book, especially chapter 5",
            "Practice the serenity prayer",
            "Call a sober friend",
            "Remove yourself from triggering situations",
            "Remember H.A.L.T. - Are you Hungry, Angry, Lonely, or Tired?"
        ]
    }
    
    return resources

# Mindfulness Tools
def get_mindfulness_exercises(category=None) -> Dict[str, Any]:
    """
    Get mindfulness and CBT exercises
    
    Args:
        category: Optional category to filter exercises
        
    Returns:
        Dict with mindfulness exercises
    """
    try:
        mindfulness = load_json_file("mindfulness.json")
        
        if not mindfulness:
            return {"error": "Mindfulness exercises not found"}
            
        # Filter by category if provided
        if category and category in mindfulness:
            return {category: mindfulness[category]}
            
        return mindfulness
        
    except Exception as e:
        logging.error(f"Error getting mindfulness exercises: {str(e)}")
        return {"error": str(e)}

def log_mindfulness_exercise(user_id, exercise_type, exercise_name, notes=None) -> Dict[str, Any]:
    """
    Log completion of a mindfulness exercise
    
    Args:
        user_id: User ID
        exercise_type: Type of exercise (breathing, thought_record, etc.)
        exercise_name: Name of the specific exercise
        notes: Optional user notes
        
    Returns:
        Dict with result status
    """
    try:
        log = AAMindfulnessLog(
            user_id=user_id,
            exercise_type=exercise_type,
            exercise_name=exercise_name,
            notes=notes
        )
        
        db.session.add(log)
        db.session.commit()
        
        # Check for badges
        exercise_count = AAMindfulnessLog.query.filter_by(user_id=user_id).count()
        
        badges = []
        if exercise_count == 1:
            badges.append(add_achievement(user_id, "first_mindfulness", "First Mindfulness Practice", "Completed your first mindfulness exercise"))
        elif exercise_count == 10:
            badges.append(add_achievement(user_id, "ten_mindfulness", "Mindfulness Journey", "Completed 10 mindfulness exercises"))
            
        return {
            "success": True, 
            "log_id": log.id,
            "new_badges": badges
        }
        
    except Exception as e:
        logging.error(f"Error logging mindfulness exercise: {str(e)}")
        return {"success": False, "error": str(e)}

# Achievements and Badges
def add_achievement(user_id, badge_id, badge_name, badge_description) -> Optional[Dict[str, Any]]:
    """
    Add an achievement badge for a user
    
    Args:
        user_id: User ID
        badge_id: Unique badge identifier
        badge_name: Display name for the badge
        badge_description: Description of the achievement
        
    Returns:
        Dict with badge details or None if badge already exists
    """
    try:
        # Check if badge already exists
        existing = AAAchievement.query.filter_by(
            user_id=user_id,
            badge_id=badge_id
        ).first()
        
        if existing:
            return None
            
        # Create new badge
        badge = AAAchievement(
            user_id=user_id,
            badge_id=badge_id,
            badge_name=badge_name,
            badge_description=badge_description
        )
        
        db.session.add(badge)
        db.session.commit()
        
        return badge.to_dict()
        
    except Exception as e:
        logging.error(f"Error adding achievement: {str(e)}")
        return None

# Forum
