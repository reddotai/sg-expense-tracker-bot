#!/usr/bin/env python3
"""
Configuration settings.

BEGINNERS: This is where you can change where your data is stored!
"""

import os
from pathlib import Path
from typing import Optional

# API Keys (loaded from environment variables)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Bot settings
BOT_NAME = "Singapore Expense Tracker"
BOT_VERSION = "1.0.0"

# =============================================================================
# DATA LOCATION - BEGINNERS CAN CHANGE THIS
# =============================================================================
# By default, all data is stored in a "data" folder next to the bot.
# You can change this to any folder path you want.

# Option 1: Use a "data" folder in the same directory as the bot (DEFAULT)
DATA_DIR = Path("data")

# Option 2: Use a specific folder path (uncomment and modify)
# DATA_DIR = Path("/home/yourname/expense-data")

# Option 3: Use your Documents folder (uncomment to use)
# DATA_DIR = Path.home() / "Documents" / "SingaporeExpenseTracker"

# Create the data directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database file location (inside DATA_DIR)
DATABASE_FILE = DATA_DIR / "expenses.db"

# Export files location (inside DATA_DIR)
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# END OF BEGINNER-CONFIGURABLE SECTION
# =============================================================================

# Gemini settings
GEMINI_MODEL = "gemini-1.5-flash"

# Singapore settings
GST_RATE = 0.09  # 9% GST

# Budget defaults (SGD)
DEFAULT_BUDGETS = {
    'groceries': 500,
    'transport': 200,
    'food_delivery': 150,
    'hawker': 200,
    'dining': 300,
    'petrol': 250,
    'shopping': 200,
    'electronics': 150,
    'utilities': 150,
    'healthcare': 100,
    'entertainment': 100,
    'education': 200,
    'travel': 300,
    'insurance': 200,
    'subscriptions': 50,
    'others': 200
}


def validate_config() -> Optional[str]:
    """Validate that required environment variables are set."""
    if not TELEGRAM_BOT_TOKEN:
        return "TELEGRAM_BOT_TOKEN not set. Get it from @BotFather on Telegram."
    
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not set. Get it from https://aistudio.google.com/app/apikey"
    
    return None


def get_data_location_info() -> str:
    """Return a friendly message showing where data is stored."""
    return f"""📁 Your data is stored in:
   {DATA_DIR.absolute()}

   • Database: {DATABASE_FILE.name}
   • Exports: {EXPORT_DIR.name}/

To change this location, edit config.py"""
