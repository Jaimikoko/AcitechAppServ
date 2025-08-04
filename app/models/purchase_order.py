"""
Purchase Order model for AcidTech Flask API
Handles purchase order data and workflow
"""
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from decimal import Decimal
from .base import BaseModel


class PurchaseOrder(BaseModel):
    """
    Purchase Order model for procurement management
    """
    
    # PO statuses
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    ORDERED = 'ordered'
    RECEIVED = 'received'
    CANCELLED = 'cancelled'
    
    # Priority levels
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    def __init__(self, vendor: str = None, amount: float = None):
        super().__init__()
        self.po_number = None  # Will be auto-generated
        self.vendor = vendor
        self.vendor_contact = None
        self.amount = Decimal(str(amount)) if amount is not None else Decimal('0.00')
        self.status = self.DRAFT
        self.priority = self.MEDIUM
        
        # Dates
        self.order_date = date.today()
        self.expected_delivery_date = None
        self.actual_delivery_date = None
        
        # Items and details
        self.items = []  # List of items/services
        self.description = None
        self.notes = None
        self.terms_conditions = None
        
        # Financial details
        self.subtotal = Decimal('0.00')
        self.tax_amount = Decimal('0.00')
        self.shipping_amount = Decimal('0.00')
        self.discount_amount = Decimal('0.00')
        self.total_amount = Decimal('0.00')
        
        # Approval workflow
        self.requested_by = None
        self.approved_by = None
        self.approval_date = None
        self.approval_notes = None
        
        # Delivery and tracking
        self.shipping_address = None
        self.tracking_number = None
        self.delivery_notes = None
        
        # Documents and attachments
        self.attachments = []
        self.receipts = []
        
        # Department and budget
        self.department = None
        self.budget_code = None
        self.project_code = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PO to dictionary"""
        data = super().to_dict()
        
        # Convert Decimal fields to float for JSON serialization
        decimal_fields = ['amount', 'subtotal', 'tax_amount', 'shipping_amount', 
                         'discount_amount', 'total_amount']
        for field in decimal_fields:
            if isinstance(data.get(field), Decimal):
                data[field] = float(data[field])
        
        # Convert date fields to string
        date_fields = ['order_date', 'expected_delivery_date', 'actual_delivery_date']
        for field in date_fields:
            if isinstance(data.get(field), date):
                data[field] = data[field].isoformat()
        
        return data
    
    def validate(self) -> Dict[str, Any]:
        """Validate purchase order data"""
        errors = []
        
        # Required fields
        if not self.vendor:
            errors.append('Vendor is required')
        
        if self.amount is None or self.amount <= 0:
            errors.append('Amount must be greater than zero')
        
        if not self.items or len(self.items) == 0:
            errors.append('At least one item is required')
        
        # Status validation
        valid_statuses = [self.DRAFT, self.PENDING, self.APPROVED, 
                         self.ORDERED, self.RECEIVED, self.CANCELLED]
        if self.status not in valid_statuses:
            errors.append('Invalid status')
        
        # Priority validation
        valid_priorities = [self.LOW, self.MEDIUM, self.HIGH, self.URGENT]
        if self.priority not in valid_priorities:
            errors.append('Invalid priority')
        
        # Date validation
        if self.expected_delivery_date and self.expected_delivery_date < self.order_date:
            errors.append('Expected delivery date cannot be before order date')
        
        # Financial validation
        if self.tax_amount < 0:
            errors.append('Tax amount cannot be negative')
        
        if self.shipping_amount < 0:
            errors.append('Shipping amount cannot be negative')
        
        if self.discount_amount < 0:
            errors.append('Discount amount cannot be negative')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def generate_po_number(self) -> str:
        """Generate unique PO number"""
        if not self.po_number:
            # Format: PO-YYYY-MMDD-XXXX
            today = date.today()
            prefix = f"PO-{today.year}-{today.strftime('%m%d')}"
            # In a real implementation, you'd query the database for the next sequence number
            sequence = str(hash(self.id))[-4:].zfill(4)
            self.po_number = f"{prefix}-{sequence}"
        return self.po_number
    
    def add_item(self, description: str, quantity: int, unit_price: float, 
                 unit: str = 'each') -> None:
        """Add item to purchase order"""
        item = {
            'description': description,
            'quantity': quantity,
            'unit_price': Decimal(str(unit_price)),
            'unit': unit,
            'total_price': Decimal(str(quantity)) * Decimal(str(unit_price)),
            'added_at': datetime.utcnow().isoformat()
        }
        self.items.append(item)
        self.calculate_totals()
        self.updated_at = datetime.utcnow()
    
    def remove_item(self, index: int) -> bool:
        """Remove item from purchase order"""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.calculate_totals()
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def calculate_totals(self) -> None:
        """Calculate all totals based on items and fees"""
        self.subtotal = sum(
            Decimal(str(item.get('total_price', 0))) 
            for item in self.items
        )
        
        self.total_amount = (
            self.subtotal + 
            self.tax_amount + 
            self.shipping_amount - 
            self.discount_amount
        )
        
        # Update main amount field
        self.amount = self.total_amount
        self.updated_at = datetime.utcnow()
    
    def approve(self, approved_by: str, notes: str = None) -> None:
        """Approve purchase order"""
        if self.status in [self.DRAFT, self.PENDING]:
            self.status = self.APPROVED
            self.approved_by = approved_by
            self.approval_date = datetime.utcnow()
            if notes:
                self.approval_notes = notes
            self.updated_at = datetime.utcnow()
    
    def reject(self, rejected_by: str, reason: str) -> None:
        """Reject purchase order"""
        self.status = self.CANCELLED
        self.approval_notes = f"Rejected by {rejected_by}: {reason}"
        self.updated_at = datetime.utcnow()
    
    def mark_ordered(self, tracking_number: str = None) -> None:
        """Mark PO as ordered"""
        if self.status == self.APPROVED:
            self.status = self.ORDERED
            if tracking_number:
                self.tracking_number = tracking_number
            self.updated_at = datetime.utcnow()
    
    def mark_received(self, delivery_notes: str = None) -> None:
        """Mark PO as received"""
        if self.status == self.ORDERED:
            self.status = self.RECEIVED
            self.actual_delivery_date = date.today()
            if delivery_notes:
                self.delivery_notes = delivery_notes
            self.updated_at = datetime.utcnow()
    
    def add_receipt(self, filename: str, file_path: str, amount: float) -> None:
        """Add receipt/invoice to PO"""
        receipt = {
            'filename': filename,
            'file_path': file_path,
            'amount': float(amount),
            'uploaded_at': datetime.utcnow().isoformat()
        }
        self.receipts.append(receipt)
        self.updated_at = datetime.utcnow()
    
    def get_status_color(self) -> str:
        """Get color code for status display"""
        status_colors = {
            self.DRAFT: '#gray',
            self.PENDING: '#yellow',
            self.APPROVED: '#blue',
            self.ORDERED: '#orange',
            self.RECEIVED: '#green',
            self.CANCELLED: '#red'
        }
        return status_colors.get(self.status, '#gray')
    
    def get_priority_level(self) -> int:
        """Get numeric priority level for sorting"""
        priority_levels = {
            self.LOW: 1,
            self.MEDIUM: 2,
            self.HIGH: 3,
            self.URGENT: 4
        }
        return priority_levels.get(self.priority, 2)
    
    @classmethod
    def get_schema(cls) -> Dict[str, str]:
        """Get database schema for PurchaseOrder table"""
        return {
            'id': 'VARCHAR(36) PRIMARY KEY',
            'po_number': 'VARCHAR(50) UNIQUE',
            'vendor': 'VARCHAR(255) NOT NULL',
            'vendor_contact': 'VARCHAR(255)',
            'amount': 'DECIMAL(15,2) NOT NULL',
            'status': 'VARCHAR(20) DEFAULT "draft"',
            'priority': 'VARCHAR(20) DEFAULT "medium"',
            'order_date': 'DATE NOT NULL',
            'expected_delivery_date': 'DATE',
            'actual_delivery_date': 'DATE',
            'items': 'TEXT',  # JSON array
            'description': 'TEXT',
            'notes': 'TEXT',
            'terms_conditions': 'TEXT',
            'subtotal': 'DECIMAL(15,2) DEFAULT 0.00',
            'tax_amount': 'DECIMAL(15,2) DEFAULT 0.00',
            'shipping_amount': 'DECIMAL(15,2) DEFAULT 0.00',
            'discount_amount': 'DECIMAL(15,2) DEFAULT 0.00',
            'total_amount': 'DECIMAL(15,2) DEFAULT 0.00',
            'requested_by': 'VARCHAR(36)',
            'approved_by': 'VARCHAR(36)',
            'approval_date': 'DATETIME',
            'approval_notes': 'TEXT',
            'shipping_address': 'TEXT',
            'tracking_number': 'VARCHAR(100)',
            'delivery_notes': 'TEXT',
            'attachments': 'TEXT',  # JSON array
            'receipts': 'TEXT',  # JSON array
            'department': 'VARCHAR(100)',
            'budget_code': 'VARCHAR(50)',
            'project_code': 'VARCHAR(50)',
            'created_at': 'DATETIME NOT NULL',
            'updated_at': 'DATETIME NOT NULL'
        }
    
    @classmethod
    def get_status_summary(cls, purchase_orders: List['PurchaseOrder']) -> Dict[str, Any]:
        """Get summary statistics by status"""
        summary = {
            'by_status': {
                cls.DRAFT: {'count': 0, 'total_amount': 0.0},
                cls.PENDING: {'count': 0, 'total_amount': 0.0},
                cls.APPROVED: {'count': 0, 'total_amount': 0.0},
                cls.ORDERED: {'count': 0, 'total_amount': 0.0},
                cls.RECEIVED: {'count': 0, 'total_amount': 0.0},
                cls.CANCELLED: {'count': 0, 'total_amount': 0.0}
            },
            'total_count': len(purchase_orders),
            'total_amount': 0.0
        }
        
        for po in purchase_orders:
            if po.status in summary['by_status']:
                summary['by_status'][po.status]['count'] += 1
                summary['by_status'][po.status]['total_amount'] += float(po.amount)
                summary['total_amount'] += float(po.amount)
        
        return summary
    
    def __repr__(self):
        return f"<PurchaseOrder(id='{self.id}', po_number='{self.po_number}', vendor='{self.vendor}', amount={self.amount})>"