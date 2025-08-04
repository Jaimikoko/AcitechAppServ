"""
System Log model for AcidTech Flask API
Handles system logging and audit trail
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base import BaseModel


class SystemLog(BaseModel):
    """
    System Log model for audit trail and monitoring
    """
    
    # Log levels
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    FATAL = 'FATAL'
    
    # Event types
    AUTH_EVENT = 'auth'
    API_REQUEST = 'api_request'
    DATABASE_EVENT = 'database'
    SYSTEM_EVENT = 'system'
    BUSINESS_EVENT = 'business'
    SECURITY_EVENT = 'security'
    
    def __init__(self, level: str = None, message: str = None, event_type: str = None):
        super().__init__()
        self.level = level or self.INFO
        self.message = message
        self.event_type = event_type or self.SYSTEM_EVENT
        self.timestamp = datetime.utcnow()
        
        # Request context
        self.user_id = None
        self.session_id = None
        self.ip_address = None
        self.user_agent = None
        
        # API context
        self.endpoint = None
        self.method = None
        self.status_code = None
        self.response_time = None
        self.request_size = None
        self.response_size = None
        
        # Error context
        self.error_code = None
        self.error_details = None
        self.stack_trace = None
        
        # Business context
        self.resource_id = None
        self.resource_type = None
        self.action = None
        self.old_values = None
        self.new_values = None
        
        # Additional metadata
        self.tags = []
        self.metadata = {}
        self.correlation_id = None
        
        # System context
        self.server_name = None
        self.process_id = None
        self.thread_id = None
        self.memory_usage = None
        self.cpu_usage = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log to dictionary"""
        data = super().to_dict()
        
        # Ensure timestamp is properly formatted
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        
        return data
    
    def validate(self) -> Dict[str, Any]:
        """Validate log entry data"""
        errors = []
        
        # Required fields
        if not self.level:
            errors.append('Log level is required')
        elif self.level not in [self.DEBUG, self.INFO, self.WARN, self.ERROR, self.FATAL]:
            errors.append('Invalid log level')
        
        if not self.message:
            errors.append('Log message is required')
        elif len(self.message.strip()) < 1:
            errors.append('Log message cannot be empty')
        
        # Event type validation
        valid_event_types = [
            self.AUTH_EVENT, self.API_REQUEST, self.DATABASE_EVENT,
            self.SYSTEM_EVENT, self.BUSINESS_EVENT, self.SECURITY_EVENT
        ]
        if self.event_type not in valid_event_types:
            errors.append('Invalid event type')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def add_tag(self, tag: str) -> None:
        """Add tag to log entry"""
        if tag and tag not in self.tags:
            self.tags.append(tag.strip().lower())
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata field"""
        if not isinstance(self.metadata, dict):
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata field"""
        if not isinstance(self.metadata, dict):
            return default
        return self.metadata.get(key, default)
    
    def set_request_context(self, request) -> None:
        """Set request context from Flask request object"""
        try:
            self.endpoint = request.endpoint
            self.method = request.method
            self.ip_address = request.remote_addr
            self.user_agent = request.headers.get('User-Agent', '')[:500]  # Limit length
            
            # Try to get content length
            self.request_size = request.content_length
            
        except Exception:
            # Ignore errors in context setting
            pass
    
    def set_response_context(self, status_code: int, response_size: int = None, 
                           response_time: float = None) -> None:
        """Set response context"""
        self.status_code = status_code
        self.response_size = response_size
        self.response_time = response_time
    
    def set_error_context(self, error: Exception, error_code: str = None) -> None:
        """Set error context from exception"""
        self.error_details = str(error)
        self.error_code = error_code or type(error).__name__
        
        # Get stack trace (limited length for storage)
        import traceback
        self.stack_trace = traceback.format_exc()[:5000]
    
    def set_business_context(self, resource_type: str, resource_id: str, 
                           action: str, old_values: Dict = None, 
                           new_values: Dict = None) -> None:
        """Set business event context"""
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.old_values = old_values
        self.new_values = new_values
        self.event_type = self.BUSINESS_EVENT
    
    def is_error(self) -> bool:
        """Check if this is an error log"""
        return self.level in [self.ERROR, self.FATAL]
    
    def is_security_event(self) -> bool:
        """Check if this is a security event"""
        return self.event_type == self.SECURITY_EVENT
    
    def get_severity_level(self) -> int:
        """Get numeric severity level for sorting/filtering"""
        severity_levels = {
            self.DEBUG: 1,
            self.INFO: 2,
            self.WARN: 3,
            self.ERROR: 4,
            self.FATAL: 5
        }
        return severity_levels.get(self.level, 2)
    
    @classmethod
    def get_schema(cls) -> Dict[str, str]:
        """Get database schema for SystemLog table"""
        return {
            'id': 'VARCHAR(36) PRIMARY KEY',
            'level': 'VARCHAR(10) NOT NULL',
            'message': 'TEXT NOT NULL',
            'event_type': 'VARCHAR(20) NOT NULL',
            'timestamp': 'DATETIME NOT NULL',
            'user_id': 'VARCHAR(36)',
            'session_id': 'VARCHAR(100)',
            'ip_address': 'VARCHAR(45)',
            'user_agent': 'VARCHAR(500)',
            'endpoint': 'VARCHAR(255)',
            'method': 'VARCHAR(10)',
            'status_code': 'INTEGER',
            'response_time': 'FLOAT',
            'request_size': 'INTEGER',
            'response_size': 'INTEGER',
            'error_code': 'VARCHAR(100)',
            'error_details': 'TEXT',
            'stack_trace': 'TEXT',
            'resource_id': 'VARCHAR(100)',
            'resource_type': 'VARCHAR(50)',
            'action': 'VARCHAR(50)',
            'old_values': 'TEXT',  # JSON
            'new_values': 'TEXT',  # JSON
            'tags': 'TEXT',  # JSON array
            'metadata': 'TEXT',  # JSON object
            'correlation_id': 'VARCHAR(100)',
            'server_name': 'VARCHAR(100)',
            'process_id': 'INTEGER',
            'thread_id': 'VARCHAR(50)',
            'memory_usage': 'FLOAT',
            'cpu_usage': 'FLOAT',
            'created_at': 'DATETIME NOT NULL',
            'updated_at': 'DATETIME NOT NULL'
        }
    
    @classmethod
    def create_auth_log(cls, level: str, message: str, user_id: str = None, 
                       ip_address: str = None) -> 'SystemLog':
        """Create authentication log entry"""
        log = cls(level=level, message=message, event_type=cls.AUTH_EVENT)
        log.user_id = user_id
        log.ip_address = ip_address
        return log
    
    @classmethod
    def create_api_log(cls, method: str, endpoint: str, status_code: int,
                      user_id: str = None, response_time: float = None) -> 'SystemLog':
        """Create API request log entry"""
        level = cls.ERROR if status_code >= 400 else cls.INFO
        message = f"{method} {endpoint} - {status_code}"
        
        log = cls(level=level, message=message, event_type=cls.API_REQUEST)
        log.method = method
        log.endpoint = endpoint
        log.status_code = status_code
        log.user_id = user_id
        log.response_time = response_time
        
        return log
    
    @classmethod
    def create_business_log(cls, action: str, resource_type: str, resource_id: str,
                          user_id: str = None, message: str = None) -> 'SystemLog':
        """Create business event log entry"""
        if not message:
            message = f"{action} {resource_type} {resource_id}"
        
        log = cls(level=cls.INFO, message=message, event_type=cls.BUSINESS_EVENT)
        log.action = action
        log.resource_type = resource_type
        log.resource_id = resource_id
        log.user_id = user_id
        
        return log
    
    @classmethod
    def create_error_log(cls, error: Exception, context: str = None,
                        user_id: str = None) -> 'SystemLog':
        """Create error log entry"""
        message = f"Error in {context}: {str(error)}" if context else str(error)
        
        log = cls(level=cls.ERROR, message=message, event_type=cls.SYSTEM_EVENT)
        log.set_error_context(error)
        log.user_id = user_id
        
        return log
    
    @classmethod
    def get_log_statistics(cls, logs: List['SystemLog']) -> Dict[str, Any]:
        """Get statistics from log entries"""
        stats = {
            'total_logs': len(logs),
            'by_level': {
                cls.DEBUG: 0,
                cls.INFO: 0,
                cls.WARN: 0,
                cls.ERROR: 0,
                cls.FATAL: 0
            },
            'by_event_type': {
                cls.AUTH_EVENT: 0,
                cls.API_REQUEST: 0,
                cls.DATABASE_EVENT: 0,
                cls.SYSTEM_EVENT: 0,
                cls.BUSINESS_EVENT: 0,
                cls.SECURITY_EVENT: 0
            },
            'error_rate': 0.0,
            'recent_errors': []
        }
        
        error_count = 0
        for log in logs:
            # Count by level
            if log.level in stats['by_level']:
                stats['by_level'][log.level] += 1
            
            # Count by event type
            if log.event_type in stats['by_event_type']:
                stats['by_event_type'][log.event_type] += 1
            
            # Track errors
            if log.is_error():
                error_count += 1
                if len(stats['recent_errors']) < 10:
                    stats['recent_errors'].append({
                        'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                        'level': log.level,
                        'message': log.message[:200],  # Truncate for summary
                        'error_code': log.error_code
                    })
        
        # Calculate error rate
        if len(logs) > 0:
            stats['error_rate'] = (error_count / len(logs)) * 100
        
        return stats
    
    def __repr__(self):
        return f"<SystemLog(id='{self.id}', level='{self.level}', event_type='{self.event_type}')>"