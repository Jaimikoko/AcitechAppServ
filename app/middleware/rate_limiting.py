"""
Rate limiting middleware for AcidTech Flask API
Implements rate limiting to prevent abuse
"""
from flask import Flask, request, jsonify, g
import time
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SimpleRateLimiter:
    """
    Simple in-memory rate limiter
    For production, consider using Redis-based rate limiting
    """
    
    def __init__(self):
        self.requests = {}  # {key: [(timestamp, count), ...]}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Unique identifier for the client (IP, user ID, etc.)
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            (allowed, info) where info contains current usage statistics
        """
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time - window)
            self.last_cleanup = current_time
        
        # Get or create request history for this key
        if key not in self.requests:
            self.requests[key] = []
        
        request_history = self.requests[key]
        
        # Remove old requests outside the window
        request_history[:] = [
            (timestamp, count) for timestamp, count in request_history
            if current_time - timestamp < window
        ]
        
        # Count current requests in window
        current_requests = sum(count for _, count in request_history)
        
        # Check if limit exceeded
        if current_requests >= limit:
            info = {
                'allowed': False,
                'limit': limit,
                'current': current_requests,
                'window': window,
                'reset_time': min(timestamp + window for timestamp, _ in request_history) if request_history else current_time,
                'retry_after': min(timestamp + window for timestamp, _ in request_history) - current_time if request_history else 0
            }
            return False, info
        
        # Add current request
        request_history.append((current_time, 1))
        
        info = {
            'allowed': True,
            'limit': limit,
            'current': current_requests + 1,
            'window': window,
            'remaining': limit - current_requests - 1,
            'reset_time': current_time + window
        }
        
        return True, info
    
    def _cleanup_old_entries(self, cutoff_time: float):
        """Remove old entries from all keys"""
        for key in list(self.requests.keys()):
            self.requests[key] = [
                (timestamp, count) for timestamp, count in self.requests[key]
                if timestamp > cutoff_time
            ]
            
            # Remove keys with no recent requests
            if not self.requests[key]:
                del self.requests[key]


# Global rate limiter instance
rate_limiter = SimpleRateLimiter()


def setup_rate_limiting(app: Flask):
    """
    Setup rate limiting middleware
    """
    
    @app.before_request
    def check_rate_limit():
        """Check rate limit before processing request"""
        try:
            # Skip rate limiting for certain endpoints
            if should_skip_rate_limiting():
                return
            
            # Get rate limit configuration
            limit_config = get_rate_limit_config()
            if not limit_config:
                return
            
            # Generate rate limit key
            rate_limit_key = generate_rate_limit_key()
            
            # Check rate limit
            allowed, info = rate_limiter.is_allowed(
                key=rate_limit_key,
                limit=limit_config['limit'],
                window=limit_config['window']
            )
            
            # Store rate limit info in request context
            g.rate_limit_info = info
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for {rate_limit_key}: "
                    f"{info['current']}/{info['limit']} requests in {info['window']}s window"
                )
                
                # Log security event for potential abuse
                if hasattr(app, 'log_security_event'):
                    app.log_security_event(
                        event_type='rate_limit_exceeded',
                        message=f"Rate limit exceeded: {info['current']}/{info['limit']} requests",
                        severity='WARN',
                        ip_address=request.remote_addr
                    )
                
                # Return rate limit error
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {info["limit"]} per {info["window"]} seconds',
                    'limit': info['limit'],
                    'window': info['window'],
                    'current': info['current'],
                    'retry_after': int(info['retry_after'])
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(info['limit'])
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(int(info['reset_time']))
                response.headers['Retry-After'] = str(int(info['retry_after']))
                
                return response
                
        except Exception as e:
            logger.error(f"Error in rate limiting: {str(e)}")
            # Don't block requests if rate limiting fails
            pass
    
    @app.after_request
    def add_rate_limit_headers(response):
        """Add rate limit headers to response"""
        try:
            if hasattr(g, 'rate_limit_info'):
                info = g.rate_limit_info
                response.headers['X-RateLimit-Limit'] = str(info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
                response.headers['X-RateLimit-Reset'] = str(int(info['reset_time']))
                
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {str(e)}")
        
        return response


def should_skip_rate_limiting() -> bool:
    """
    Determine if rate limiting should be skipped for this request
    """
    # Skip for health check endpoints
    if request.endpoint in ['health', 'home']:
        return True
    
    # Skip for static files
    if request.endpoint and request.endpoint.startswith('static'):
        return True
    
    # Skip for certain user agents (internal monitoring, etc.)
    user_agent = request.headers.get('User-Agent', '').lower()
    if any(bot in user_agent for bot in ['monitor', 'health-check', 'uptime']):
        return True
    
    return False


def get_rate_limit_config() -> Optional[Dict[str, int]]:
    """
    Get rate limit configuration for current request
    """
    from flask import current_app
    
    # Default rate limits
    default_limits = {
        'limit': 100,  # requests
        'window': 3600  # per hour
    }
    
    # Get from app config
    app_limits = current_app.config.get('RATE_LIMITS', {})
    
    # Endpoint-specific limits
    endpoint = request.endpoint
    if endpoint and endpoint in app_limits:
        return app_limits[endpoint]
    
    # Method-specific limits
    method = request.method
    method_key = f'method_{method.lower()}'
    if method_key in app_limits:
        return app_limits[method_key]
    
    # Authenticated vs unauthenticated limits
    if hasattr(g, 'current_user') and g.current_user:
        auth_limits = app_limits.get('authenticated', default_limits)
        
        # Role-based limits
        user_roles = g.current_user.get('roles', [])
        if 'admin' in user_roles and 'admin' in app_limits:
            return app_limits['admin']
        elif 'premium' in user_roles and 'premium' in app_limits:
            return app_limits['premium']
        
        return auth_limits
    else:
        return app_limits.get('unauthenticated', default_limits)


def generate_rate_limit_key() -> str:
    """
    Generate unique key for rate limiting
    """
    # For authenticated users, use user ID
    if hasattr(g, 'current_user') and g.current_user:
        return f"user:{g.current_user['id']}"
    
    # For unauthenticated users, use IP address
    ip = request.remote_addr
    
    # Consider X-Forwarded-For header for load balancers
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
    
    return f"ip:{ip}"


def rate_limit(limit: int, window: int = 3600, key_func: Optional[callable] = None):
    """
    Decorator for applying rate limits to specific routes
    
    Args:
        limit: Maximum number of requests
        window: Time window in seconds (default: 1 hour)
        key_func: Function to generate custom rate limit key
    """
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Generate rate limit key
                if key_func:
                    rate_limit_key = key_func()
                else:
                    rate_limit_key = generate_rate_limit_key()
                
                # Check rate limit
                allowed, info = rate_limiter.is_allowed(
                    key=rate_limit_key,
                    limit=limit,
                    window=window
                )
                
                if not allowed:
                    logger.warning(
                        f"Rate limit exceeded for {rate_limit_key} on {request.endpoint}: "
                        f"{info['current']}/{info['limit']} requests in {info['window']}s window"
                    )
                    
                    response = jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many requests to this endpoint. Limit: {limit} per {window} seconds',
                        'limit': limit,
                        'window': window,
                        'current': info['current'],
                        'retry_after': int(info['retry_after'])
                    })
                    response.status_code = 429
                    response.headers['X-RateLimit-Limit'] = str(limit)
                    response.headers['X-RateLimit-Remaining'] = '0'
                    response.headers['X-RateLimit-Reset'] = str(int(info['reset_time']))
                    response.headers['Retry-After'] = str(int(info['retry_after']))
                    
                    return response
                
                # Store rate limit info for headers
                g.rate_limit_info = info
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Error in route rate limiting: {str(e)}")
                # Don't block requests if rate limiting fails
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# Common rate limit decorators
def rate_limit_strict(f):
    """Strict rate limit: 10 requests per minute"""
    return rate_limit(limit=10, window=60)(f)


def rate_limit_moderate(f):
    """Moderate rate limit: 30 requests per minute"""
    return rate_limit(limit=30, window=60)(f)


def rate_limit_loose(f):
    """Loose rate limit: 100 requests per hour"""
    return rate_limit(limit=100, window=3600)(f)