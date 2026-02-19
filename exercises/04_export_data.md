# Exercise 4: Export to Excel

## Goal
Add `/export` command that generates Excel with monthly breakdown.

**Time:** 1 hour  
**Prerequisites:** Exercises 1-3 complete

---

## Step 1: Understand the Export Module

Open `export.py` — this file already exists with TODO marker.

Look at the main function:

```python
def export_to_excel(user_id: int, filename: Optional[str] = None) -> str:
    """
    Export user transactions to Excel file.
    """
    # Get all transactions
    transactions = get_all_transactions(user_id)
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Create Excel with multiple sheets
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: All transactions
        df.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Sheet 2: Summary by category
        summary = df.groupby('category')['amount'].agg(['sum', 'count'])
        summary.to_excel(writer, sheet_name='Summary by Category')
        
        # Sheet 3: Monthly summary
        ...
    
    return filename
```

---

## Step 2: Add the Export Command

### Find Command Handlers in bot.py

Look for where commands are registered in `main()`:

```python
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("summary", summary_command))
```

### Add Import

At the top of `bot.py`, add:

```python
from export import export_to_excel
```

### Create Export Handler

Add this function in `bot.py` (after other command handlers):

```python
async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export expenses to Excel."""
    user_id = update.effective_user.id
    
    await update.message.reply_text("📊 Generating Excel export...")
    
    try:
        # Generate filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"expenses_{user_id}_{timestamp}.xlsx"
        
        # Export to Excel
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
```

### Register the Command

In `main()`, add:

```python
application.add_handler(CommandHandler("export", export_command))
```

### Update Help Text

Find `help_command` and add `/export` to the list:

```python
help_text = """
📋 Available Commands:

/start - Welcome message
/help - This help message
/summary - Monthly spending summary
/export - Export data to Excel  # <-- ADD THIS
/budget - Set or view budget limits

Just send me a receipt photo anytime! 📸
"""
```

---

## Step 3: Test the Export

### Run the Bot

```bash
python3 bot.py
```

### Send Some Receipts First

Send 3-5 receipt photos to build up some data.

### Test Export Command

Send: `/export`

You should receive:
1. "📊 Generating Excel export..." message
2. An Excel file as a document

### Open the Excel File

The file should have 3 sheets:

**Sheet 1: Transactions**
| id | vendor | amount | date | category | ... |
|----|--------|--------|------|----------|-----|
| 1 | NTUC | 47.85 | 2024-02-19 | groceries | ... |
| 2 | Grab | 12.50 | 2024-02-19 | transport | ... |

**Sheet 2: Summary by Category**
| category | Total Amount | Transaction Count |
|----------|--------------|-------------------|
| groceries | 47.85 | 1 |
| transport | 12.50 | 1 |

**Sheet 3: Monthly Summary**
| month | amount |
|-------|--------|
| 2024-02 | 60.35 |

---

## Step 4: Customize the Export

### Add GST Column

Modify `export_to_excel` to calculate GST:

```python
# In export.py, after creating DataFrame
df['gst_amount'] = df['amount'] * 0.09 / 1.09  # 9% GST
df['amount_before_gst'] = df['amount'] - df['gst_amount']

# Reorder columns
columns = ['date', 'vendor', 'category', 'amount_before_gst', 'gst_amount', 'amount', 'items']
df = df[columns]
```

### Add Filtering

Let users export specific months:

```python
# In bot.py, modify export_command
async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check for month argument
    args = context.args
    if args:
        month = args[0]  # e.g., "2024-02"
        filename = f"expenses_{month}.xlsx"
    else:
        filename = None  # All data
    
    filepath = export_to_excel(user_id, filename, month=month)
```

---

## Step 5: Add CSV Export Option

### Create CSV Handler

Add to `bot.py`:

```python
async def export_csv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export to CSV format."""
    from export import export_to_csv
    
    user_id = update.effective_user.id
    filename = export_to_csv(user_id)
    
    with open(filename, 'rb') as f:
        await update.message.reply_document(
            document=f,
            filename=filename,
            caption="📄 CSV export ready!"
        )
    
    os.remove(filename)
```

### Register

```python
application.add_handler(CommandHandler("exportcsv", export_csv_command))
```

---

## Troubleshooting

### "No module named 'openpyxl'"

**Problem:** Dependency not installed  
**Fix:**
```bash
pip install openpyxl pandas
```

### "No transactions to export"

**Problem:** Database is empty  
**Fix:** Send some receipt photos first, then try `/export` again

### File not sending

**Problem:** File might be too large  
**Check:** Telegram has a 50MB limit for documents

### Excel won't open

**Problem:** File might be corrupted  
**Debug:** Check if file exists and has content:
```python
import os
print(os.path.getsize(filename))  # Should be > 0
```

---

## What You Learned

- Working with pandas and Excel
- File handling in Telegram bots
- Multi-sheet Excel generation
- Data aggregation and summarization
- User file delivery

---

## Bonus: Tax-Ready Export

Create a special export for tax filing:

```python
def export_for_taxes(user_id: int) -> str:
    """Export only tax-deductible expenses."""
    transactions = get_all_transactions(user_id)
    
    # Filter for tax-deductible categories
    tax_categories = ['healthcare', 'education', 'insurance']
    tax_expenses = [t for t in transactions if t['category'] in tax_categories]
    
    # Create summary for tax filing
    df = pd.DataFrame(tax_expenses)
    # ... format for IRAS submission
    
    return filename
```

---

## 🎉 You Completed All Exercises!

You now have a working Singapore Expense Tracker bot that:
- ✅ Processes receipt photos with AI
- ✅ Auto-categorizes Singapore vendors
- ✅ Tracks your spending
- ✅ Exports to Excel

**Better than any SkillsFuture course.**

Share your bot with friends, add more features, or build something new!

---

## What to Build Next

Ideas for extending your bot:

1. **Budget alerts** — Warn when overspending
2. **Monthly reports** — Auto-send summary on 1st of month
3. **Shared expenses** — Split bills with friends
4. **Recurring expenses** — Track subscriptions
5. **Web dashboard** — View expenses in browser

---

**Built in 3 hours. No certificate required.**
