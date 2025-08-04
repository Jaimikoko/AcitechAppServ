"""
Transaction model for AcidTech Flask API
Handles financial transaction data and operations
"""
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from decimal import Decimal
from .base import BaseModel


class Transaction(BaseModel):
    """
    Financial transaction model
    Supports both income and expense transactions
    """
    
    # Transaction types
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'
    
    # Transaction statuses
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    def __init__(self, transaction_type: str = None, amount: float = None, description: str = None):
        super().__init__()
        self.transaction_type = transaction_type  # income, expense, transfer
        self.amount = Decimal(str(amount)) if amount is not None else Decimal('0.00')
        self.description = description
        self.date = date.today()
        self.category = None
        self.account = None
        self.status = self.PENDING
        
        # Additional fields
        self.reference_number = None
        self.vendor = None
        self.customer = None
        self.tax_amount = Decimal('0.00')
        self.notes = None
        self.tags = []
        self.attachments = []
        
        # Reconciliation
        self.reconciled = False
        self.reconciled_date = None
        self.bank_reference = None
        
        # User tracking
        self.created_by = None
        self.approved_by = None
        self.approval_date = None
        
        # Accounting fields
        self.debit_account = None
        self.credit_account = None
        self.fiscal_year = None
        self.fiscal_period = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        data = super().to_dict()
        
        # Convert Decimal to float for JSON serialization
        if isinstance(data.get('amount'), Decimal):
            data['amount'] = float(data['amount'])
        if isinstance(data.get('tax_amount'), Decimal):
            data['tax_amount'] = float(data['tax_amount'])
        
        # Convert date to string
        if isinstance(data.get('date'), date):
            data['date'] = data['date'].isoformat()
        
        return data
    
    def validate(self) -> Dict[str, Any]:
        """Validate transaction data"""
        errors = []
        
        # Required fields
        if not self.transaction_type:
            errors.append('Transaction type is required')
        elif self.transaction_type not in [self.INCOME, self.EXPENSE, self.TRANSFER]:
            errors.append('Invalid transaction type')
        
        if self.amount is None:
            errors.append('Amount is required')
        elif self.amount == 0:
            errors.append('Amount cannot be zero')
        
        if not self.description:
            errors.append('Description is required')
        elif len(self.description.strip()) < 3:
            errors.append('Description must be at least 3 characters')
        
        if not self.account:
            errors.append('Account is required')
        
        # Business logic validation
        if self.transaction_type == self.EXPENSE and self.amount > 0:
            # Automatically make expense amounts negative
            self.amount = -abs(self.amount)
        
        if self.transaction_type == self.INCOME and self.amount < 0:
            # Income should be positive
            self.amount = abs(self.amount)
        
        # Date validation
        if self.date and self.date > date.today():
            errors.append('Transaction date cannot be in the future')
        
        # Tax amount validation
        if self.tax_amount and self.tax_amount < 0:
            errors.append('Tax amount cannot be negative')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def add_tag(self, tag: str) -> None:
        """Add tag to transaction"""
        if tag and tag not in self.tags:
            self.tags.append(tag.strip().lower())
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from transaction"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def add_attachment(self, filename: str, file_path: str, file_type: str) -> None:
        """Add attachment to transaction"""
        attachment = {
            'filename': filename,
            'file_path': file_path,
            'file_type': file_type,
            'uploaded_at': datetime.utcnow().isoformat()
        }
        self.attachments.append(attachment)
        self.updated_at = datetime.utcnow()
    
    def mark_reconciled(self, bank_reference: str = None) -> None:
        """Mark transaction as reconciled"""
        self.reconciled = True
        self.reconciled_date = datetime.utcnow()
        if bank_reference:
            self.bank_reference = bank_reference
        self.updated_at = datetime.utcnow()
    
    def approve(self, approved_by: str) -> None:
        """Approve transaction"""
        self.status = self.COMPLETED
        self.approved_by = approved_by
        self.approval_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason: str = None) -> None:
        """Cancel transaction"""
        self.status = self.CANCELLED
        if reason:
            self.notes = f"{self.notes or ''}\nCancelled: {reason}".strip()
        self.updated_at = datetime.utcnow()
    
    def calculate_total_with_tax(self) -> Decimal:
        """Calculate total amount including tax"""
        return self.amount + self.tax_amount
    
    def get_absolute_amount(self) -> Decimal:
        """Get absolute amount (always positive)"""
        return abs(self.amount)
    
    @classmethod
    def get_schema(cls) -> Dict[str, str]:
        """Get database schema for Transaction table"""
        return {
            'id': 'VARCHAR(36) PRIMARY KEY',
            'transaction_type': 'VARCHAR(20) NOT NULL',
            'amount': 'DECIMAL(15,2) NOT NULL',
            'description': 'VARCHAR(500) NOT NULL',
            'date': 'DATE NOT NULL',
            'category': 'VARCHAR(100)',
            'account': 'VARCHAR(100) NOT NULL',
            'status': 'VARCHAR(20) DEFAULT "pending"',
            'reference_number': 'VARCHAR(100)',
            'vendor': 'VARCHAR(255)',
            'customer': 'VARCHAR(255)',
            'tax_amount': 'DECIMAL(15,2) DEFAULT 0.00',
            'notes': 'TEXT',
            'tags': 'TEXT',  # JSON array
            'attachments': 'TEXT',  # JSON array
            'reconciled': 'BOOLEAN DEFAULT 0',
            'reconciled_date': 'DATETIME',
            'bank_reference': 'VARCHAR(100)',
            'created_by': 'VARCHAR(36)',
            'approved_by': 'VARCHAR(36)',
            'approval_date': 'DATETIME',
            'debit_account': 'VARCHAR(100)',
            'credit_account': 'VARCHAR(100)',
            'fiscal_year': 'INTEGER',
            'fiscal_period': 'INTEGER',
            'created_at': 'DATETIME NOT NULL',
            'updated_at': 'DATETIME NOT NULL'
        }
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get available transaction categories"""
        return [
            # Income categories
            'revenue', 'sales', 'consulting', 'interest', 'dividends', 'grants',
            
            # Expense categories
            'rent', 'utilities', 'office_supplies', 'software', 'marketing',
            'travel', 'meals', 'insurance', 'legal', 'accounting', 'taxes',
            'equipment', 'maintenance', 'banking_fees', 'other'
        ]
    
    @classmethod
    def get_summary_by_type(cls, transactions: List['Transaction']) -> Dict[str, Any]:
        """Get summary statistics by transaction type"""
        summary = {
            'total_income': Decimal('0.00'),
            'total_expenses': Decimal('0.00'),
            'net_income': Decimal('0.00'),
            'transaction_count': {
                'income': 0,
                'expense': 0,
                'total': len(transactions)
            }
        }
        
        for transaction in transactions:
            if transaction.transaction_type == cls.INCOME:
                summary['total_income'] += transaction.amount
                summary['transaction_count']['income'] += 1
            elif transaction.transaction_type == cls.EXPENSE:
                summary['total_expenses'] += abs(transaction.amount)
                summary['transaction_count']['expense'] += 1
        
        summary['net_income'] = summary['total_income'] - summary['total_expenses']
        
        # Convert Decimal to float for JSON serialization
        for key in ['total_income', 'total_expenses', 'net_income']:
            summary[key] = float(summary[key])
        
        return summary
    
    def __repr__(self):
        return f"<Transaction(id='{self.id}', type='{self.transaction_type}', amount={self.amount})>"