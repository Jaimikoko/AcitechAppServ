"""
Basic tests for AcidTech Flask API
"""
import pytest
import json


class TestBasicEndpoints:
    """Test basic API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_home_endpoint(self, client):
        """Test home endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data
        assert data['endpoints']['health'] == '/health'
    
    def test_nonexistent_endpoint(self, client):
        """Test 404 handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Endpoint not found'


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_auth_validate_no_token(self, client):
        """Test auth validation without token"""
        response = client.post('/api/auth/validate')
        assert response.status_code == 401
    
    def test_auth_validate_with_mock_token(self, client, auth_headers):
        """Test auth validation with mock token"""
        response = client.post('/api/auth/validate', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'valid'
        assert 'user' in data
    
    def test_get_user_info(self, client, auth_headers):
        """Test get user info endpoint"""
        response = client.get('/api/auth/user', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['name'] == 'Demo User'


class TestTransactions:
    """Test transaction endpoints"""
    
    def test_get_transactions_no_auth(self, client):
        """Test getting transactions without authentication"""
        response = client.get('/api/transactions/')
        # Should return mock data for now
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)
    
    def test_create_transaction_valid(self, client):
        """Test creating valid transaction"""
        transaction_data = {
            'type': 'income',
            'amount': 1000.00,
            'description': 'Test income transaction',
            'category': 'revenue',
            'account': 'Test Account'
        }
        
        response = client.post('/api/transactions/', 
                             data=json.dumps(transaction_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['message'] == 'Transaction created successfully'
        assert 'transaction' in data
    
    def test_create_transaction_invalid(self, client):
        """Test creating invalid transaction"""
        transaction_data = {
            'type': 'invalid_type',  # Invalid type
            'amount': 1000.00
        }
        
        response = client.post('/api/transactions/', 
                             data=json.dumps(transaction_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_transaction_summary(self, client):
        """Test transaction summary endpoint"""
        response = client.get('/api/transactions/summary')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'summary' in data
        assert 'total_income' in data['summary']
        assert 'total_expenses' in data['summary']
        assert 'net_income' in data['summary']


class TestPurchaseOrders:
    """Test purchase order endpoints"""
    
    def test_get_purchase_orders(self, client):
        """Test getting purchase orders"""
        response = client.get('/api/purchase-orders/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'purchase_orders' in data
        assert isinstance(data['purchase_orders'], list)
    
    def test_create_purchase_order_valid(self, client):
        """Test creating valid purchase order"""
        po_data = {
            'vendor': 'Test Vendor',
            'amount': 500.00,
            'items': ['Test Item 1', 'Test Item 2']
        }
        
        response = client.post('/api/purchase-orders/', 
                             data=json.dumps(po_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['message'] == 'Purchase order created successfully'
        assert 'purchase_order' in data


class TestSystemLogs:
    """Test system logs endpoints"""
    
    def test_get_system_logs(self, client):
        """Test getting system logs"""
        response = client.get('/api/system-logs/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'logs' in data
        assert isinstance(data['logs'], list)
    
    def test_create_log_entry(self, client):
        """Test creating log entry"""
        log_data = {
            'level': 'INFO',
            'message': 'Test log message'
        }
        
        response = client.post('/api/system-logs/', 
                             data=json.dumps(log_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['message'] == 'Log entry created successfully'
    
    def test_get_log_statistics(self, client):
        """Test log statistics endpoint"""
        response = client.get('/api/system-logs/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'statistics' in data
        assert 'total_logs' in data['statistics']
        assert 'by_level' in data['statistics']