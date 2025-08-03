"""
AcidTech Flask API
Flask factory pattern implementation
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import datetime


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'acidtech-dev-key-2024')
    app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')
    
    # CORS configuration for Azure AD B2C
    CORS(app, origins=[
        'https://acidtech-prod-app.azurewebsites.net',
        'https://fintraqx.b2clogin.com',
        'http://localhost:3000'  # For development
    ])
    
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
            'environment': app.config['FLASK_ENV'],
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth',
                'purchase_orders': '/api/purchase-orders',
                'transactions': '/api/transactions',
                'system_logs': '/api/system-logs'
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'AcidTech Flask API',
            'version': '2.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': app.config['FLASK_ENV']
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested endpoint does not exist',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    return app