"""
Tests for export functionality.
"""

import pytest
import os
import pandas as pd
from datetime import datetime


class TestExportToExcel:
    """Test Excel export functionality."""
    
    def test_export_creates_file(self, temp_db):
        """Should create an Excel file."""
        from export import export_to_excel
        from database import add_transaction
        
        # Add test data
        add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        
        filename = export_to_excel(12345, 'test_export.xlsx')
        
        assert os.path.exists(filename)
        assert filename.endswith('.xlsx')
        
        # Cleanup
        os.remove(filename)
    
    def test_export_contains_transactions(self, temp_db):
        """Excel should contain transaction data."""
        from export import export_to_excel
        from database import add_transaction
        
        add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        add_transaction(12345, 'Grab', 20.0, '2024-02-19', 'transport', [])
        
        filename = export_to_excel(12345, 'test_export.xlsx')
        
        # Read Excel
        df = pd.read_excel(filename, sheet_name='Transactions')
        
        assert len(df) == 2
        assert 'NTUC' in df['vendor'].values
        assert 'Grab' in df['vendor'].values
        
        # Cleanup
        os.remove(filename)
    
    def test_export_has_summary_sheet(self, temp_db):
        """Excel should have summary by category sheet."""
        from export import export_to_excel
        from database import add_transaction
        
        add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        add_transaction(12345, 'NTUC', 30.0, '2024-02-20', 'groceries', [])
        
        filename = export_to_excel(12345, 'test_export.xlsx')
        
        # Read summary sheet
        df = pd.read_excel(filename, sheet_name='Summary by Category')
        
        assert 'groceries' in df.index
        assert df.loc['groceries', 'Total Amount'] == 80.0
        assert df.loc['groceries', 'Transaction Count'] == 2
        
        # Cleanup
        os.remove(filename)
    
    def test_export_empty_raises_error(self, temp_db):
        """Should raise error if no transactions."""
        from export import export_to_excel
        
        with pytest.raises(ValueError, match="No transactions"):
            export_to_excel(12345, 'test_export.xlsx')


class TestExportToCSV:
    """Test CSV export functionality."""
    
    def test_export_csv_creates_file(self, temp_db):
        """Should create a CSV file."""
        from export import export_to_csv
        from database import add_transaction
        
        add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        
        filename = export_to_csv(12345, 'test_export.csv')
        
        assert os.path.exists(filename)
        assert filename.endswith('.csv')
        
        # Cleanup
        os.remove(filename)
    
    def test_export_csv_contains_data(self, temp_db):
        """CSV should contain transaction data."""
        from export import export_to_csv
        from database import add_transaction
        
        add_transaction(12345, 'NTUC', 50.0, '2024-02-19', 'groceries', [])
        
        filename = export_to_csv(12345, 'test_export.csv')
        
        # Read CSV
        df = pd.read_csv(filename)
        
        assert len(df) == 1
        assert df.iloc[0]['vendor'] == 'NTUC'
        assert df.iloc[0]['amount'] == 50.0
        
        # Cleanup
        os.remove(filename)
