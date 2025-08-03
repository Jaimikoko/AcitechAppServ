"""
Transactions routes for AcidTech Flask API
Manages financial transaction operations
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import uuid

transactions_bp = Blueprint('transactions', __name__)

# Mock transaction data
mock_transactions = [
    {
        'id': 'txn-001',
        'type': 'income',
        'amount': 5000.00,
        'description': 'Client Payment - Invoice #INV-2024-001',
        'date': '2024-01-15',
        'category': 'revenue',
        'account': 'Business Checking'
    },
    {
        'id': 'txn-002',
        'type': 'expense',
        'amount': -1200.00,
        'description': 'Office Rent - January 2024',
        'date': '2024-01-14',
        'category': 'rent',
        'account': 'Business Checking'
    },
    {
        'id': 'txn-003',
        'type': 'expense',
        'amount': -450.00,
        'description': 'Software Subscription - Tools & Analytics',
        'date': '2024-01-13',
        'category': 'software',
        'account': 'Business Credit Card'
    }
]


@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    """
    Get all transactions with optional filtering
    TODO: Implement database query with proper filtering
    """
    # Get query parameters
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', default=50, type=int)
    
    filtered_transactions = mock_transactions.copy()
    
    # Apply filters (basic implementation)
    if transaction_type:
        filtered_transactions = [t for t in filtered_transactions if t['type'] == transaction_type]
    
    # Limit results
    filtered_transactions = filtered_transactions[:limit]
    
    return jsonify({
        'transactions': filtered_transactions,
        'total': len(filtered_transactions),
        'filters_applied': {
            'type': transaction_type,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@transactions_bp.route('/<string:txn_id>', methods=['GET'])
def get_transaction(txn_id):
    """
    Get specific transaction by ID
    TODO: Implement database query
    """
    transaction = next((t for t in mock_transactions if t['id'] == txn_id), None)
    
    if not transaction:
        return jsonify({
            'error': 'Transaction not found',
            'transaction_id': txn_id
        }), 404
    
    return jsonify({
        'transaction': transaction,
        'timestamp': datetime.utcnow().isoformat()
    })


@transactions_bp.route('/', methods=['POST'])
def create_transaction():
    """
    Create new transaction
    TODO: Implement database insertion and validation
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['type', 'amount', 'description', 'category', 'account']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate transaction type
        if data['type'] not in ['income', 'expense']:
            return jsonify({
                'error': 'Transaction type must be either "income" or "expense"'
            }), 400
        
        # Create new transaction
        new_transaction = {
            'id': f'txn-{str(uuid.uuid4())[:8]}',
            'type': data['type'],
            'amount': float(data['amount']),
            'description': data['description'],
            'date': data.get('date', datetime.utcnow().strftime('%Y-%m-%d')),
            'category': data['category'],
            'account': data['account']
        }
        
        # Ensure expense amounts are negative
        if new_transaction['type'] == 'expense' and new_transaction['amount'] > 0:
            new_transaction['amount'] = -new_transaction['amount']
        
        # Add to mock data (TODO: Save to database)
        mock_transactions.append(new_transaction)
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': new_transaction,
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create transaction',
            'message': str(e)
        }), 500


@transactions_bp.route('/summary', methods=['GET'])
def get_transaction_summary():
    """
    Get transaction summary and statistics
    TODO: Implement proper aggregation queries
    """
    try:
        # Calculate summary statistics
        total_income = sum(t['amount'] for t in mock_transactions if t['type'] == 'income')
        total_expenses = sum(abs(t['amount']) for t in mock_transactions if t['type'] == 'expense')
        net_income = total_income - total_expenses
        
        # Count transactions by type
        income_count = len([t for t in mock_transactions if t['type'] == 'income'])
        expense_count = len([t for t in mock_transactions if t['type'] == 'expense'])
        
        return jsonify({
            'summary': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_income': net_income,
                'transaction_count': {
                    'income': income_count,
                    'expenses': expense_count,
                    'total': len(mock_transactions)
                }
            },
            'period': {
                'start_date': '2024-01-01',  # TODO: Calculate from actual data
                'end_date': datetime.utcnow().strftime('%Y-%m-%d')
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate transaction summary',
            'message': str(e)
        }), 500