"""
Default User Creator

This module creates a default admin user for the application
when no users exist in the database.

@module create_default_user
@description Create default admin user for initial login
"""

import logging
import uuid
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask

logger = logging.getLogger(__name__)

def create_default_admin(app: Flask, db):
    """
    Create a default admin user if no users exist in the database

    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    with app.app_context():
        try:
            # Import model inside the function to avoid circular imports
            from models import User, UserSettings

            # Check if any users exist
            users_count = User.query.count()

            if users_count == 0:
                logger.info("No users found. Creating default admin user...")

                # Create default admin user
                admin_user = User()
                admin_user.id = str(uuid.uuid4())
                admin_user.email = 'admin@example.com'
                admin_user.first_name = 'Admin'
                admin_user.last_name = 'User'
                admin_user.is_admin = True
                admin_user.account_active = True
                admin_user.created_at = datetime.utcnow()
                admin_user.email_verified = True
                admin_user.username = 'admin'

                # Set password to 'admin123'
                admin_user.set_password('admin123')

                # Add user to database
                db.session.add(admin_user)
                db.session.commit()

                # Create default settings for admin user
                admin_settings = UserSettings()
                admin_settings.user_id = admin_user.id
                admin_settings.theme = 'light'
                admin_settings.ai_name = 'NOUS'
                admin_settings.ai_personality = 'helpful'
                admin_settings.preferred_language = 'en'

                # Add settings to database
                db.session.add(admin_settings)
                db.session.commit()

                logger.info(f"Default admin user created successfully: {admin_user.email}")
                logger.info("Username: admin@example.com / Password: admin123")
            else:
                logger.info(f"Users already exist in database ({users_count} found). Skipping default user creation.")

        except SQLAlchemyError as e:
            logger.error(f"Database error creating default user: {str(e)}")
            db.session.rollback()
        except Exception as e:
            logger.error(f"Error creating default user: {str(e)}")
            db.session.rollback()