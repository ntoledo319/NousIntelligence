"""
Migration script to add the color_theme column to the UserSettings table.
"""
from app import app, db
from sqlalchemy import text
import logging

def add_color_theme_column():
    """Add color_theme column to user_settings table if it doesn't exist"""
    try:
        with app.app_context():
            # Check if the column exists
            result = db.session.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user_settings' AND column_name='color_theme'"
            )).fetchone()
            
            if not result:
                # Add the column with default value
                db.session.execute(text(
                    "ALTER TABLE user_settings ADD COLUMN color_theme VARCHAR(20) DEFAULT 'default'"
                ))
                db.session.commit()
                print("Added color_theme column to user_settings table")
                logging.info("Added color_theme column to user_settings table")
            else:
                print("color_theme column already exists in user_settings table")
                logging.info("color_theme column already exists in user_settings table")
                
    except Exception as e:
        print(f"Error adding color_theme column: {e}")
        logging.error(f"Error adding color_theme column: {e}")
        db.session.rollback()

if __name__ == "__main__":
    add_color_theme_column()