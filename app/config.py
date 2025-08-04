"""
Configuration settings for AcidTech Flask API
Handles different environment configurations
"""
import os
from typing import Dict, Any
from datetime import timedelta


class Config:
    """Base configuration class"""
    
    # Flask Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'acidtech-default-secret-key-change-in-production'
    FLASK_APP = os.environ.get('FLASK_APP') or 'run.py'
    
    # Server Configuration
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8000)
    
    # Azure AD B2C Configuration
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
    AZURE_B2C_AUTHORITY = os.environ.get('AZURE_B2C_AUTHORITY')
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASE_CONNECTION_STRING = os.environ.get('DATABASE_CONNECTION_STRING')
    
    # External API Keys
    NANONETS_API_KEY = os.environ.get('NANONETS_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES') or 3600))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES') or 86400))
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else ['*']
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/acidtech.log'
    
    # Pagination
    PAGINATION_PER_PAGE = 50
    MAX_PAGINATION_PER_PAGE = 500
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "100/hour"
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Development Database (SQLite)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///acidtech_dev.db'
    
    # Relaxed CORS for development
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:8000',
        'http://127.0.0.1:8000'
    ]
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    
    # Disable CSRF for development API testing
    WTF_CSRF_ENABLED = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Setup development logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/acidtech_dev.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.DEBUG)
            app.logger.info('AcidTech Flask API - Development mode')


class ProductionConfig(Config):
    """Production environment configuration"""
    
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Production Database (Azure SQL)
    DATABASE_CONNECTION_STRING = os.environ.get('DATABASE_CONNECTION_STRING')
    
    # Strict CORS for production
    CORS_ORIGINS = [
        'https://acidtech-prod-app.azurewebsites.net',
        'https://fintraqx.b2clogin.com'
    ]
    
    # Production logging
    LOG_LEVEL = 'INFO'
    
    # Enhanced security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting for production
    RATELIMIT_DEFAULT = "60/hour"
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Setup production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/acidtech_prod.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AcidTech Flask API - Production mode')


class TestingConfig(Config):
    """Testing environment configuration"""
    
    TESTING = True
    DEBUG = True
    FLASK_ENV = 'testing'
    
    # Testing Database (in-memory SQLite)
    DATABASE_URL = 'sqlite:///:memory:'
    DATABASE_CONNECTION_STRING = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting for testing
    RATELIMIT_ENABLED = False
    
    # Mock external APIs for testing
    NANONETS_API_KEY = 'mock-nanonets-key'
    OPENAI_API_KEY = 'mock-openai-key'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


def validate_config() -> Dict[str, Any]:
    """Validate current configuration and return status"""
    current_config = get_config()
    
    validation_results = {
        'valid': True,
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'issues': [],
        'warnings': []
    }
    
    # Check required settings
    required_settings = {
        'SECRET_KEY': current_config.SECRET_KEY,
        'AZURE_TENANT_ID': current_config.AZURE_TENANT_ID,
        'AZURE_CLIENT_ID': current_config.AZURE_CLIENT_ID,
        'AZURE_B2C_AUTHORITY': current_config.AZURE_B2C_AUTHORITY
    }
    
    for setting_name, setting_value in required_settings.items():
        if not setting_value or setting_value.startswith('your-') or setting_value == 'acidtech-default-secret-key-change-in-production':
            validation_results['issues'].append(f'{setting_name} is not properly configured')
            validation_results['valid'] = False
    
    # Check optional settings
    optional_settings = {
        'NANONETS_API_KEY': current_config.NANONETS_API_KEY,
        'OPENAI_API_KEY': current_config.OPENAI_API_KEY
    }
    
    for setting_name, setting_value in optional_settings.items():
        if not setting_value or setting_value.startswith('your-'):
            validation_results['warnings'].append(f'{setting_name} is not configured (optional)')
    
    return validation_results