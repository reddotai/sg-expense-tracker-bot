# Singapore Expense Tracker Bot

> **Track your spending with a simple Telegram bot.**
> 
> Photo of receipt → AI extracts details → Track spending
> 
> Built in 3 hours. No certificate required.

---

## What It Does

1. **Send a photo** of any receipt to the Telegram bot
2. **Gemini AI** extracts vendor, amount, date, category
3. **Auto-categorizes** into Food, Transport, Shopping, etc.
4. **Tracks spending** with monthly summaries
5. **Budget alerts** when you're overspending
6. **Export to Excel** for tax/CPF claims

---

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/reddotai/sg-expense-tracker-bot.git
cd sg-expense-tracker-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set up your Telegram bot
# - Message @BotFather on Telegram
# - Create a new bot
# - Copy the API token

# 3. Set up Gemini API
# - Go to https://makersuite.google.com/app/apikey
# - Create an API key

# 4. Configure environment variables
export TELEGRAM_BOT_TOKEN="your_telegram_token"
export GEMINI_API_KEY="your_gemini_key"

# 5. Run the bot
python3 bot.py
```

---

## How It Works

### Receipt Processing Flow

```
User sends photo → Telegram Bot receives → Gemini Vision API extracts:
  - Vendor name (e.g., "NTUC FairPrice")
  - Total amount (e.g., "$47.85")
  - Date (e.g., "2026-02-19")
  - Items (optional)
  
→ Bot categorizes:
  - "NTUC" → Groceries
  - "Grab" → Transport/Food
  - "Uniqlo" → Shopping
  
→ Store in SQLite database
→ Update monthly totals
→ Check budget limits
→ Reply to user with summary
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and setup |
| `/help` | List all commands |
| `/summary` | This month's spending by category |
| `/budget` | Set monthly budget limits |
| `/export` | Export to Excel/CSV |
| `/delete` | Delete a transaction |

---

## Singapore-Specific Features

### Auto-Categorization

| Vendor Pattern | Category |
|----------------|----------|
| NTUC, Cold Storage, Sheng Siong | Groceries |
| Grab, Gojek, ComfortDelGro | Transport |
| GrabFood, Foodpanda, Deliveroo | Food Delivery |
| Hawker centre, Kopitiam | Hawker |
| Shell, Esso, Caltex | Petrol |
| Uniqlo, H&M, Zara | Shopping |
| Any restaurant/cafe | Dining |

### GST Handling
- Automatically detects GST from receipts
- Shows pre-GST and post-GST amounts
- Useful for business expense claims

### CPF-Trackable Expenses
- Flags medical expenses (claimable from Medisave)
- Tracks education expenses
- Marks insurance premiums

---

## Project Structure

```
sg-expense-tracker-bot/
├── bot.py                 # Main Telegram bot
├── receipt_processor.py   # Gemini API integration
├── database.py            # SQLite operations
├── categories.py          # Singapore vendor categories
├── budget.py              # Budget tracking and alerts [OPTIONAL]
├── export.py              # Excel/CSV export [OPTIONAL]
├── config.py              # Configuration
├── CLAUDE.md              # Developer guidance
├── requirements.txt       # Dependencies
├── README.md              # This file
├── .env.example           # Environment template
└── exercises/             # Learning exercises
    ├── 01_setup_bot.md
    ├── 02_process_receipt.md
    ├── 03_add_category.md
    └── 04_export_data.md
```

### Optional Features

This template includes optional features marked with `TODO: DELETE IF NOT USING`.
Search for these markers to remove features you don't need:

| Feature | File | To Remove |
|---------|------|-----------|
| Budget alerts | `budget.py` | Delete file + remove imports from `bot.py` |
| Excel export | `export.py` | Delete file + remove `/export` command |
| GST detection | `receipt_processor.py` | Remove GST extraction logic |

See `CLAUDE.md` for detailed guidance.

---

## What You Learn

### Technical Skills
- Telegram Bot API
- Google Gemini Vision API
- SQLite database operations
- Receipt OCR and data extraction
- Budget calculation logic

### Singapore Context
- GST 9% calculations
- Common vendor recognition
- Expense categorization patterns
- CPF/medical claimable expenses

---

## Exercises

### Exercise 1: Set Up Your Bot (30 min)
Create a Telegram bot and get it responding to messages.

### Exercise 2: Process a Receipt (1 hour)
Send a photo → Extract text with Gemini → Parse amount and vendor.

### Exercise 3: Add a New Category (30 min)
Add "Electronics" category with vendors like Challenger, Courts, Best Denki.

### Exercise 4: Export to Excel (1 hour)
Add `/export` command that generates Excel with monthly breakdown.

---

## Why This Beats SkillsFuture

| SkillsFuture Course | This Project |
|---------------------|--------------|
| $500-800 | Free |
| 2 days classroom | 3 hours hands-on |
| Generic examples | Your actual expenses |
| Certificate | Working bot you use daily |
| Forget in 3 months | Use every time you shop |

---

## Requirements

- Python 3.10+
- Telegram account
- Google account (for Gemini API)
- ~$0 cost (Gemini API has free tier)

---

## Privacy Note

- All data stored locally in SQLite
- No cloud storage
- Receipt photos processed via Gemini but not stored
- You own your data

---

**Built in 3 hours. No certificate required.**

If this helps you track your spending, star the repo and share it.
