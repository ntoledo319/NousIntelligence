"""
Database configuration for NOUS application

This module provides a centralized database configuration to avoid circular imports
and properly initialize the SQLAlchemy instance.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Create the SQLAlchemy instance
db = SQLAlchemy(model_class=Base)