"""
User model for AcidTech Flask API
Handles user data and Azure AD B2C integration
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base import BaseModel


class User(BaseModel):
    """
    User model for Azure AD B2C users
    """
    
    def __init__(self, azure_id: str = None, email: str = None, name: str = None):
        super().__init__()
        self.azure_id = azure_id  # Azure AD B2C user ID
        self.email = email
        self.name = name
        self.given_name = None
        self.family_name = None
        self.roles = ['user']  # Default role
        self.tenant = 'fintraqx'
        self.is_active = True
        self.last_login = None
        self.preferences = {}
        
        # Business-specific fields
        self.company_name = None
        self.department = None
        self.position = None
        self.phone = None
        self.timezone = 'UTC'
        self.language = 'en'
        
        # Audit fields
        self.login_count = 0
        self.last_activity = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (safe for API responses)"""
        data = super().to_dict()
        
        # Remove sensitive fields
        safe_fields = [
            'id', 'azure_id', 'email', 'name', 'given_name', 'family_name',
            'roles', 'tenant', 'is_active', 'last_login', 'preferences',
            'company_name', 'department', 'position', 'phone', 'timezone',
            'language', 'created_at', 'updated_at', 'last_activity'
        ]
        
        return {key: data[key] for key in safe_fields if key in data}
    
    def validate(self) -> Dict[str, Any]:
        """Validate user data"""
        errors = []
        
        # Required fields
        if not self.azure_id:
            errors.append('Azure ID is required')
        
        if not self.email:
            errors.append('Email is required')
        elif '@' not in self.email:
            errors.append('Invalid email format')
        
        if not self.name:
            errors.append('Name is required')
        
        # Role validation
        valid_roles = ['user', 'admin', 'manager', 'accountant', 'viewer']
        for role in self.roles:
            if role not in valid_roles:
                errors.append(f'Invalid role: {role}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self.roles
    
    def add_role(self, role: str) -> bool:
        """Add role to user"""
        valid_roles = ['user', 'admin', 'manager', 'accountant', 'viewer']
        if role in valid_roles and role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_role(self, role: str) -> bool:
        """Remove role from user"""
        if role in self.roles and role != 'user':  # Cannot remove base 'user' role
            self.roles.remove(role)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_login(self) -> None:
        """Update login information"""
        self.last_login = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.login_count += 1
        self.updated_at = datetime.utcnow()
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set user preference"""
        if not isinstance(self.preferences, dict):
            self.preferences = {}
        self.preferences[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        if not isinstance(self.preferences, dict):
            return default
        return self.preferences.get(key, default)
    
    @classmethod
    def get_schema(cls) -> Dict[str, str]:
        """Get database schema for User table"""
        return {
            'id': 'VARCHAR(36) PRIMARY KEY',
            'azure_id': 'VARCHAR(100) UNIQUE NOT NULL',
            'email': 'VARCHAR(255) UNIQUE NOT NULL',
            'name': 'VARCHAR(255) NOT NULL',
            'given_name': 'VARCHAR(100)',
            'family_name': 'VARCHAR(100)',
            'roles': 'TEXT',  # JSON array
            'tenant': 'VARCHAR(100)',
            'is_active': 'BOOLEAN DEFAULT 1',
            'last_login': 'DATETIME',
            'preferences': 'TEXT',  # JSON object
            'company_name': 'VARCHAR(255)',
            'department': 'VARCHAR(100)',
            'position': 'VARCHAR(100)',
            'phone': 'VARCHAR(20)',
            'timezone': 'VARCHAR(50) DEFAULT "UTC"',
            'language': 'VARCHAR(10) DEFAULT "en"',
            'login_count': 'INTEGER DEFAULT 0',
            'last_activity': 'DATETIME',
            'created_at': 'DATETIME NOT NULL',
            'updated_at': 'DATETIME NOT NULL'
        }
    
    @classmethod
    def from_azure_claims(cls, claims: Dict[str, Any]) -> 'User':
        """Create User instance from Azure AD B2C claims"""
        user = cls()
        
        # Map Azure claims to user fields
        user.azure_id = claims.get('sub') or claims.get('oid')
        user.email = claims.get('emails', [claims.get('email')])[0] if claims.get('emails') else claims.get('email')
        user.name = claims.get('name', f"{claims.get('given_name', '')} {claims.get('family_name', '')}".strip())
        user.given_name = claims.get('given_name')
        user.family_name = claims.get('family_name')
        user.tenant = claims.get('tfp') or claims.get('acr') or 'fintraqx'
        
        # Set default role based on claims or tenant
        if claims.get('roles'):
            user.roles = claims['roles']
        
        return user
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', name='{self.name}')>"