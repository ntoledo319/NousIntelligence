"""
Financial Routes - Comprehensive Financial Management
Banking integration, transaction tracking, budgeting, and investment monitoring
"""

import logging
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, session, render_template
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

# Create blueprint
financial_bp = Blueprint('financial', __name__, url_prefix='/financial')

# Mock data for development - replace with real banking APIs in production
SAMPLE_ACCOUNTS = [
    {
        'id': 'acc_001',
        'name': 'Main Checking',
        'type': 'checking',
        'balance': 2547.83,
        'currency': 'USD',
        'bank': 'Chase Bank',
        'last_updated': datetime.now(timezone.utc).isoformat()
    },
    {
        'id': 'acc_002', 
        'name': 'Savings Account',
        'type': 'savings',
        'balance': 12450.67,
        'currency': 'USD',
        'bank': 'Chase Bank',
        'last_updated': datetime.now(timezone.utc).isoformat()
    },
    {
        'id': 'acc_003',
        'name': 'Investment Portfolio',
        'type': 'investment',
        'balance': 45230.12,
        'currency': 'USD',
        'bank': 'Fidelity',
        'last_updated': datetime.now(timezone.utc).isoformat()
    }
]

SAMPLE_TRANSACTIONS = [
    {
        'id': 'txn_001',
        'account_id': 'acc_001',
        'amount': -45.67,
        'description': 'Grocery Store',
        'category': 'Food & Dining',
        'date': (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        'merchant': 'Whole Foods Market'
    },
    {
        'id': 'txn_002',
        'account_id': 'acc_001',
        'amount': -89.32,
        'description': 'Gas Station',
        'category': 'Transportation',
        'date': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        'merchant': 'Shell'
    },
    {
        'id': 'txn_003',
        'account_id': 'acc_002',
        'amount': 2500.00,
        'description': 'Salary Deposit',
        'category': 'Income',
        'date': (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
        'merchant': 'Employer Direct Deposit'
    }
]

SAMPLE_BUDGETS = [
    {
        'id': 'budget_001',
        'category': 'Food & Dining',
        'monthly_limit': 500.00,
        'spent_this_month': 234.56,
        'remaining': 265.44,
        'color': '#FF6B6B'
    },
    {
        'id': 'budget_002',
        'category': 'Transportation',
        'monthly_limit': 300.00,
        'spent_this_month': 189.32,
        'remaining': 110.68,
        'color': '#4ECDC4'
    },
    {
        'id': 'budget_003',
        'category': 'Entertainment',
        'monthly_limit': 200.00,
        'spent_this_month': 78.45,
        'remaining': 121.55,
        'color': '#95E1D3'
    }
]


@financial_bp.route('/')
def financial_dashboard():
    """Main financial dashboard"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return render_template('financial/login_required.html'), 401
        
        # Calculate totals
        total_balance = sum(acc['balance'] for acc in SAMPLE_ACCOUNTS)
        checking_balance = sum(acc['balance'] for acc in SAMPLE_ACCOUNTS if acc['type'] == 'checking')
        savings_balance = sum(acc['balance'] for acc in SAMPLE_ACCOUNTS if acc['type'] == 'savings')
        investment_balance = sum(acc['balance'] for acc in SAMPLE_ACCOUNTS if acc['type'] == 'investment')
        
        # Recent transactions
        recent_transactions = sorted(SAMPLE_TRANSACTIONS, key=lambda x: x['date'], reverse=True)[:5]
        
        # Budget summary
        total_budget = sum(b['monthly_limit'] for b in SAMPLE_BUDGETS)
        total_spent = sum(b['spent_this_month'] for b in SAMPLE_BUDGETS)
        
        return render_template('financial/dashboard.html',
                             accounts=SAMPLE_ACCOUNTS,
                             transactions=recent_transactions,
                             budgets=SAMPLE_BUDGETS,
                             totals={
                                 'balance': total_balance,
                                 'checking': checking_balance,
                                 'savings': savings_balance,
                                 'investment': investment_balance,
                                 'budget_total': total_budget,
                                 'budget_spent': total_spent,
                                 'budget_remaining': total_budget - total_spent
                             })
    
    except Exception as e:
        logger.error(f"Error loading financial dashboard: {str(e)}")
        return render_template('error.html', error="Failed to load financial dashboard"), 500


@financial_bp.route('/api/accounts')
def get_accounts():
    """Get user's financial accounts"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        return jsonify({
            'success': True,
            'accounts': SAMPLE_ACCOUNTS,
            'total_balance': sum(acc['balance'] for acc in SAMPLE_ACCOUNTS),
            'last_updated': datetime.now(timezone.utc).isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting accounts: {str(e)}")
        return jsonify({'error': 'Failed to retrieve accounts'}), 500


@financial_bp.route('/api/transactions')
def get_transactions():
    """Get transaction history"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get query parameters
        account_id = request.args.get('account_id')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        
        # Filter transactions
        filtered_transactions = SAMPLE_TRANSACTIONS
        
        if account_id:
            filtered_transactions = [t for t in filtered_transactions if t['account_id'] == account_id]
        
        if category:
            filtered_transactions = [t for t in filtered_transactions if t['category'] == category]
        
        # Sort by date and limit
        sorted_transactions = sorted(filtered_transactions, key=lambda x: x['date'], reverse=True)[:limit]
        
        return jsonify({
            'success': True,
            'transactions': sorted_transactions,
            'total_count': len(filtered_transactions)
        })
    
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({'error': 'Failed to retrieve transactions'}), 500


@financial_bp.route('/api/budgets')
def get_budgets():
    """Get budget information"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        return jsonify({
            'success': True,
            'budgets': SAMPLE_BUDGETS,
            'total_limit': sum(b['monthly_limit'] for b in SAMPLE_BUDGETS),
            'total_spent': sum(b['spent_this_month'] for b in SAMPLE_BUDGETS)
        })
    
    except Exception as e:
        logger.error(f"Error getting budgets: {str(e)}")
        return jsonify({'error': 'Failed to retrieve budgets'}), 500


