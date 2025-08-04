"""
Base model class for AcidTech Flask API
Provides common functionality for all models
"""
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class BaseModel:
    """
    Base class for all data models
    Provides common functionality and validation
    """
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                result[key] = value
            else:
                result[key] = value
        return result
    
    def from_dict(self, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    def update(self, data: Dict[str, Any]) -> 'BaseModel':
        """Update model with new data"""
        self.updated_at = datetime.utcnow()
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        return self
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate model data
        Override in subclasses for specific validation
        """
        errors = []
        
        # Basic validation
        if not hasattr(self, 'id') or not self.id:
            errors.append('ID is required')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @classmethod
    def get_table_name(cls) -> str:
        """Get database table name for this model"""
        return cls.__name__.lower() + 's'
    
    @classmethod
    def get_schema(cls) -> Dict[str, str]:
        """
        Get database schema for this model
        Override in subclasses to define schema
        """
        return {
            'id': 'VARCHAR(36) PRIMARY KEY',
            'created_at': 'DATETIME',
            'updated_at': 'DATETIME'
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id='{self.id}')>"
    
    def __str__(self):
        return f"{self.__class__.__name__}: {self.id}"