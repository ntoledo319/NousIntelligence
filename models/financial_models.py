"""
Financial Models

This module contains financial management models for the NOUS application,
supporting expense tracking, budgeting, and financial insights.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from models.database import db
import json

class BankAccount(db.Model):
    """User bank accounts for expense tracking"""
    __tablename__ = 'bank_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # checking, savings, credit
    account_number_masked = db.Column(db.String(20))  # Only last 4 digits
    bank_name = db.Column(db.String(100))
    current_balance = db.Column(db.Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('bank_accounts', lazy=True))
    # Transactions relationship defined in Transaction model via backref

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'account_number_masked': self.account_number_masked,
            'bank_name': self.bank_name,
            'current_balance': float(self.current_balance) if self.current_balance else 0,
            'is_active': self.is_active,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Transaction(db.Model):
    """Financial transactions"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense, transfer
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'))
    merchant = db.Column(db.String(100))
    transaction_date = db.Column(db.Date, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)
    tags = db.Column(db.JSON)  # Array of tags
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    account = db.relationship('BankAccount', backref=db.backref('transactions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'description': self.description,
            'category_id': self.category_id,
            'merchant': self.merchant,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'is_recurring': self.is_recurring,
            'tags': self.tags,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExpenseCategory(db.Model):
    """Categories for organizing expenses"""
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6366f1')
    icon = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'))
    is_system = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('expense_categories', lazy=True))
    parent = db.relationship('ExpenseCategory', remote_side=[id], backref='subcategories')
    transactions = db.relationship('Transaction', backref='category')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'parent_id': self.parent_id,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Budget(db.Model):
    """User budgets"""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    budget_type = db.Column(db.String(20), default='monthly')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    alert_threshold = db.Column(db.Float, default=0.8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('budgets', lazy=True))
    categories = db.relationship('BudgetCategory', backref='budget', cascade='all, delete-orphan')

    @hybrid_property
    def spent_amount(self):
        # This would be calculated from transactions
        return 0.0  # Placeholder

    @hybrid_property
    def remaining_amount(self):
        return float(self.total_amount) - self.spent_amount

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'budget_type': self.budget_type,
            'total_amount': float(self.total_amount),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'alert_threshold': self.alert_threshold,
            'spent_amount': self.spent_amount,
            'remaining_amount': self.remaining_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BudgetCategory(db.Model):
    """Budget allocations by category"""
    __tablename__ = 'budget_categories'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    allocated_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    category = db.relationship('ExpenseCategory')

    def to_dict(self):
        return {
            'id': self.id,
            'budget_id': self.budget_id,
            'category_id': self.category_id,
            'allocated_amount': float(self.allocated_amount),
            'category': self.category.to_dict() if self.category else None
        }

class Bill(db.Model):
    """Recurring bills and payments"""
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'))
    frequency = db.Column(db.String(20), default='monthly')  # weekly, monthly, quarterly, yearly
    due_day = db.Column(db.Integer)  # Day of month/week
    next_due_date = db.Column(db.Date)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'))
    is_active = db.Column(db.Boolean, default=True)
    is_autopay = db.Column(db.Boolean, default=False)
    reminder_days = db.Column(db.Integer, default=3)  # Days before due date to remind
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('bills', lazy=True))
    category = db.relationship('ExpenseCategory')
    account = db.relationship('BankAccount')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'amount': float(self.amount),
            'category_id': self.category_id,
            'frequency': self.frequency,
            'due_day': self.due_day,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'account_id': self.account_id,
            'is_active': self.is_active,
            'is_autopay': self.is_autopay,
            'reminder_days': self.reminder_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Investment(db.Model):
    """User investments and portfolio tracking"""
    __tablename__ = 'investments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)  # Stock symbol
    name = db.Column(db.String(200))
    investment_type = db.Column(db.String(50))  # stock, bond, crypto, etc.
    quantity = db.Column(db.Numeric(10, 4), default=0)
    average_cost = db.Column(db.Numeric(10, 2), default=0)
    current_price = db.Column(db.Numeric(10, 2), default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('investments', lazy=True))

    @hybrid_property
    def total_value(self):
        return float(self.quantity * self.current_price) if self.quantity and self.current_price else 0

    @hybrid_property
    def total_cost(self):
        return float(self.quantity * self.average_cost) if self.quantity and self.average_cost else 0

    @hybrid_property
    def gain_loss(self):
        return self.total_value - self.total_cost

    @hybrid_property
    def gain_loss_percentage(self):
        if self.total_cost > 0:
            return (self.gain_loss / self.total_cost) * 100
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'name': self.name,
            'investment_type': self.investment_type,
            'quantity': float(self.quantity) if self.quantity else 0,
            'average_cost': float(self.average_cost) if self.average_cost else 0,
            'current_price': float(self.current_price) if self.current_price else 0,
            'total_value': self.total_value,
            'total_cost': self.total_cost,
            'gain_loss': self.gain_loss,
            'gain_loss_percentage': self.gain_loss_percentage,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FinancialGoal(db.Model):
    """Financial goals and targets"""
    __tablename__ = 'financial_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    goal_type = db.Column(db.String(50))  # savings, debt_payoff, investment, etc.
    target_amount = db.Column(db.Numeric(12, 2), nullable=False)
    current_amount = db.Column(db.Numeric(12, 2), default=0)
    target_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('financial_goals', lazy=True))

    @hybrid_property
    def progress_percentage(self):
        if not self.target_amount or self.target_amount == 0:
            return 0
        return min(100, (float(self.current_amount) / float(self.target_amount)) * 100)

    @hybrid_property
    def remaining_amount(self):
        return float(self.target_amount) - float(self.current_amount)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'goal_type': self.goal_type,
            'target_amount': float(self.target_amount),
            'current_amount': float(self.current_amount),
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'is_completed': self.is_completed,
            'priority': self.priority,
            'progress_percentage': self.progress_percentage,
            'remaining_amount': self.remaining_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        } 