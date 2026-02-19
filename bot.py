#!/usr/bin/env python3
"""
Singapore Expense Tracker Bot
Telegram bot for tracking expenses from receipt photos.
Uses Gemini AI for receipt parsing.
"""

import os
import logging
from datetime import datetime
from typing import Optional

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
from budget import check_budget

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
    """Set or view budget limits."""
    await update.message.reply_text(
        "💰 Budget feature coming soon!\n\n"
        "You'll be able to set monthly limits like:\n"
        "- Food: $500\n"
        "- Transport: $200\n\n"
        "I'll alert you when you're close to your limit."
    )


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export data to Excel."""
    await update.message.reply_text(
        "📤 Export feature coming soon!\n\n"
        "You'll be able to download:\n"
        "- Monthly Excel report\n"
        "- CSV for tax filing\n"
        "- CPF claimable expenses summary"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process receipt photos."""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📸 Processing your receipt...")
    
    try:
        # Get the photo file
        photo = update.message.photo[-1]  # Get largest photo
        photo_file = await photo.get_file()
        
        # Download to memory
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Process with Gemini
        receipt_data = process_receipt(photo_bytes, GEMINI_API_KEY)
        
        if not receipt_data:
            await update.message.reply_text(
                "❌ Sorry, I couldn't read this receipt.\n"
                "Try sending a clearer photo with good lighting."
            )
            return
        
        # Categorize the vendor
        category = categorize_vendor(receipt_data['vendor'])
        
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
    
    # Photo handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Text handler (for non-commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
