"""
Tests for budget calculations.
"""

import pytest
from datetime import datetime
from budget import check_budget, get_budget_status
from config import DEFAULT_BUDGETS


# Get current month for test data
CURRENT_MONTH = datetime.now().strftime('%Y-%m')


class TestCheckBudget:
    """Test budget checking logic."""
    
    def test_under_budget(self, temp_db):
        """Should return None when under budget."""
        # First transaction in groceries (limit: 500)
        result = check_budget(12345, 'groceries', 100.0)
        assert result is None
    
    def test_at_80_percent(self, temp_db):
        """Should warn at 80% of budget."""
        # Add spending to reach 80% of 500 = 400
        from database import add_transaction
        add_transaction(12345, 'NTUC', 400.0, f'{CURRENT_MONTH}-19', 'groceries', [])
        
        # Adding $1 more pushes it over 80% threshold
        result = check_budget(12345, 'groceries', 1.0)
        
        assert result is not None
        assert '80%' in result
        assert 'remaining' in result.lower()
    
    def test_over_budget(self, temp_db):
        """Should alert when over budget."""
        # Add spending to exceed 500 limit
        from database import add_transaction
        add_transaction(12345, 'NTUC', 450.0, f'{CURRENT_MONTH}-19', 'groceries', [])
        
        result = check_budget(12345, 'groceries', 100.0)  # Would make it 550
        
        assert result is not None
        assert 'Over budget' in result
        assert 'Limit: $500.00' in result
    
    def test_exactly_at_budget(self, temp_db):
        """Should warn when at or over budget."""
        from database import add_transaction
        add_transaction(12345, 'NTUC', 500.0, f'{CURRENT_MONTH}-19', 'groceries', [])
        
        result = check_budget(12345, 'groceries', 0.0)
        
        # At exactly 100%, should warn about being over budget
        assert result is not None
        assert 'Over budget' in result or '80%' in result


class TestGetBudgetStatus:
    """Test budget status retrieval."""
    
    def test_all_categories_present(self, temp_db):
        """Status should include all categories."""
        status = get_budget_status(12345)
        
        for category in DEFAULT_BUDGETS.keys():
            assert category in status
            assert 'budget' in status[category]
            assert 'spent' in status[category]
            assert 'remaining' in status[category]
            assert 'percentage' in status[category]
    
    def test_calculations_correct(self, temp_db):
        """Budget calculations should be correct."""
        from database import add_transaction
        add_transaction(12345, 'NTUC', 100.0, f'{CURRENT_MONTH}-19', 'groceries', [])
        
        status = get_budget_status(12345)
        
        assert status['groceries']['budget'] == 500.0
        assert status['groceries']['spent'] == 100.0
        assert status['groceries']['remaining'] == 400.0
        assert status['groceries']['percentage'] == 20.0
    
    def test_percentage_calculation(self, temp_db):
        """Percentage should be calculated correctly."""
        from database import add_transaction
        add_transaction(12345, 'NTUC', 250.0, f'{CURRENT_MONTH}-19', 'groceries', [])
        
        status = get_budget_status(12345)
        
        assert status['groceries']['percentage'] == 50.0


class TestDefaultBudgets:
    """Test default budget values."""
    
    def test_reasonable_defaults(self):
        """Default budgets should be reasonable amounts."""
        # All budgets should be positive numbers
        for category, budget in DEFAULT_BUDGETS.items():
            assert budget > 0
            assert isinstance(budget, (int, float))
        
        # Groceries should be highest (Singapore is expensive!)
        assert DEFAULT_BUDGETS['groceries'] >= 500
        
        # Transport should be reasonable
        assert 100 <= DEFAULT_BUDGETS['transport'] <= 500
    
    def test_electronics_budget_exists(self):
        """Electronics category should have a budget."""
        assert 'electronics' in DEFAULT_BUDGETS
        assert DEFAULT_BUDGETS['electronics'] > 0
