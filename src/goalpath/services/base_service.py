"""
Base Service Class
Provides common functionality for all service classes
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..database import get_db


class BaseService:
    """Base service class with common database operations"""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize service with optional database session"""
        self.db = db
        self._owns_session = False
        
        if self.db is None:
            # Create our own session if none provided
            self.db = next(get_db())
            self._owns_session = True
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup session if we own it"""
        if self._owns_session and self.db:
            self.db.close()
    
    def commit(self):
        """Commit current transaction"""
        if self.db:
            self.db.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        if self.db:
            self.db.rollback()
    
    def refresh(self, instance):
        """Refresh instance from database"""
        if self.db:
            self.db.refresh(instance)
            
    def add(self, instance):
        """Add instance to session"""
        if self.db:
            self.db.add(instance)
            
    def delete(self, instance):
        """Delete instance from session"""
        if self.db:
            self.db.delete(instance)