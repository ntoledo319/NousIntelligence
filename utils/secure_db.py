from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

class SecureQuery:
    @staticmethod
    def safe_filter(model, field, value):
        """Safe filtering using SQLAlchemy ORM"""
        return model.query.filter(getattr(model, field) == value)
    
    @staticmethod
    def safe_search(model, field, search_term):
        """Safe text search"""
        return model.query.filter(getattr(model, field).ilike(f"%{search_term}%"))
    
    @staticmethod
    def safe_execute(query, params=None):
        """Safe raw SQL execution"""
        from app import db
        if params is None:
            params = {}
        return db.session.execute(text(query), params)
