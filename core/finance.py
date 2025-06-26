"""
Consolidated Finance Management Core Module
Combines budget tracking, expense management, and financial analytics
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from flask import session

logger = logging.getLogger(__name__)

def get_budget_status() -> List[Dict[str, Any]]:
    """Get current budget status for pulse dashboard"""
    try:
        # This would query actual budget data from the database
        budget_alerts = [
            {
                "category": "Groceries",
                "spent": 280.00,
                "budget": 300.00,
                "percentage": 93.3,
                "status": "critical",  # >90%
                "days_remaining": 5
            },
            {
                "category": "Entertainment", 
                "spent": 75.00,
                "budget": 100.00,
                "percentage": 75.0,
                "status": "warning",  # 70-90%
                "days_remaining": 5
            },
            {
                "category": "Transportation",
                "spent": 45.00,
                "budget": 80.00,
                "percentage": 56.25,
                "status": "good",  # <70%
                "days_remaining": 5
            }
        ]
        return budget_alerts
    except Exception as e:
        logger.error(f"Error fetching budget status: {e}")
        return []

def get_budget_heat_map_data() -> Dict[str, Any]:
    """Get budget utilization data for heat map visualization"""
    try:
        return {
            "categories": [
                {"name": "Groceries", "utilization": 93.3, "color_class": "budget-critical"},
                {"name": "Entertainment", "utilization": 75.0, "color_class": "budget-warning"},
                {"name": "Transportation", "utilization": 56.25, "color_class": "budget-good"},
                {"name": "Utilities", "utilization": 88.5, "color_class": "budget-warning"},
                {"name": "Healthcare", "utilization": 45.0, "color_class": "budget-good"}
            ]
        }
    except Exception as e:
        logger.error(f"Error generating budget heat map: {e}")
        return {"categories": []}

def get_expense_shopping_correlation() -> List[Dict[str, Any]]:
    """Get expenses that should trigger shopping list items"""
    try:
        # Items that are running low based on usage patterns
        return [
            {
                "item": "Coffee",
                "last_purchase": datetime.now() - timedelta(days=12),
                "average_days": 14,
                "should_replenish": True,
                "category": "Groceries"
            },
            {
                "item": "Toothpaste",
                "last_purchase": datetime.now() - timedelta(days=28),
                "average_days": 30,
                "should_replenish": True,
                "category": "Personal Care"
            }
        ]
    except Exception as e:
        logger.error(f"Error correlating expenses with shopping: {e}")
        return []

def calculate_budget_color_class(utilization_percentage: float) -> str:
    """Calculate CSS class for budget heat map coloring"""
    if utilization_percentage >= 90:
        return "budget-critical"  # Red
    elif utilization_percentage >= 70:
        return "budget-warning"   # Yellow
    else:
        return "budget-good"      # Green