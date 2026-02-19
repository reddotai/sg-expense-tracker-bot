#!/usr/bin/env python3
"""
Export functionality for expenses.

TODO: DELETE IF NOT USING EXCEL EXPORT
This entire file can be removed if you don't want export functionality.
Also remove export-related code from bot.py.
"""

import pandas as pd
from datetime import datetime
from typing import Optional
from pathlib import Path
from database import get_all_transactions
from config import EXPORT_DIR


def export_to_excel(user_id: int, filename: Optional[str] = None) -> str:
    """
    Export user transactions to Excel file.
    
    Args:
        user_id: Telegram user ID
        filename: Optional custom filename
    
    Returns:
        Path to the generated Excel file
    """
    # Get all transactions
    transactions = get_all_transactions(user_id)
    
    if not transactions:
        raise ValueError("No transactions to export")
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Format date column
    df['date'] = pd.to_datetime(df['date'])
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"expenses_{timestamp}.xlsx"
    
    # Full path in export directory
    filepath = EXPORT_DIR / filename
    
    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Main transactions sheet
        df.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Summary by category
        summary = df.groupby('category')['amount'].agg(['sum', 'count'])
        summary.columns = ['Total Amount', 'Transaction Count']
        summary.to_excel(writer, sheet_name='Summary by Category')
        
        # Monthly summary
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].sum()
        monthly.to_excel(writer, sheet_name='Monthly Summary')
    
    return str(filepath)


def export_to_csv(user_id: int, filename: Optional[str] = None) -> str:
    """Export to CSV format."""
    transactions = get_all_transactions(user_id)
    
    if not transactions:
        raise ValueError("No transactions to export")
    
    df = pd.DataFrame(transactions)
    
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"expenses_{timestamp}.csv"
    
    filepath = EXPORT_DIR / filename
    df.to_csv(filepath, index=False)
    return str(filepath)


if __name__ == '__main__':
    print("Export module loaded")
    print(f"Exports go to: {EXPORT_DIR}")
