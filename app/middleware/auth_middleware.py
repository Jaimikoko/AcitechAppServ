"""
Authentication middleware for AcidTech Flask API
Handles JWT token validation and role-based access control
"""
from functools import wraps
from flask import request, jsonify, g, current_app
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def auth_required(f):
    """
    Decorator to require authentication for route access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    'error': 'Authorization header is required',
                    'code': 'MISSING_AUTH_HEADER'
                }), 401
            
            # Extract token
            if not auth_header.startswith('Bearer '):
                return jsonify({
                    'error': 'Invalid authorization header format',
                    'code': 'INVALID_AUTH_FORMAT'
                }), 401
            
            token = auth_header.replace('Bearer ', '')
            
            # Validate token using auth service
            from app.services.auth_service import auth_service
            validation_result = auth_service.validate_token(token)
            
            if not validation_result.get('valid'):
                return jsonify({
                    'error': validation_result.get('error', 'Invalid token'),
                    'code': 'INVALID_TOKEN'
                }), 401
            
            # Store user information in request context
            g.current_user = validation_result.get('user')
            g.token_claims = validation_result.get('claims', {})
            
            logger.info(f"Authenticated user: {g.current_user.get('id')}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_ERROR'
            }), 401
    
    return decorated_function


def require_roles(required_roles: List[str]):
    """
    Decorator to require specific roles for route access
    Must be used after @auth_required
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Check if user is authenticated
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({
                        'error': 'Authentication required',
                        'code': 'NOT_AUTHENTICATED'
                    }), 401
                
                user_roles = g.current_user.get('roles', [])
                
                # Check if user has any of the required roles
                has_required_role = any(role in user_roles for role in required_roles)
                
                if not has_required_role:
                    logger.warning(
                        f"Access denied for user {g.current_user.get('id')} "
                        f"with roles {user_roles}. Required: {required_roles}"
                    )
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'code': 'INSUFFICIENT_PERMISSIONS',
                        'required_roles': required_roles
                    }), 403
                
                logger.info(
                    f"Role check passed for user {g.current_user.get('id')} "
                    f"with roles {user_roles}"
                )
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Role check error: {str(e)}")
                return jsonify({
                    'error': 'Permission check failed',
                    'code': 'PERMISSION_ERROR'
                }), 500
        
        return decorated_function
    return decorator


def optional_auth(f):
    """
    Decorator for optional authentication
    Populates g.current_user if token is valid, but doesn't fail if missing
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Initialize user as None
            g.current_user = None
            g.token_claims = {}
            
            # Get authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                # No auth provided, continue without user
                return f(*args, **kwargs)
            
            token = auth_header.replace('Bearer ', '')
            
            # Try to validate token
            from app.services.auth_service import auth_service
            validation_result = auth_service.validate_token(token)
            
            if validation_result.get('valid'):
                g.current_user = validation_result.get('user')
                g.token_claims = validation_result.get('claims', {})
                logger.info(f"Optional auth - authenticated user: {g.current_user.get('id')}")
            else:
                logger.info("Optional auth - invalid token, continuing without user")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Optional auth error: {str(e)}")
            # Continue without user in case of error
            g.current_user = None
            g.token_claims = {}
            return f(*args, **kwargs)
    
    return decorated_function


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user from request context
    """
    return getattr(g, 'current_user', None)


def get_current_user_id() -> Optional[str]:
    """
    Get current authenticated user ID
    """
    user = get_current_user()
    return user.get('id') if user else None


def get_current_user_roles() -> List[str]:
    """
    Get current authenticated user roles
    """
    user = get_current_user()
    return user.get('roles', []) if user else []


def has_role(role: str) -> bool:
    """
    Check if current user has specific role
    """
    return role in get_current_user_roles()


def is_admin() -> bool:
    """
    Check if current user is admin
    """
    return has_role('admin')


def check_resource_access(resource_user_id: str, allow_admin: bool = True) -> bool:
    """
    Check if current user can access a resource owned by another user
    """
    current_user_id = get_current_user_id()
    
    if not current_user_id:
        return False
    
    # User can access their own resources
    if current_user_id == resource_user_id:
        return True
    
    # Admin can access all resources if allowed
    if allow_admin and is_admin():
        return True
    
    return False


def require_resource_access(resource_user_id_key: str = 'user_id', allow_admin: bool = True):
    """
    Decorator to require access to a specific user's resource
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get resource user ID from kwargs or request data
                resource_user_id = kwargs.get(resource_user_id_key)
                
                if not resource_user_id:
                    # Try to get from request JSON
                    if request.is_json:
                        data = request.get_json()
                        resource_user_id = data.get(resource_user_id_key)
                
                if not resource_user_id:
                    return jsonify({
                        'error': 'Resource user ID not found',
                        'code': 'MISSING_RESOURCE_USER_ID'
                    }), 400
                
                if not check_resource_access(resource_user_id, allow_admin):
                    return jsonify({
                        'error': 'Cannot access this resource',
                        'code': 'RESOURCE_ACCESS_DENIED'
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Resource access check error: {str(e)}")
                return jsonify({
                    'error': 'Resource access check failed',
                    'code': 'ACCESS_CHECK_ERROR'
                }), 500
        
        return decorated_function
    return decorator