"""
User Repository - Data access layer for user-related operations
"""

from typing import Optional, List, Dict, Any
from database import db
from models.user import User

class UserRepository:
    """Repository for user data access operations"""

    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all_users(limit: Optional[int] = None) -> List[User]:
        """Get all users with optional limit"""
        query = User.query
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def update_user(user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user data"""
        user = User.query.filter_by(id=user_id).first()
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete user by ID"""
        user = User.query.filter_by(id=user_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    @staticmethod
    def search_users(query: str, limit: int = 10) -> List[User]:
        """Search users by name or email"""
        search_pattern = f"%{query}%"
        return User.query.filter(
            db.or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        ).limit(limit).all()