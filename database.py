#!/usr/bin/env python3
"""
SQLite database operations for expense tracking.
"""

import sqlite3
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from config import DATABASE_FILE

logger = logging.getLogger(__name__)


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
            items TEXT,
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
    """Add a new transaction to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
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
    """Get spending summary for a month."""
    if not year_month:
        year_month = datetime.now().strftime('%Y-%m')
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT vendor, amount, date, category, items
        FROM transactions
        WHERE user_id = ? AND date LIKE ?
        ORDER BY date DESC
    ''', (user_id, f'{year_month}%'))
    
    transactions = cursor.fetchall()
    
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


# User settings
def init_user_settings_table() -> None:
    """Create user_settings table if not exists."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER NOT NULL,
            setting_key TEXT NOT NULL,
            setting_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, setting_key)
        )
    ''')
    
    conn.commit()
    conn.close()


def get_user_setting(user_id: int, key: str, default: str = '') -> str:
    """Get a user setting value."""
    init_user_settings_table()
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT setting_value FROM user_settings
        WHERE user_id = ? AND setting_key = ?
    ''', (user_id, key))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else default


def set_user_setting(user_id: int, key: str, value: str) -> None:
    """Set a user setting value."""
    init_user_settings_table()
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_settings (user_id, setting_key, setting_value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, setting_key) DO UPDATE SET
            setting_value = excluded.setting_value,
            updated_at = CURRENT_TIMESTAMP
    ''', (user_id, key, value))
    
    conn.commit()
    conn.close()


# Rate limiting with atomic operations
def init_rate_limit_table() -> None:
    """Create rate limiting table if not exists."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limits (
            user_id INTEGER NOT NULL,
            limit_type TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            reset_date TEXT NOT NULL,
            last_request REAL,
            PRIMARY KEY (user_id, limit_type)
        )
    ''')
    
    conn.commit()
    conn.close()


def check_rate_limit(user_id: int, limit_type: str, max_requests: int,
                     window_seconds: Optional[int] = None) -> Tuple[bool, str]:
    """
    Atomic rate limit check using database transactions.
    Prevents race conditions by using BEGIN IMMEDIATE.
    """
    init_rate_limit_table()
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    now = time.time()
    
    try:
        # Use IMMEDIATE to prevent race conditions
        conn.execute('BEGIN IMMEDIATE')
        
        # Get current record with locking
        cursor.execute('''
            SELECT count, reset_date, last_request FROM rate_limits
            WHERE user_id = ? AND limit_type = ?
        ''', (user_id, limit_type))
        
        result = cursor.fetchone()
        
        if not result:
            # First request - create record
            cursor.execute('''
                INSERT INTO rate_limits (user_id, limit_type, count, reset_date, last_request)
                VALUES (?, ?, 1, ?, ?)
            ''', (user_id, limit_type, today, now))
            conn.commit()
            return True, ""
        
        count, reset_date, last_request = result
        
        # Check if window has reset
        should_reset = False
        if limit_type.startswith('daily') and reset_date != today:
            should_reset = True
            count = 0
        elif limit_type == 'burst' and window_seconds and last_request:
            if now - last_request > window_seconds:
                should_reset = True
                count = 0
        
        # Check limit before incrementing
        if count >= max_requests and not should_reset:
            conn.rollback()
            if limit_type.startswith('daily'):
                message = f"⚠️ Daily limit reached ({max_requests} requests/day). Try again tomorrow!"
            else:
                message = "⏳ Rate limit exceeded. Please wait a moment."
            return False, message
        
        # Atomic increment
        if should_reset:
            cursor.execute('''
                UPDATE rate_limits 
                SET count = 1, reset_date = ?, last_request = ?
                WHERE user_id = ? AND limit_type = ?
            ''', (today, now, user_id, limit_type))
        else:
            cursor.execute('''
                UPDATE rate_limits 
                SET count = count + 1, last_request = ?
                WHERE user_id = ? AND limit_type = ?
            ''', (now, user_id, limit_type))
        
        conn.commit()
        return True, ""
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Rate limit database error: {e}")
        return True, ""  # Fail open
    finally:
        conn.close()


def get_rate_limit_status(user_id: int, limit_type: str) -> Dict:
    """Get current rate limit status for user."""
    init_rate_limit_table()
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT count, reset_date, last_request FROM rate_limits
        WHERE user_id = ? AND limit_type = ?
    ''', (user_id, limit_type))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return {'count': 0, 'reset_date': today, 'last_request': None}
    
    return {
        'count': result[0],
        'reset_date': result[1],
        'last_request': result[2]
    }


if __name__ == '__main__':
    init_db()
    init_user_settings_table()
    init_rate_limit_table()
    print("Database initialized successfully")
