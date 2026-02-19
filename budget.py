#!/usr/bin/env python3
"""
Budget tracking and alerts.

TODO: DELETE IF NOT USING BUDGET ALERTS
This entire file can be removed if you don't want budget tracking.
Also remove budget-related code from bot.py and config.py.
"""

from typing import Optional, Dict
from database import get_monthly_summary

# Default budget limits (can be customized per user)
DEFAULT_BUDGETS = {
    'groceries': 500,
    'transport': 200,
    'food_delivery': 150,
    'hawker': 200,
    'dining': 300,
    'petrol': 250,
    'shopping': 200,
    'utilities': 150,
    'healthcare': 100,
    'entertainment': 100,
    'others': 200
}


def check_budget(user_id: int, category: str, amount: float) -> Optional[str]:
    """
    Check if a transaction exceeds budget limits.
    
    Returns:
        Alert message if over budget, None otherwise
    """
    # Get current month's spending in this category
    summary = get_monthly_summary(user_id)
    current_spending = summary['by_category'].get(category, 0)
    
    # Get budget limit
    budget_limit = DEFAULT_BUDGETS.get(category, 200)
    
    # Calculate after this transaction
    new_total = current_spending + amount
    
    # Check thresholds
    if new_total > budget_limit:
        over_by = new_total - budget_limit
        return f"Over budget by ${over_by:.2f}! (Limit: ${budget_limit:.2f})"
    
    if new_total > budget_limit * 0.8:
        remaining = budget_limit - new_total
        return f"80% of budget used. ${remaining:.2f} remaining."
    
    return None


def set_budget(user_id: int, category: str, limit: float) -> bool:
    """
    Set a custom budget limit for a user.
    
    TODO: Store in database
    """
    # This would store user-specific budget overrides
    return True


def get_budget_status(user_id: int) -> Dict:
    """
    Get full budget status for all categories.
    
    Returns:
        Dictionary with budget vs actual for each category
    """
    summary = get_monthly_summary(user_id)
    status = {}
    
    for category, budget in DEFAULT_BUDGETS.items():
        spent = summary['by_category'].get(category, 0)
        remaining = budget - spent
        percentage = (spent / budget * 100) if budget > 0 else 0
        
        status[category] = {
            'budget': budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage
        }
    
    return status


if __name__ == '__main__':
    print("Budget module loaded")
    print(f"Default budgets: {DEFAULT_BUDGETS}")
