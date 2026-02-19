# CLAUDE.md

This file provides guidance when working on the Singapore Expense Tracker Bot.

## Project Overview

A Telegram bot that processes receipt photos using Gemini AI to track expenses.
Built for Singapore context with local vendor recognition and GST handling.

## Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN and GEMINI_API_KEY

# Run
python3 bot.py
```

## Architecture

### Core Modules

| File | Purpose |
|------|---------|
| `bot.py` | Telegram bot entry point, command handlers |
| `receipt_processor.py` | Gemini Vision API integration |
| `database.py` | SQLite operations |
| `categories.py` | Singapore vendor categorization |
| `budget.py` | Budget tracking and alerts |
| `config.py` | Configuration and validation |

### Data Flow

```
User sends photo → Telegram Bot API → bot.py
                                    ↓
                              receipt_processor.py (Gemini API)
                                    ↓
                              Extract: vendor, amount, date
                                    ↓
                              categories.py (auto-categorize)
                                    ↓
                              database.py (store)
                                    ↓
                              budget.py (check limits)
                                    ↓
                              Reply to user
```

## Optional Features (TODO Markers)

Search for `TODO: DELETE IF NOT USING` to find optional features:

### Budget Alerts
- **File:** `budget.py`, `bot.py`
- **TODO:** `DELETE IF NOT USING BUDGET ALERTS`
- Removes monthly budget tracking and overspending warnings

### Excel Export
- **File:** `export.py` (create), `bot.py`
- **TODO:** `DELETE IF NOT USING EXCEL EXPORT`
- Removes `/export` command and Excel generation

### GST Detection
- **File:** `receipt_processor.py`
- **TODO:** `DELETE IF NOT USING GST DETECTION`
- Removes GST amount extraction from receipts

## Adding Features

### New Command
1. Add handler in `bot.py`
2. Register in `main()` function
3. Update `/help` text

### New Category
1. Add vendor patterns in `categories.py`
2. Add emoji in `get_category_emoji()`
3. Update README with examples

### New Database Field
1. Update `init_db()` in `database.py`
2. Update `add_transaction()` parameters
3. Update call sites in `bot.py`

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_categories.py -v
```

## Deployment

### Local Testing
```bash
# Use polling (good for development)
python3 bot.py
```

### Production (Webhook)
```bash
# Set webhook URL
export WEBHOOK_URL="https://your-domain.com/webhook"
# Update bot.py to use webhook mode
```

## Singapore-Specific Context

### Vendor Recognition
The bot recognizes common Singapore vendors:
- **Groceries:** NTUC, Cold Storage, Sheng Siong, Giant
- **Transport:** Grab, Gojek, ComfortDelGro
- **Food Delivery:** GrabFood, Foodpanda, Deliveroo
- **Hawker:** Kopitiam, Food Republic, food courts
- **Petrol:** Shell, Esso, Caltex, SPC

### GST Handling
- Current rate: 9%
- Extracted from receipts when visible
- Shown separately in transaction details

### CPF-Claimable Expenses
TODO: Add flags for medical, education, insurance expenses

## Common Issues

**"No module named 'telegram'"**
→ Run `pip install -r requirements.txt`

**"TELEGRAM_BOT_TOKEN not set"**
→ Copy `.env.example` to `.env` and add your token

**"Gemini API error"**
→ Check your API key at https://makersuite.google.com/app/apikey

**"Database locked"**
→ SQLite doesn't support concurrent writes; bot handles this with retries

## Resources

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [Gemini API docs](https://ai.google.dev/docs)
- [SQLite Python docs](https://docs.python.org/3/library/sqlite3.html)
