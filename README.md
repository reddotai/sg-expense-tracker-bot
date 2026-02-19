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

### Before You Start (Check These)

- [ ] **Python 3.10+ installed** → [Download here](https://www.python.org/downloads/)
- [ ] **Git installed** → [Download here](https://git-scm.com/downloads)
- [ ] **A code editor** (VS Code, Notepad++, or any text editor)

**Not sure?** Open your terminal/command prompt and type:
```bash
python --version  # Should show 3.10 or higher
git --version     # Should show a version number
```

---

### Setup (Choose Your Operating System)

<details>
<summary><b>🪟 Windows</b> (Click to expand)</summary>

```bash
# 1. Clone the project
git clone https://github.com/reddotai/sg-expense-tracker-bot.git

# 2. Go into the folder
cd sg-expense-tracker-bot

# 3. Create virtual environment
python -m venv venv

# 4. Activate virtual environment
venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create environment file
copy .env.example .env

# 7. Edit .env file with your editor
# Add your TELEGRAM_BOT_TOKEN and GEMINI_API_KEY

# 8. Run the bot
python bot.py
```

</details>

<details>
<summary><b>🍎 Mac</b> (Click to expand)</summary>

```bash
# 1. Clone the project
git clone https://github.com/reddotai/sg-expense-tracker-bot.git

# 2. Go into the folder
cd sg-expense-tracker-bot

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Install dependencies
pip3 install -r requirements.txt

# 6. Create environment file
cp .env.example .env

# 7. Edit .env file
# Use TextEdit: open -e .env
# Or VS Code: code .env

# 8. Run the bot
python3 bot.py
```

</details>

<details>
<summary><b>🐧 Linux</b> (Click to expand)</summary>

```bash
# 1. Clone the project
git clone https://github.com/reddotai/sg-expense-tracker-bot.git

# 2. Go into the folder
cd sg-expense-tracker-bot

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Install dependencies
pip3 install -r requirements.txt

# 6. Create environment file
cp .env.example .env

# 7. Edit .env file
# nano .env    # or vim .env, or any editor

# 8. Run the bot
python3 bot.py
```

</details>

---

### What Each Command Does

| Command | What It Does |
|---------|--------------|
| `git clone` | Downloads the project from GitHub |
| `cd` | Changes to the project folder |
| `python -m venv venv` | Creates an isolated Python environment |
| `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows) | Activates the isolated environment |
| `pip install` | Downloads required libraries |
| `copy` or `cp` | Creates your personal settings file |

---

### Get Your API Keys

**Telegram Bot Token:**
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Type `/newbot`
3. Give your bot a name (e.g., "My Expense Tracker")
4. Give it a username ending in "bot" (e.g., "myexpense_bot")
5. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Gemini API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

---

## Common Setup Problems

### "'git' is not recognized" or "command not found"
**Problem:** Git is not installed  
**Fix:** Download and install Git from https://git-scm.com/downloads

### "'python' is not recognized" (Windows)
**Problem:** Python is not installed or not in PATH  
**Fix:** 
1. Install Python from https://python.org (check "Add to PATH" during install)
2. Or use `py` instead of `python` in commands

### "Permission denied" when activating venv (Mac/Linux)
**Problem:** Script needs execute permissions  
**Fix:** Run `chmod +x venv/bin/activate` then try again

### "No module named 'telegram'" or similar
**Problem:** Virtual environment not activated  
**Fix:** Make sure you see `(venv)` in your prompt before running pip install

### "TELEGRAM_BOT_TOKEN not set"
**Problem:** .env file not created or edited  
**Fix:** 
1. Make sure `.env` file exists (not `.env.example`)
2. Make sure you replaced the placeholder text with actual keys
3. No quotes needed around the values

### Bot doesn't respond to messages
**Checklist:**
- [ ] Bot is running (you see "Starting bot..." in terminal)
- [ ] You sent `/start` to the bot first
- [ ] You're messaging the correct bot (check the username)
- [ ] Your API keys are correct (no extra spaces)

---

### Edit Your .env File

Open `.env` in your editor and add:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
GEMINI_API_KEY=AIzaSyYourActualKeyHere
```

**Replace the values with your actual keys!**

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

## Troubleshooting

### "No module named 'google.genai'"
```bash
pip install google-genai
```

### "TELEGRAM_BOT_TOKEN not set"
You need to create a bot with @BotFather first. See Exercise 1.

### "GEMINI_API_KEY not set"
Get your API key from https://aistudio.google.com/app/apikey

### Bot doesn't respond to photos
- Make sure you've set both environment variables
- Check that the bot is running without errors
- Try sending a clearer photo with good lighting

### Tests fail with "ImportError"
Some tests require the `google-genai` package. Install it:
```bash
pip install google-genai
```

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
- A computer that stays on while using the bot (see Hosting Options below)

---

## Hosting Options

### Option 1: Run on Your Computer (Easiest)
Just run `python3 bot.py` on your laptop. The bot works when your computer is on and stops when it sleeps/shuts down.

**Good for:** Personal use, learning, testing

### Option 2: Cheap VPS (~$5/month)
Rent a small virtual server that stays online 24/7:
- [DigitalOcean](https://www.digitalocean.com/) - $4/month
- [Linode](https://www.linode.com/) - $5/month
- [Hetzner](https://www.hetzner.com/) - €3.79/month

**Good for:** Always-on bot, multiple users, production use

### Option 3: Raspberry Pi (One-time ~$50)
Buy a Raspberry Pi, leave it plugged in at home. Uses minimal electricity.

**Good for:** Privacy-conscious, tinkerers, learning Linux

---

## Cloud-Native Alternative: Cloudflare Workers

Want to run this without managing a server? See Exercise 5 (coming soon) on migrating to **Cloudflare Workers + Durable Objects**:
- Free tier: 100,000 requests/day
- Always on, globally distributed
- SQLite-like persistence via Durable Objects
- Good learning project for serverless architecture

---
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

---

## About This Project

This project is part of **Better Than SkillsFuture** — practical, hands-on learning for Singapore professionals.

**Learn more:** [reddotai.substack.com](https://reddotai.substack.com)

*Built with curiosity, caffeine, and a healthy disregard for boring classroom learning.*
