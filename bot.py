#!/usr/bin/env python3
"""
Singapore Expense Tracker Bot
Telegram bot for tracking expenses from receipt photos.
Uses Gemini AI for receipt parsing.
"""

import os
import logging
import time
from datetime import datetime
from typing import Optional, Dict
from functools import wraps

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

from receipt_processor import process_receipt
from database import init_db, add_transaction, get_monthly_summary
from categories import categorize_vendor
from budget import check_budget, get_budget_status
from export import export_to_excel, export_to_csv
from ai_categorization import (
    is_ai_categorization_enabled,
    toggle_ai_categorization,
    smart_categorize
)
from config import get_data_location_info

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Rate limiting storage (in production, use Redis or database)
user_last_request: Dict[int, float] = {}
user_daily_count: Dict[int, Dict[str, int]] = {}  # user_id -> {date: count}

# Constants
MAX_PHOTO_SIZE_MB = 10
RATE_LIMIT_SECONDS = 3
MAX_DAILY_RECEIPTS = 50  # Prevent API quota exhaustion


def rate_limit(seconds: int = RATE_LIMIT_SECONDS):
    """Decorator to rate limit commands per user."""
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            now = time.time()
            
            if user_id in user_last_request:
                elapsed = now - user_last_request[user_id]
                if elapsed < seconds:
                    await update.message.reply_text(
                        f"⏳ Please wait {seconds - int(elapsed)} seconds before trying again."
                    )
                    return
            
            user_last_request[user_id] = now
            return await func(update, context)
        return wrapper
    return decorator


def check_daily_limit(user_id: int, limit: int = MAX_DAILY_RECEIPTS) -> bool:
    """Check if user has exceeded daily receipt limit."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user_id not in user_daily_count:
        user_daily_count[user_id] = {}
    
    if today not in user_daily_count[user_id]:
        user_daily_count[user_id][today] = 0
    
    return user_daily_count[user_id][today] < limit


def increment_daily_count(user_id: int):
    """Increment user's daily receipt count."""
    today = datetime.now().strftime('%Y-%m-%d')
    if user_id in user_daily_count and today in user_daily_count[user_id]:
        user_daily_count[user_id][today] += 1


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued."""
    welcome_text = """
👋 Welcome to Singapore Expense Tracker!

Send me a photo of any receipt and I'll:
✓ Extract the vendor and amount
✓ Categorize it (Food, Transport, etc.)
✓ Track your spending

Commands:
/summary - View this month's spending
/budget - Set budget limits
/export - Export to Excel
/ai - Toggle AI categorization
/data - Show where your data is stored
/help - Show all commands

Built for Singapore: GST 9%, Grab, NTUC, hawker centres 🇸🇬
    """
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message."""
    help_text = """
📋 Available Commands:

/start - Welcome message
/help - This help message
/summary - Monthly spending summary
/budget - Set or view budget limits
/export - Export data to Excel
/ai - Toggle AI categorization on/off
/data - Show where your data is stored
/delete - Delete a transaction (use: /delete <ID>)

Just send me a receipt photo anytime! 📸

Supported receipts:
✓ NTUC, Cold Storage, Sheng Siong
✓ Grab, Gojek, taxis
✓ Hawker centres, food courts
✓ Any restaurant or shop
    """
    await update.message.reply_text(help_text)


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show monthly spending summary."""
    user_id = update.effective_user.id
    summary = get_monthly_summary(user_id)
    
    if not summary['transactions']:
        await update.message.reply_text(
            "No expenses recorded this month yet.\n"
            "Send me a receipt photo to get started! 📸"
        )
        return
    
    # Build summary message
    message = f"📊 Spending Summary ({summary['month']})\n"
    message += "=" * 30 + "\n\n"
    
    for category, amount in summary['by_category'].items():
        message += f"{category}: ${amount:.2f}\n"
    
    message += f"\n💰 Total: ${summary['total']:.2f}\n"
    message += f"📈 Transactions: {summary['count']}"
    
    await update.message.reply_text(message)


async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show budget status."""
    user_id = update.effective_user.id
    
    # Get budget status
    status = get_budget_status(user_id)
    
    # Build message
    message = "💰 Budget Status\n"
    message += "=" * 30 + "\n\n"
    
    has_spending = any(s['spent'] > 0 for s in status.values())
    
    if not has_spending:
        message += "No spending recorded yet.\n"
        message += "Send me a receipt photo to get started!"
        await update.message.reply_text(message)
        return
    
    for category, data in status.items():
        if data['spent'] > 0:  # Only show categories with spending
            emoji = "🟢" if data['percentage'] < 80 else "🟡" if data['percentage'] < 100 else "🔴"
            message += f"{emoji} {category.capitalize()}\n"
            message += f"   Spent: ${data['spent']:.2f} / ${data['budget']:.2f}\n"
            message += f"   {data['percentage']:.1f}% used\n\n"
    
    await update.message.reply_text(message)


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export data to Excel."""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating export...")
    
    try:
        # Generate Excel file
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"expenses_{user_id}_{timestamp}.xlsx"
        
        filepath = export_to_excel(user_id, filename)
        
        # Send file to user
        with open(filepath, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption="📊 Your expense report is ready!"
            )
        
        # Clean up file after sending
        import os
        os.remove(filepath)
        
    except ValueError as e:
        await update.message.reply_text(
            f"❌ {str(e)}\nSend some receipts first!"
        )
    except Exception as e:
        logger.error(f"Export error: {e}")
        await update.message.reply_text(
            "❌ Sorry, couldn't generate export. Try again later."
        )


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle AI categorization on/off."""
    user_id = update.effective_user.id
    
    # Check if google-genai is installed
    try:
        from ai_categorization import GENAI_AVAILABLE
        if not GENAI_AVAILABLE:
            await update.message.reply_text(
                "❌ AI categorization is not available.\n"
                "Install with: pip install google-genai"
            )
            return
    except ImportError:
        await update.message.reply_text(
            "❌ AI categorization module not found."
        )
        return
    
    # Toggle the setting
    current = is_ai_categorization_enabled(user_id)
    new_state = not current
    toggle_ai_categorization(user_id, new_state)
    
    if new_state:
        message = (
            "🤖 AI Categorization: ON\n\n"
            "Unknown vendors will be categorized using Gemini AI.\n"
            "This uses a small amount of API quota per unknown vendor."
        )
    else:
        message = (
            "🤖 AI Categorization: OFF\n\n"
            "Using rule-based categorization only.\n"
            "Unknown vendors will be marked as 'others'."
        )
    
    await update.message.reply_text(message)


