"""
Tests for database operations.
"""

import pytest
from database import (
    init_db, add_transaction, get_monthly_summary,
    get_all_transactions, delete_transaction
)


class TestDatabaseOperations:
    """Test database CRUD operations."""
    
    def test_init_db_creates_tables(self, temp_db):
        """Database initialization should create required tables."""
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check if transactions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='transactions'
        """)
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_add_transaction(self, temp_db):
        """Should be able to add a transaction."""
        transaction_id = add_transaction(
            user_id=12345,
            vendor='NTUC FairPrice',
            amount=47.85,
            date='2024-02-19',
            category='groceries',
            items=['Milk', 'Bread']
        )
        
        assert transaction_id is not None
        assert isinstance(transaction_id, int)
        assert transaction_id > 0
    
    def test_add_transaction_without_date(self, temp_db):
        """Should use current date if not provided."""
        from datetime import datetime
        
        transaction_id = add_transaction(
            user_id=12345,
            vendor='Grab',
            amount=12.50,
            date=None,
            category='transport',
            items=[]
        )
        
        assert transaction_id > 0
        
        # Verify date was set
        transactions = get_all_transactions(12345)
        assert len(transactions) == 1
        assert transactions[0]['date'] == datetime.now().strftime('%Y-%m-%d')
    
    def test_get_monthly_summary_empty(self, temp_db):
        """Summary for user with no transactions should be empty."""
        summary = get_monthly_summary(99999)  # Non-existent user
        
        assert summary['total'] == 0
        assert summary['count'] == 0
        assert summary['by_category'] == {}
        assert summary['transactions'] == []
    
    def test_get_monthly_summary_with_data(self, temp_db):
        """Summary should aggregate transactions correctly."""
        # Add test transactions
        add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        add_transaction(12345, 'Grab', 20.0, '2024-02-19', 'transport', [])
        add_transaction(12345, 'NTUC', 30.0, '2024-02-20', 'groceries', [])
        
        summary = get_monthly_summary(12345, '2024-02')
        
        assert summary['total'] == 100.0
        assert summary['count'] == 3
        assert summary['by_category']['groceries'] == 80.0
        assert summary['by_category']['transport'] == 20.0
    
    def test_get_monthly_summary_different_months(self, temp_db):
        """Summary should only include specified month."""
        add_transaction(12345, 'NTUC', 50.0, '2024-01-15', 'groceries', [])
        add_transaction(12345, 'Grab', 20.0, '2024-02-15', 'transport', [])
        
        jan_summary = get_monthly_summary(12345, '2024-01')
        feb_summary = get_monthly_summary(12345, '2024-02')
        
        assert jan_summary['total'] == 50.0
        assert feb_summary['total'] == 20.0
    
    def test_get_all_transactions(self, temp_db):
        """Should return all transactions for a user."""
        # Add transactions for different users
        add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        add_transaction(12345, 'Grab', 20.0, '2024-02-19', 'transport', [])
        add_transaction(99999, 'Starbucks', 10.0, '2024-02-19', 'dining', [])
        
        user_transactions = get_all_transactions(12345)
        
        assert len(user_transactions) == 2
        assert all(t['vendor'] in ['NTUC', 'Grab'] for t in user_transactions)
    
    def test_get_all_transactions_sorted(self, temp_db):
        """Transactions should be sorted by date descending."""
        add_transaction(12345, 'Old', 10.0, '2024-01-01', 'others', [])
        add_transaction(12345, 'New', 10.0, '2024-02-01', 'others', [])
        
        transactions = get_all_transactions(12345)
        
        assert transactions[0]['vendor'] == 'New'
        assert transactions[1]['vendor'] == 'Old'
    
    def test_delete_transaction_success(self, temp_db):
        """Should be able to delete own transaction."""
        transaction_id = add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        
        result = delete_transaction(transaction_id, 12345)
        
        assert result is True
        assert len(get_all_transactions(12345)) == 0
    
    def test_delete_transaction_wrong_user(self, temp_db):
        """Should not be able to delete another user's transaction."""
        transaction_id = add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        
        result = delete_transaction(transaction_id, 99999)  # Different user
        
        assert result is False
        assert len(get_all_transactions(12345)) == 1  # Still exists
    
    def test_delete_nonexistent_transaction(self, temp_db):
        """Deleting non-existent transaction should return False."""
        result = delete_transaction(99999, 12345)
        assert result is False