@financial_bp.route('/api/budgets/<budget_id>', methods=['PUT'])
def update_budget(budget_id):
    """Update budget limits"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        new_limit = data.get('monthly_limit')
        
        if not new_limit or new_limit <= 0:
            return jsonify({'error': 'Invalid budget limit'}), 400
        
        # Find and update budget
        for budget in SAMPLE_BUDGETS:
            if budget['id'] == budget_id:
                budget['monthly_limit'] = new_limit
                budget['remaining'] = new_limit - budget['spent_this_month']
                
                return jsonify({
                    'success': True,
                    'budget': budget
                })
        
        return jsonify({'error': 'Budget not found'}), 404
    
    except Exception as e:
        logger.error(f"Error updating budget: {str(e)}")
        return jsonify({'error': 'Failed to update budget'}), 500


@financial_bp.route('/api/spending-analysis')
def spending_analysis():
    """Get spending analysis and insights"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Calculate spending by category
        category_spending = {}
        for transaction in SAMPLE_TRANSACTIONS:
            if transaction['amount'] < 0:  # Only expenses
                category = transaction['category']
                amount = abs(transaction['amount'])
                category_spending[category] = category_spending.get(category, 0) + amount
        
        # Generate insights
        insights = []
        
        # High spending categories
        if category_spending:
            highest_category = max(category_spending.items(), key=lambda x: x[1])
            insights.append(f"Your highest spending category is {highest_category[0]} at ${highest_category[1]:.2f}")
        
        # Budget warnings
        for budget in SAMPLE_BUDGETS:
            usage_percent = (budget['spent_this_month'] / budget['monthly_limit']) * 100
            if usage_percent > 80:
                insights.append(f"Warning: You've used {usage_percent:.1f}% of your {budget['category']} budget")
        
        return jsonify({
            'success': True,
            'category_spending': category_spending,
            'insights': insights,
            'analysis_date': datetime.now(timezone.utc).isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in spending analysis: {str(e)}")
        return jsonify({'error': 'Failed to analyze spending'}), 500


@financial_bp.route('/api/investment-summary')
def investment_summary():
    """Get investment portfolio summary"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Sample investment data
        investments = [
            {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'shares': 50,
                'current_price': 185.32,
                'total_value': 9266.00,
                'gain_loss': 876.50,
                'gain_loss_percent': 10.45
            },
            {
                'symbol': 'GOOGL',
                'name': 'Alphabet Inc.',
                'shares': 25,
                'current_price': 142.56,
                'total_value': 3564.00,
                'gain_loss': -234.75,
                'gain_loss_percent': -6.18
            },
            {
                'symbol': 'TSLA',
                'name': 'Tesla Inc.',
                'shares': 30,
                'current_price': 245.67,
                'total_value': 7370.10,
                'gain_loss': 1245.30,
                'gain_loss_percent': 20.33
            }
        ]
        
        total_value = sum(inv['total_value'] for inv in investments)
        total_gain_loss = sum(inv['gain_loss'] for inv in investments)
        
        return jsonify({
            'success': True,
            'investments': investments,
            'portfolio_summary': {
                'total_value': total_value,
                'total_gain_loss': total_gain_loss,
                'total_gain_loss_percent': (total_gain_loss / (total_value - total_gain_loss)) * 100,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting investment summary: {str(e)}")
        return jsonify({'error': 'Failed to retrieve investment data'}), 500


@financial_bp.route('/api/financial-goals')
def get_financial_goals():
    """Get user's financial goals"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Sample financial goals
        goals = [
            {
                'id': 'goal_001',
                'title': 'Emergency Fund',
                'target_amount': 10000.00,
                'current_amount': 6500.00,
                'target_date': '2024-12-31',
                'category': 'savings',
                'progress': 65.0
            },
            {
                'id': 'goal_002',
                'title': 'Vacation Fund',
                'target_amount': 3000.00,
                'current_amount': 1200.00,
                'target_date': '2024-08-15',
                'category': 'travel',
                'progress': 40.0
            },
            {
                'id': 'goal_003',
                'title': 'New Car Down Payment',
                'target_amount': 5000.00,
                'current_amount': 2300.00,
                'target_date': '2024-10-01',
                'category': 'purchase',
                'progress': 46.0
            }
        ]
        
        return jsonify({
            'success': True,
            'goals': goals,
            'total_goals': len(goals),
            'total_target': sum(g['target_amount'] for g in goals),
            'total_saved': sum(g['current_amount'] for g in goals)
        })
    
    except Exception as e:
        logger.error(f"Error getting financial goals: {str(e)}")
        return jsonify({'error': 'Failed to retrieve financial goals'}), 500


@financial_bp.route('/api/financial-goals', methods=['POST'])
def create_financial_goal():
    """Create a new financial goal"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'target_amount', 'target_date', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new goal
        new_goal = {
            'id': f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': data['title'],
            'target_amount': float(data['target_amount']),
            'current_amount': float(data.get('current_amount', 0)),
            'target_date': data['target_date'],
            'category': data['category'],
            'progress': 0.0,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Calculate progress
        if new_goal['target_amount'] > 0:
            new_goal['progress'] = (new_goal['current_amount'] / new_goal['target_amount']) * 100
        
        return jsonify({
            'success': True,
            'goal': new_goal
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating financial goal: {str(e)}")
        return jsonify({'error': 'Failed to create financial goal'}), 500


@financial_bp.route('/accounts')
def accounts_page():
    """Accounts management page"""
    return render_template('financial/accounts.html', accounts=SAMPLE_ACCOUNTS)


@financial_bp.route('/transactions')
def transactions_page():
    """Transactions history page"""
    return render_template('financial/transactions.html', transactions=SAMPLE_TRANSACTIONS)


@financial_bp.route('/budgets')
def budgets_page():
    """Budget management page"""
    return render_template('financial/budgets.html', budgets=SAMPLE_BUDGETS)


@financial_bp.route('/investments')
def investments_page():
    """Investment portfolio page"""
    return render_template('financial/investments.html')


@financial_bp.route('/goals')
def goals_page():
    """Financial goals page"""
    return render_template('financial/goals.html')


@financial_bp.route('/reports')
def reports_page():
    """Financial reports and analytics page"""
    return render_template('financial/reports.html')


# Error handlers
@financial_bp.errorhandler(404)
def financial_not_found(error):
    return render_template('financial/404.html'), 404


@financial_bp.errorhandler(500)
def financial_server_error(error):
    return render_template('financial/500.html'), 500


# Utility functions
def calculate_budget_progress():
    """Calculate budget progress for all categories"""
    progress = {}
    for budget in SAMPLE_BUDGETS:
        if budget['monthly_limit'] > 0:
            usage = (budget['spent_this_month'] / budget['monthly_limit']) * 100
            progress[budget['category']] = {
                'percentage': usage,
                'status': 'warning' if usage > 80 else 'good' if usage < 60 else 'caution'
            }
    return progress


def get_spending_trends():
    """Get spending trends over time"""
    # This would normally query transaction history from database
    # For now, return sample trend data
    return {
        'monthly_spending': [2450, 2678, 2134, 2567, 2890],
        'categories': ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping'],
        'trend': 'increasing'
    }


def generate_financial_insights():
    """Generate AI-powered financial insights"""
    insights = []
    
    # Budget analysis
    for budget in SAMPLE_BUDGETS:
        usage = (budget['spent_this_month'] / budget['monthly_limit']) * 100
        if usage > 90:
            insights.append({
                'type': 'warning',
                'message': f"You're close to exceeding your {budget['category']} budget",
                'action': 'Consider reducing spending in this category'
            })
    
    # Savings opportunities
    total_expenses = sum(abs(t['amount']) for t in SAMPLE_TRANSACTIONS if t['amount'] < 0)
    insights.append({
        'type': 'tip',
        'message': f"You spent ${total_expenses:.2f} on expenses this period",
        'action': 'Review transactions to identify potential savings'
    })
    
    return insights