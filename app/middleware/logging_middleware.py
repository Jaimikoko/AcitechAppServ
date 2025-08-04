"""
Logging middleware for AcidTech Flask API
Handles request/response logging and system monitoring
"""
from flask import Flask, request, g
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def setup_request_logging(app: Flask):
    """
    Setup request/response logging middleware
    """
    
    @app.before_request
    def before_request():
        """Log request start and setup timing"""
        g.start_time = time.time()
        g.request_id = generate_request_id()
        
        # Log request
        logger.info(
            f"REQUEST START [{g.request_id}] {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
        
        # Log request details in debug mode
        if app.debug:
            logger.debug(
                f"REQUEST DETAILS [{g.request_id}] "
                f"Headers: {dict(request.headers)} "
                f"Args: {dict(request.args)} "
                f"Content-Type: {request.content_type}"
            )
    
    @app.after_request
    def after_request(response):
        """Log response and timing"""
        try:
            # Calculate response time
            response_time = None
            if hasattr(g, 'start_time'):
                response_time = (time.time() - g.start_time) * 1000  # Convert to ms
            
            request_id = getattr(g, 'request_id', 'unknown')
            
            # Determine log level based on status code
            if response.status_code >= 400:
                log_level = logging.ERROR if response.status_code >= 500 else logging.WARNING
            else:
                log_level = logging.INFO
            
            # Log response
            logger.log(
                log_level,
                f"REQUEST END [{request_id}] {request.method} {request.path} "
                f"-> {response.status_code} "
                f"({response_time:.2f}ms)" if response_time else ""
            )
            
            # Add custom headers
            response.headers['X-Request-ID'] = request_id
            if response_time:
                response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
            
            # Log to system logs if available
            try:
                from app.models.system_log import SystemLog
                
                # Create API log entry
                api_log = SystemLog.create_api_log(
                    method=request.method,
                    endpoint=request.path,
                    status_code=response.status_code,
                    user_id=getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None,
                    response_time=response_time
                )
                
                # Set additional context
                api_log.set_request_context(request)
                api_log.set_response_context(
                    status_code=response.status_code,
                    response_size=response.content_length,
                    response_time=response_time
                )
                api_log.correlation_id = request_id
                
                # TODO: Save to database
                # db_service.save_log(api_log)
                
            except Exception as e:
                logger.error(f"Failed to create system log: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in after_request logging: {str(e)}")
        
        return response
    
    @app.teardown_request
    def teardown_request(exception):
        """Handle request teardown and error logging"""
        if exception:
            request_id = getattr(g, 'request_id', 'unknown')
            logger.error(
                f"REQUEST ERROR [{request_id}] {request.method} {request.path} "
                f"Exception: {str(exception)}"
            )
            
            # Log exception to system logs
            try:
                from app.models.system_log import SystemLog
                
                error_log = SystemLog.create_error_log(
                    error=exception,
                    context=f"{request.method} {request.path}",
                    user_id=getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
                )
                error_log.correlation_id = request_id
                error_log.set_request_context(request)
                
                # TODO: Save to database
                # db_service.save_log(error_log)
                
            except Exception as e:
                logger.error(f"Failed to log exception: {str(e)}")


def generate_request_id() -> str:
    """Generate unique request ID"""
    import uuid
    return str(uuid.uuid4())[:8]


def setup_business_event_logging(app: Flask):
    """
    Setup business event logging helpers
    """
    
    def log_business_event(action: str, resource_type: str, resource_id: str, 
                          old_values: dict = None, new_values: dict = None):
        """Log business event"""
        try:
            from app.models.system_log import SystemLog
            
            user_id = getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
            request_id = getattr(g, 'request_id', None)
            
            business_log = SystemLog.create_business_log(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user_id
            )
            
            business_log.set_business_context(
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                old_values=old_values,
                new_values=new_values
            )
            
            business_log.correlation_id = request_id
            
            # TODO: Save to database
            # db_service.save_log(business_log)
            
            logger.info(
                f"BUSINESS EVENT [{request_id}] {action} {resource_type} {resource_id} "
                f"by user {user_id}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log business event: {str(e)}")
    
    # Make the function available in Flask app context
    app.log_business_event = log_business_event


def setup_security_logging(app: Flask):
    """
    Setup security event logging
    """
    
    def log_security_event(event_type: str, message: str, severity: str = 'INFO',
                          user_id: str = None, ip_address: str = None):
        """Log security event"""
        try:
            from app.models.system_log import SystemLog
            
            user_id = user_id or (getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None)
            ip_address = ip_address or request.remote_addr
            request_id = getattr(g, 'request_id', None)
            
            security_log = SystemLog(
                level=severity,
                message=message,
                event_type=SystemLog.SECURITY_EVENT
            )
            
            security_log.user_id = user_id
            security_log.ip_address = ip_address
            security_log.correlation_id = request_id
            security_log.add_tag('security')
            security_log.add_tag(event_type)
            
            # TODO: Save to database
            # db_service.save_log(security_log)
            
            logger.log(
                getattr(logging, severity, logging.INFO),
                f"SECURITY EVENT [{request_id}] {event_type}: {message} "
                f"(user: {user_id}, ip: {ip_address})"
            )
            
            # For high-severity events, also log to separate security log
            if severity in ['ERROR', 'FATAL']:
                security_logger = logging.getLogger('security')
                security_logger.error(
                    f"HIGH SEVERITY SECURITY EVENT: {event_type} - {message} "
                    f"(user: {user_id}, ip: {ip_address})"
                )
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    # Make the function available in Flask app context
    app.log_security_event = log_security_event


def setup_performance_logging(app: Flask):
    """
    Setup performance monitoring
    """
    
    @app.before_request
    def setup_performance_tracking():
        """Setup performance tracking"""
        g.perf_start = time.time()
        g.perf_counters = {
            'db_queries': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def track_db_query(query_time: float):
        """Track database query performance"""
        if hasattr(g, 'perf_counters'):
            g.perf_counters['db_queries'] += 1
            
            if not hasattr(g, 'db_query_time'):
                g.db_query_time = 0
            g.db_query_time += query_time
    
    def track_api_call(call_time: float):
        """Track external API call performance"""
        if hasattr(g, 'perf_counters'):
            g.perf_counters['api_calls'] += 1
            
            if not hasattr(g, 'api_call_time'):
                g.api_call_time = 0
            g.api_call_time += call_time
    
    def track_cache_hit():
        """Track cache hit"""
        if hasattr(g, 'perf_counters'):
            g.perf_counters['cache_hits'] += 1
    
    def track_cache_miss():
        """Track cache miss"""
        if hasattr(g, 'perf_counters'):
            g.perf_counters['cache_misses'] += 1
    
    @app.after_request
    def log_performance_metrics(response):
        """Log performance metrics"""
        try:
            if hasattr(g, 'perf_start') and hasattr(g, 'perf_counters'):
                total_time = (time.time() - g.perf_start) * 1000  # ms
                
                # Log performance metrics for slow requests
                if total_time > 1000:  # Log requests taking more than 1 second
                    metrics = {
                        'total_time_ms': total_time,
                        'db_queries': g.perf_counters['db_queries'],
                        'db_time_ms': getattr(g, 'db_query_time', 0) * 1000,
                        'api_calls': g.perf_counters['api_calls'],
                        'api_time_ms': getattr(g, 'api_call_time', 0) * 1000,
                        'cache_hits': g.perf_counters['cache_hits'],
                        'cache_misses': g.perf_counters['cache_misses']
                    }
                    
                    request_id = getattr(g, 'request_id', 'unknown')
                    logger.warning(
                        f"SLOW REQUEST [{request_id}] {request.method} {request.path} "
                        f"took {total_time:.2f}ms - Metrics: {metrics}"
                    )
        
        except Exception as e:
            logger.error(f"Error logging performance metrics: {str(e)}")
        
        return response
    
    # Make tracking functions available
    app.track_db_query = track_db_query
    app.track_api_call = track_api_call
    app.track_cache_hit = track_cache_hit
    app.track_cache_miss = track_cache_miss