"""
Centralized Database Configuration
Eliminates circular imports by providing a clean database setup
"""
import logging
from models.database import db, init_db as init_database

logger = logging.getLogger(__name__)

__all__ = ["db", "init_database"]