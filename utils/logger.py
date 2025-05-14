import os
import json
import datetime
import logging

def ensure_directory(directory):
    """Ensure a directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def log_workout(entry):
    """Log workout entry to JSON file"""
    try:
        ensure_directory("data")
        log_file = "data/workouts.json"
        
        # Create an empty file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                json.dump([], f)
        
        # Read existing entries
        with open(log_file, "r") as f:
            try:
                entries = json.load(f)
                if not isinstance(entries, list):
                    entries = []
            except json.JSONDecodeError:
                entries = []
        
        # Add new entry
        entry_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "entry": entry
        }
        entries.append(entry_data)
        
        # Write back to file
        with open(log_file, "w") as f:
            json.dump(entries, f, indent=2)
            
        return True
    except Exception as e:
        logging.error(f"Error logging workout: {str(e)}")
        return False

def log_mood(entry):
    """Log mood entry to JSON file"""
    try:
        ensure_directory("data")
        log_file = "data/moods.json"
        
        # Create an empty file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                json.dump([], f)
        
        # Read existing entries
        with open(log_file, "r") as f:
            try:
                entries = json.load(f)
                if not isinstance(entries, list):
                    entries = []
            except json.JSONDecodeError:
                entries = []
        
        # Add new entry
        entry_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "entry": entry
        }
        entries.append(entry_data)
        
        # Write back to file
        with open(log_file, "w") as f:
            json.dump(entries, f, indent=2)
            
        return True
    except Exception as e:
        logging.error(f"Error logging mood: {str(e)}")
        return False

def get_workout_entries(limit=10):
    """Get recent workout entries"""
    try:
        log_file = "data/workouts.json"
        if not os.path.exists(log_file):
            return []
            
        with open(log_file, "r") as f:
            entries = json.load(f)
            
        # Sort by timestamp (newest first) and limit
        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return entries[:limit]
    except Exception as e:
        logging.error(f"Error reading workout log: {str(e)}")
        return []

def get_mood_entries(limit=10):
    """Get recent mood entries"""
    try:
        log_file = "data/moods.json"
        if not os.path.exists(log_file):
            return []
            
        with open(log_file, "r") as f:
            entries = json.load(f)
            
        # Sort by timestamp (newest first) and limit
        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return entries[:limit]
    except Exception as e:
        logging.error(f"Error reading mood log: {str(e)}")
        return []
