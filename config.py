#!/usr/bin/env python3
"""
Configuration settings.
"""

import os
from typing import Optional

# API Keys (loaded from environment variables)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Bot settings
BOT_NAME = "Singapore Expense Tracker"
BOT_VERSION = "1.0.0"

# Database
DATABASE_FILE = "expenses.db"

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
    'others': 200
}


def validate_config() -> Optional[str]:
    """Validate that required environment variables are set."""
    if not TELEGRAM_BOT_TOKEN:
        return "TELEGRAM_BOT_TOKEN not set. Get it from @BotFather on Telegram."
    
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not set. Get it from https://aistudio.google.com/app/apikey"
    
    return None
