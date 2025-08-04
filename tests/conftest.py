"""
Test configuration and fixtures for AcidTech Flask API
"""
import pytest
import os
import tempfile
from app import create_app


@pytest.fixture
def app():
    """Create application for testing"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Override config for testing
    test_config = {
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    }
    
    app = create_app('testing')
    
    with app.app_context():
        # Initialize test database if needed
        pass
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def mock_user():
    """Create mock user for testing"""
    return {
        'id': 'test-user-123',
        'azure_id': 'azure-test-123',
        'email': 'test@acidtech.com',
        'name': 'Test User',
        'roles': ['user']
    }


@pytest.fixture
def mock_admin_user():
    """Create mock admin user for testing"""
    return {
        'id': 'admin-user-123',
        'azure_id': 'azure-admin-123',
        'email': 'admin@acidtech.com',
        'name': 'Admin User',
        'roles': ['admin', 'user']
    }


@pytest.fixture
def auth_headers(mock_user):
    """Create authentication headers for testing"""
    return {
        'Authorization': 'Bearer mock-token-123',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_auth_headers(mock_admin_user):
    """Create admin authentication headers for testing"""
    return {
        'Authorization': 'Bearer mock-admin-token-123',
        'Content-Type': 'application/json'
    }