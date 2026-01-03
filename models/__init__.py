"""
Models package initialization
Imports all models for easy access
"""

# Import only models that actually exist
# Wrap all imports in try/except for resilience
from .user import User

# Optional imports - only import if files exist
OAuthToken = None
APIKey = None
UserPreferences = None
Interaction = None
Conversation = None
Message = None
Memory = None
Reminder = None
Task = None
Habit = None
JournalEntry = None
CrisisResource = None
FinancialTransaction = None
Budget = None
FinancialGoal = None
SpotifyToken = None

try:
    from .oauth_token import OAuthToken
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .api_key import APIKey
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .user_preferences import UserPreferences
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .interaction import Interaction
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .conversation import Conversation
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .message import Message
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .memory import Memory
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .task_models import Task, Reminder
except (ImportError, ModuleNotFoundError):
    Task = None
    Reminder = None

try:
    from .cbt_models import ThoughtRecord, CognitiveDistortion, MoodEntry
except (ImportError, ModuleNotFoundError):
    ThoughtRecord = None
    CognitiveDistortion = None
    MoodEntry = None

try:
    from .journal import JournalEntry
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .crisis_resource import CrisisResource
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .financial_models import FinancialTransaction, Budget, FinancialGoal
except (ImportError, ModuleNotFoundError):
    pass

try:
    from .spotify_models import SpotifyToken
except (ImportError, ModuleNotFoundError):
    pass

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
