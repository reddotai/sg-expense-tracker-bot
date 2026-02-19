"""
Shared test fixtures and configuration.
"""

import pytest
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    from database import init_db, DATABASE_FILE
    
    # Create temp file
    fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Override database file
    original_db = DATABASE_FILE
    import database
    database.DATABASE_FILE = temp_path
    
    # Initialize
    init_db()
    
    yield temp_path
    
    # Cleanup
    database.DATABASE_FILE = original_db
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing."""
    return [
        {
            'vendor': 'NTUC FairPrice',
            'amount': 47.85,
            'date': '2024-02-19',
            'category': 'groceries',
            'items': ['Milk', 'Bread', 'Eggs']
        },
        {
            'vendor': 'Grab',
            'amount': 12.50,
            'date': '2024-02-19',
            'category': 'transport',
            'items': []
        },
        {
            'vendor': 'Starbucks',
            'amount': 7.20,
            'date': '2024-02-18',
            'category': 'dining',
            'items': ['Latte']
        }
    ]


@pytest.fixture
def mock_gemini_response():
    """Mock response from Gemini API."""
    return {
        'vendor': 'NTUC FairPrice',
        'amount': 47.85,
        'date': '2024-02-19',
        'items': ['Milk', 'Bread', 'Eggs']
    }
