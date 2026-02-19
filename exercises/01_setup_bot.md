# Exercise 1: Set Up Your Bot

## Goal
Create a Telegram bot and get it responding to messages.

**Time:** 30 minutes  
**Prerequisites:** Telegram account, Python 3.10+

---

## Step 1: Create Your Telegram Bot

### Message @BotFather

1. Open Telegram and search for **@BotFather**
2. Start a chat and send: `/newbot`
3. Follow the prompts:
   - **Name:** `Singapore Expense Tracker` (display name)
   - **Username:** `yourname_expense_bot` (must end in `bot`, unique)

4. BotFather will give you a **token** that looks like:
   ```
   123456789:ABCdefGHIjklMNOpqrSTUvwxyz
   ```

**⚠️ Keep this token secret!** Anyone with it can control your bot.

---

## Step 2: Set Up Your Environment

### Clone the Repository

```bash
git clone https://github.com/reddotai/sg-expense-tracker-bot.git
cd sg-expense-tracker-bot
```

### Create Virtual Environment

This keeps your project dependencies isolated.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt when activated.

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3: Configure Environment Variables

### Create .env File

```bash
cp .env.example .env
```

### Edit .env

Open `.env` in your text editor and add your token:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
GEMINI_API_KEY=your_gemini_key_here  # We'll add this in Exercise 2
```

---

## Step 4: Test Your Bot

### Run the Bot

```bash
python3 bot.py
```

You should see:
```
Database initialized
Starting bot...
```

### Test in Telegram

1. Find your bot in Telegram (search for the username you created)
2. Send `/start`
3. You should see the welcome message!

Try these commands:
- `/start` — Welcome message
- `/help` — List commands
- Send any text — Bot should respond

---

## Step 5: Understanding the Code

### Find the Start Handler

Look in `bot.py` for the `start_command` function:

```python
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    welcome_text = """
👋 Welcome to Singapore Expense Tracker!
...
    """
    await update.message.reply_text(welcome_text)
```

### How It Works

1. **Telegram sends a message** to your bot
2. **python-telegram-bot** receives it and calls the right handler
3. **Your function** sends a reply back

### The Main Function

Find `main()` in `bot.py`:

```python
def main():
    # Create application with your token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Start the bot
    application.run_polling()
```

---

## Troubleshooting

### "No module named 'telegram'"

**Problem:** Dependencies not installed  
**Fix:**
```bash
pip install -r requirements.txt
```

### "TELEGRAM_BOT_TOKEN not set"

**Problem:** Environment variable missing  
**Fix:**
```bash
# Check if .env exists
ls -la .env

# If not, create it
cp .env.example .env
# Then edit and add your token
```

### Bot not responding

**Problem:** Token might be wrong  
**Fix:**
1. Check token with @BotFather: `/token`
2. Update `.env` file
3. Restart the bot (Ctrl+C, then `python3 bot.py`)

---

## What You Learned

- How Telegram bots work
- Setting up a Python project
- Using environment variables
- Running a bot locally

---

## Next Exercise

[→ Exercise 2: Process a Receipt](02_process_receipt.md)

We'll add Gemini AI to read receipt photos!
