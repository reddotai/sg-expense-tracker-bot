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

import html

# Bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Constants
MAX_PHOTO_SIZE_MB = 10
RATE_LIMIT_SECONDS = 3
MAX_DAILY_RECEIPTS = 50  # Prevent API quota exhaustion
MAX_AI_CATEGORIZATIONS = 20  # Limit AI categorization separately


async def check_rate_limits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check all rate limits for user. Returns True if allowed."""
    user_id = update.effective_user.id
    
    # Check burst rate limit (3 seconds between requests)
    allowed, message = check_rate_limit(user_id, 'burst', 1, RATE_LIMIT_SECONDS)
    if not allowed:
        await update.message.reply_text(message)
        return False
    
    # Check daily receipt limit
    allowed, message = check_rate_limit(user_id, 'daily_receipts', MAX_DAILY_RECEIPTS)
    if not allowed:
        await update.message.reply_text(message)
        return False
    
    return True


async def check_ai_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check AI categorization rate limit. Returns True if allowed."""
    user_id = update.effective_user.id
    allowed, message = check_rate_limit(user_id, 'ai_categorization', MAX_AI_CATEGORIZATIONS)
    if not allowed:
        await update.message.reply_text(
            f"⚠️ AI categorization limit reached ({MAX_AI_CATEGORIZATIONS}/day).\n"
            "Unknown vendors will be marked as 'others' until tomorrow."
        )
        return False
    return True


def sanitize_vendor_name(vendor: str) -> str:
    """
    Sanitize vendor name for storage.
    Removes control characters and limits length.
    NOTE: HTML escaping is done at display time to prevent XSS.
    """
    if not vendor:
        return "Unknown Vendor"
    
    # Remove control characters (keep only printable ASCII and common Unicode)
    vendor = ''.join(char for char in vendor if ord(char) >= 32 or char in '\t\n\r')
    
    # Limit length
    vendor = vendor[:100]
    
    # Strip whitespace
    vendor = vendor.strip()
    
    return vendor if vendor else "Unknown Vendor"


def escape_for_display(text: str) -> str:
    """
    Escape HTML for safe display in Telegram.
    This prevents XSS if data is later used in a web context.
    """
    return html.escape(text)


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
    
    # Check rate limits (persistent, survives bot restart)
    if not await check_rate_limits(update, context):
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
        
        # Sanitize vendor name (prevent XSS/log injection)
        vendor = sanitize_vendor_name(receipt_data['vendor'])
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
        
        # Build response (escape for display to prevent XSS)
        message = f"✅ Expense recorded!\n\n"
        message += f"🏪 {escape_for_display(receipt_data['vendor'])}\n"
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
    # Check for placeholder values and provide friendly error messages
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN in ['your_telegram_bot_token_here', 'dummy_token_for_testing']:
        print("🤖 Welcome to Singapore Expense Tracker!")
        print()
        print("❌ TELEGRAM_BOT_TOKEN not configured")
        print()
        print("To set up your bot:")
        print("1. Message @BotFather on Telegram")
        print("2. Create a new bot with /newbot")
        print("3. Copy the token (looks like: 123456789:ABCdef...)")
        print("4. Edit the .env file and add your token:")
        print("   TELEGRAM_BOT_TOKEN=your_actual_token_here")
        print()
        print("Need help? See the README.md for detailed instructions.")
        return
    
    if not GEMINI_API_KEY or GEMINI_API_KEY in ['your_gemini_api_key_here', 'dummy_key_for_testing']:
        print("🤖 Welcome to Singapore Expense Tracker!")
        print()
        print("❌ GEMINI_API_KEY not configured")
        print()
        print("To get your API key:")
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Sign in with your Google account")
        print("3. Click 'Create API Key'")
        print("4. Edit the .env file and add your key:")
        print("   GEMINI_API_KEY=your_actual_key_here")
        print()
        print("Need help? See the README.md for detailed instructions.")
        return
    
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
