"""
Purchase Orders routes for AcidTech Flask API
Manages purchase order operations and data
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

purchase_orders_bp = Blueprint('purchase_orders', __name__)

# Mock data for demonstration
mock_purchase_orders = [
    {
        'id': 'po-001',
        'vendor': 'Tech Solutions Inc',
        'amount': 15750.00,
        'status': 'pending',
        'date': '2024-01-15',
        'items': ['Software Licenses', 'Hardware Components']
    },
    {
        'id': 'po-002', 
        'vendor': 'Office Supplies Co',
        'amount': 2340.50,
        'status': 'approved',
        'date': '2024-01-14',
        'items': ['Office Furniture', 'Stationery']
    }
]


@purchase_orders_bp.route('/', methods=['GET'])
def get_purchase_orders():
    """
    Get all purchase orders
    TODO: Integrate with actual database
    """
    return jsonify({
        'purchase_orders': mock_purchase_orders,
        'total': len(mock_purchase_orders),
        'timestamp': datetime.utcnow().isoformat()
    })


@purchase_orders_bp.route('/<string:po_id>', methods=['GET'])
def get_purchase_order(po_id):
    """
    Get specific purchase order by ID
    TODO: Implement database query
    """
    po = next((po for po in mock_purchase_orders if po['id'] == po_id), None)
    
    if not po:
        return jsonify({
            'error': 'Purchase order not found',
            'po_id': po_id
        }), 404
    
    return jsonify({
        'purchase_order': po,
        'timestamp': datetime.utcnow().isoformat()
    })


@purchase_orders_bp.route('/', methods=['POST'])
def create_purchase_order():
    """
    Create new purchase order
    TODO: Implement database insertion
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vendor', 'amount', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create new PO
        new_po = {
            'id': f'po-{str(uuid.uuid4())[:8]}',
            'vendor': data['vendor'],
            'amount': float(data['amount']),
            'status': 'pending',
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'items': data['items']
        }
        
        # Add to mock data (TODO: Save to database)
        mock_purchase_orders.append(new_po)
        
        return jsonify({
            'message': 'Purchase order created successfully',
            'purchase_order': new_po,
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create purchase order',
            'message': str(e)
        }), 500


@purchase_orders_bp.route('/<string:po_id>/status', methods=['PUT'])
def update_purchase_order_status(po_id):
    """
    Update purchase order status
    TODO: Implement database update
    """
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'error': 'Status is required'
            }), 400
        
        # Find and update PO
        po = next((po for po in mock_purchase_orders if po['id'] == po_id), None)
        if not po:
            return jsonify({
                'error': 'Purchase order not found'
            }), 404
        
        po['status'] = new_status
        
        return jsonify({
            'message': 'Purchase order status updated',
            'purchase_order': po,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update purchase order',
            'message': str(e)
        }), 500