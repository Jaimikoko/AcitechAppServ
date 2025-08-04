"""
AcidTech Flask API
Flask factory pattern implementation with proper configuration management
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app(config_name=None):
    """Application factory pattern with configuration"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from app.config import config
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)
    
    # Initialize configuration
    config_class.init_app(app)
    
    # CORS configuration
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['*']),
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # Initialize middleware
    from app.middleware.logging_middleware import (
        setup_request_logging, 
        setup_business_event_logging,
        setup_security_logging,
        setup_performance_logging
    )
    from app.middleware.rate_limiting import setup_rate_limiting
    
    # Setup logging middleware
    setup_request_logging(app)
    setup_business_event_logging(app)
    setup_security_logging(app)
    setup_performance_logging(app)
    
    # Setup rate limiting
    setup_rate_limiting(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.purchase_orders import purchase_orders_bp
    from app.routes.transactions import transactions_bp
    from app.routes.system_logs import system_logs_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(purchase_orders_bp, url_prefix='/api/purchase-orders')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(system_logs_bp, url_prefix='/api/system-logs')
    
    # Root endpoint
    @app.route('/')
    def home():
        return jsonify({
            'message': '🚀 AcidTech Flask API funcionando',
            'version': '2.0.0',
            'environment': app.config.get('FLASK_ENV', 'development'),
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth',
                'purchase_orders': '/api/purchase-orders',
                'transactions': '/api/transactions',
                'system_logs': '/api/system-logs'
            },
            'features': {
                'authentication': 'Azure AD B2C',
                'database': 'Azure SQL / SQLite',
                'middleware': ['CORS', 'Rate Limiting', 'Logging', 'Auth'],
                'testing': 'pytest'
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Comprehensive health check endpoint"""
        from app.config import validate_config
        
        # Basic health info
        health_data = {
            'status': 'healthy',
            'service': 'AcidTech Flask API',
            'version': '2.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': app.config.get('FLASK_ENV', 'development')
        }
        
        # Configuration validation
        try:
            config_validation = validate_config()
            health_data['configuration'] = {
                'valid': config_validation['valid'],
                'environment': config_validation['environment']
            }
            if config_validation['issues']:
                health_data['configuration']['issues'] = config_validation['issues']
        except Exception as e:
            health_data['configuration'] = {'error': str(e)}
        
        # System info
        try:
            import psutil
            import os
            health_data['system'] = {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'process_id': os.getpid()
            }
        except ImportError:
            health_data['system'] = {'info': 'psutil not available'}
        except Exception as e:
            health_data['system'] = {'error': str(e)}
        
        return jsonify(health_data)
    
    # Configuration endpoint
    @app.route('/config')
    def config_info():
        """Get configuration information (non-sensitive)"""
        from app.config import validate_config
        
        try:
            config_validation = validate_config()
            return jsonify({
                'environment': config_validation['environment'],
                'valid': config_validation['valid'],
                'warnings': config_validation.get('warnings', []),
                'flask_env': app.config.get('FLASK_ENV'),
                'debug': app.config.get('DEBUG', False),
                'testing': app.config.get('TESTING', False),
                'features': {
                    'cors_enabled': True,
                    'rate_limiting_enabled': True,
                    'logging_enabled': True,
                    'authentication_enabled': True
                }
            })
        except Exception as e:
            return jsonify({
                'error': 'Failed to get configuration info',
                'message': str(e)
            }), 500
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'The request was invalid or malformed',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested endpoint does not exist',
            'status_code': 404,
            'available_endpoints': {
                'health': '/health',
                'config': '/config',
                'auth': '/api/auth',
                'transactions': '/api/transactions',
                'purchase_orders': '/api/purchase-orders',
                'system_logs': '/api/system-logs'
            }
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests, please try again later',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log the error
        app.logger.error(f'Internal server error: {str(error)}')
        
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    # Global exception handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        
        # Return JSON error for API calls
        return jsonify({
            'error': 'An unexpected error occurred',
            'message': str(e) if app.debug else 'Internal server error',
            'status_code': 500
        }), 500
    
    return app