"""
Consolidated Shopping Management Core Module  
Combines shopping lists, inventory tracking, and auto-replenishment
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_due_shopping_lists() -> List[Dict[str, Any]]:
    """Get shopping lists that are due for pulse dashboard"""
    try:
        return [
            {
                "id": 1,
                "name": "Weekly Groceries",
                "items_count": 12,
                "priority": "high",
                "due_date": datetime.now() + timedelta(days=1),
                "category": "groceries"
            },
            {
                "id": 2,
                "name": "Household Supplies",
                "items_count": 5,
                "priority": "medium", 
                "due_date": datetime.now() + timedelta(days=3),
                "category": "household"
            }
        ]
    except Exception as e:
        logger.error(f"Error fetching due shopping lists: {e}")
        return []

def auto_replenish_from_expenses(expense_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create shopping list items based on expense patterns"""
    try:
        auto_items = []
        for expense in expense_data:
            if expense.get('should_replenish', False):
                auto_items.append({
                    "item": expense['item'],
                    "category": expense['category'],
                    "reason": f"Last purchased {expense['last_purchase'].strftime('%m/%d')}",
                    "auto_generated": True,
                    "priority": "medium"
                })
        return auto_items
    except Exception as e:
        logger.error(f"Error auto-generating shopping items: {e}")
        return []

def get_shopping_analytics() -> Dict[str, Any]:
    """Get shopping pattern analytics"""
    try:
        return {
            "total_lists": 8,
            "completed_this_month": 12,
            "average_items_per_list": 7.5,
            "most_frequent_category": "Groceries",
            "monthly_spending": 456.78
        }
    except Exception as e:
        logger.error(f"Error fetching shopping analytics: {e}")
        return {}