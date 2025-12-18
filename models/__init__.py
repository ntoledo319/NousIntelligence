"""
Models package initialization
Imports all models for easy access
"""

# Keep existing imports or use generic placeholders if not available
# This block assumes these files exist in your project.
from .user import User
from .oauth_token import OAuthToken
from .api_key import APIKey
from .user_preferences import UserPreferences
from .interaction import Interaction
from .conversation import Conversation
from .message import Message
from .memory import Memory
from .reminder import Reminder
from .task import Task
from .habit import Habit
from .journal import JournalEntry
from .crisis_resource import CrisisResource
from .financial import FinancialTransaction, Budget, FinancialGoal

# Optional Spotify models
try:
    from .spotify_models import SpotifyToken
except Exception:
    SpotifyToken = None

__all__ = [
    "User",
    "OAuthToken",
    "APIKey",
    "UserPreferences",
    "Interaction",
    "Conversation",
    "Message",
    "Memory",
    "Reminder",
    "Task",
    "Habit",
    "JournalEntry",
    "CrisisResource",
    "FinancialTransaction",
    "Budget",
    "FinancialGoal",
    "SpotifyToken",
]
