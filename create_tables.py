"""
Database Table Creation Script

This script creates all the necessary database tables for the application.
"""

from app_factory import create_app, db
from models import User, UserSettings, Task, BetaTester, SystemSettings

def main():
    """Create all database tables"""
    print("Creating application context...")
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Print list of created tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        print(f"\nCreated tables ({len(table_names)}):")
        for table in table_names:
            print(f"- {table}")

if __name__ == "__main__":
    main() 