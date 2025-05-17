"""
Base Repository Module

This module provides a base repository implementation for database operations.
Repositories provide an abstraction layer for database access and implement
common patterns for data access.

@module repositories.base
@author NOUS Development Team
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union
from sqlalchemy.exc import SQLAlchemyError
import logging
from models import db

T = TypeVar('T')

logger = logging.getLogger(__name__)

class Repository(Generic[T]):
    """
    Base repository class that implements common database operations.
    Generic over the model type T.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize repository with the model class.
        
        Args:
            model_class: SQLAlchemy model class
        """
        self.model_class = model_class
    
    def create(self, **kwargs) -> T:
        """
        Create a new entity.
        
        Args:
            **kwargs: Attributes for the new entity
            
        Returns:
            Created entity
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            entity = self.model_class(**kwargs)
            db.session.add(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            raise
    
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Entity or None if not found
        """
        return self.model_class.query.get(entity_id)
    
    def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of all entities
        """
        return self.model_class.query.all()
    
    def find_by(self, **kwargs) -> List[T]:
        """
        Find entities by attributes.
        
        Args:
            **kwargs: Attributes to filter by
            
        Returns:
            List of matching entities
        """
        return self.model_class.query.filter_by(**kwargs).all()
    
    def find_one_by(self, **kwargs) -> Optional[T]:
        """
        Find a single entity by attributes.
        
        Args:
            **kwargs: Attributes to filter by
            
        Returns:
            Entity or None if not found
        """
        return self.model_class.query.filter_by(**kwargs).first()
    
    def update(self, entity: T, **kwargs) -> T:
        """
        Update an entity with new attributes.
        
        Args:
            entity: Entity to update
            **kwargs: New attribute values
            
        Returns:
            Updated entity
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating {self.model_class.__name__}: {str(e)}")
            raise
    
    def delete(self, entity: T) -> bool:
        """
        Delete an entity.
        
        Args:
            entity: Entity to delete
            
        Returns:
            True if successful
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting {self.model_class.__name__}: {str(e)}")
            raise
    
    def delete_by_id(self, entity_id: Any) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if successful, False if entity not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        entity = self.get_by_id(entity_id)
        if entity is None:
            return False
        
        return self.delete(entity)
    
    def count(self) -> int:
        """
        Count all entities.
        
        Returns:
            Number of entities
        """
        return self.model_class.query.count()
    
    def count_by(self, **kwargs) -> int:
        """
        Count entities by attributes.
        
        Args:
            **kwargs: Attributes to filter by
            
        Returns:
            Number of matching entities
        """
        return self.model_class.query.filter_by(**kwargs).count()
    
    def exists(self, **kwargs) -> bool:
        """
        Check if any entity exists with the given attributes.
        
        Args:
            **kwargs: Attributes to filter by
            
        Returns:
            True if at least one matching entity exists
        """
        return self.count_by(**kwargs) > 0 