async def data_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show where data is stored."""
    await update.message.reply_text(get_data_location_info())


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete a transaction by ID."""
    user_id = update.effective_user.id
    
    # Check if transaction ID was provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a transaction ID.\n"
            "Use /summary to see your transactions with IDs.\n\n"
            "Example: /delete 5"
        )
        return
    
    try:
        transaction_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Transaction ID must be a number.\n"
            "Example: /delete 5"
        )
        return
    
    # Try to delete
    from database import delete_transaction
    success = delete_transaction(transaction_id, user_id)
    
    if success:
        await update.message.reply_text(
            f"✅ Transaction {transaction_id} deleted successfully."
        )
    else:
        await update.message.reply_text(
            f"❌ Could not delete transaction {transaction_id}.\n"
            "Make sure the ID is correct and the transaction belongs to you."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process receipt photos with security checks."""
    user_id = update.effective_user.id
    
    # Rate limiting check
    now = time.time()
    if user_id in user_last_request:
        elapsed = now - user_last_request[user_id]
        if elapsed < RATE_LIMIT_SECONDS:
            await update.message.reply_text(
                f"⏳ Please wait {RATE_LIMIT_SECONDS - int(elapsed)} seconds between receipts."
            )
            return
    user_last_request[user_id] = now
    
    # Daily limit check
    if not check_daily_limit(user_id):
        await update.message.reply_text(
            f"⚠️ Daily limit reached ({MAX_DAILY_RECEIPTS} receipts/day).\n"
            "This helps prevent API quota exhaustion.\n"
            "Try again tomorrow!"
        )
        return
    
    # Get the photo file
    photo = update.message.photo[-1]  # Get largest photo
    
    # File size validation (prevent crashes from huge images)
    if photo.file_size and photo.file_size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            f"❌ Image too large ({photo.file_size // (1024*1024)}MB).\n"
            f"Maximum size: {MAX_PHOTO_SIZE_MB}MB.\n"
            "Please compress or crop the image."
        )
        return
    
    await update.message.reply_text("📸 Processing your receipt...")
    
    try:
        # Download to memory
        photo_file = await photo.get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Validate image format (basic check)
        if len(photo_bytes) < 100:
            await update.message.reply_text(
                "❌ Invalid image. Please send a proper photo."
            )
            return
        
        # Process with Gemini
        receipt_data = process_receipt(photo_bytes, GEMINI_API_KEY)
        
        if not receipt_data:
            await update.message.reply_text(
                "❌ Sorry, I couldn't read this receipt.\n"
                "Try sending a clearer photo with good lighting."
            )
            return
        
        # Increment daily count on success
        increment_daily_count(user_id)
        
        # Sanitize vendor name (prevent XSS/log injection)
        vendor = receipt_data['vendor']
        if vendor:
            # Remove control characters and limit length
            vendor = ''.join(char for char in vendor if ord(char) >= 32)[:100]
        if not vendor:
            vendor = "Unknown Vendor"
        receipt_data['vendor'] = vendor
        
        # Categorize the vendor (smart categorization with AI fallback)
        category = smart_categorize(vendor, user_id, GEMINI_API_KEY)
        
        # Add to database
        transaction_id = add_transaction(
            user_id=user_id,
            vendor=receipt_data['vendor'],
            amount=receipt_data['amount'],
            date=receipt_data['date'],
            category=category,
            items=receipt_data.get('items', [])
        )
        
        # Build response
        message = f"✅ Expense recorded!\n\n"
        message += f"🏪 {receipt_data['vendor']}\n"
        message += f"💵 ${receipt_data['amount']:.2f}\n"
        message += f"📁 {category}\n"
        
        if receipt_data.get('date'):
            message += f"📅 {receipt_data['date']}\n"
        
        # Check budget
        budget_status = check_budget(user_id, category, receipt_data['amount'])
        if budget_status:
            message += f"\n⚠️ {budget_status}"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        await update.message.reply_text(
            "❌ Sorry, something went wrong.\n"
            "Please try again with a clearer photo."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    await update.message.reply_text(
        "Send me a receipt photo! 📸\n\n"
        "I can read receipts from:\n"
        "• NTUC, Cold Storage, Sheng Siong\n"
        "• Grab, Gojek, taxis\n"
        "• Hawker centres, restaurants\n\n"
        "Use /help for more options."
    )


def main() -> None:
    """Start the bot."""
    # Validate environment variables
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set. Get it from @BotFather")
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Get it from Google AI Studio")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("summary", summary_command))
    application.add_handler(CommandHandler("budget", budget_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("data", data_command))
    application.add_handler(CommandHandler("delete", delete_command))
    
    # Photo handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Text handler (for non-commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
