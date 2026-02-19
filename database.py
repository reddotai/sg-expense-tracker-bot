#!/usr/bin/env python3
"""
SQLite database operations for expense tracking.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

DATABASE_FILE = "expenses.db"


def init_db() -> None:
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vendor TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            items TEXT,  -- JSON array of items
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_date 
        ON transactions(user_id, date)
    ''')
    
    conn.commit()
    conn.close()


def add_transaction(
    user_id: int,
    vendor: str,
    amount: float,
    date: Optional[str],
    category: str,
    items: List[str]
) -> int:
    """
    Add a new transaction to the database.
    
    Returns:
        The transaction ID
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Use current date if not provided
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        INSERT INTO transactions (user_id, vendor, amount, date, category, items)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, vendor, amount, date, category, json.dumps(items)))
    
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return transaction_id


def get_monthly_summary(user_id: int, year_month: Optional[str] = None) -> Dict:
    """
    Get spending summary for a month.
    
    Args:
        user_id: Telegram user ID
        year_month: Format "2024-02", defaults to current month
    
    Returns:
        Dictionary with total, by_category, transactions, count
    """
    if not year_month:
        year_month = datetime.now().strftime('%Y-%m')
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Get transactions for the month
    cursor.execute('''
        SELECT vendor, amount, date, category, items
        FROM transactions
        WHERE user_id = ? AND date LIKE ?
        ORDER BY date DESC
    ''', (user_id, f'{year_month}%'))
    
    transactions = cursor.fetchall()
    
    # Calculate totals by category
    by_category = {}
    total = 0
    
    for vendor, amount, date, category, items in transactions:
        by_category[category] = by_category.get(category, 0) + amount
        total += amount
    
    conn.close()
    
    return {
        'month': year_month,
        'total': total,
        'by_category': by_category,
        'transactions': transactions,
        'count': len(transactions)
    }


def get_all_transactions(user_id: int) -> List[Dict]:
    """Get all transactions for a user."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, vendor, amount, date, category, items, created_at
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    transactions = []
    for row in rows:
        transactions.append({
            'id': row[0],
            'vendor': row[1],
            'amount': row[2],
            'date': row[3],
            'category': row[4],
            'items': json.loads(row[5]) if row[5] else [],
            'created_at': row[6]
        })
    
    return transactions


def delete_transaction(transaction_id: int, user_id: int) -> bool:
    """Delete a transaction. Returns True if successful."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
    ''', (transaction_id, user_id))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted


if __name__ == '__main__':
    init_db()
    print("Database initialized successfully")
