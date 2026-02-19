# Exercise 2: Process a Receipt

## Goal
Send a photo → Extract text with Gemini → Parse amount and vendor.

**Time:** 1 hour  
**Prerequisites:** Exercise 1 complete, Google account

---

## Step 1: Get Your Gemini API Key

### Create API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

### Add to .env

Edit your `.env` file:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_token_here
GEMINI_API_KEY=AIzaSyYourActualKeyHere
```

---

## Step 2: Test Receipt Processing

### Create a Test Script

Create `test_receipt.py`:

```python
#!/usr/bin/env python3
"""Test receipt processing without the full bot."""

import os
from dotenv import load_dotenv
from receipt_processor import process_receipt

# Load environment variables
load_dotenv()

# Test with a sample image path
# Replace with an actual receipt photo on your computer
TEST_IMAGE_PATH = "test_receipt.jpg"

def test_with_file():
    """Test receipt processing with a file."""
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not set in .env")
        return
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        print("Please add a receipt photo named 'test_receipt.jpg' to test")
        return
    
    # Read the image
    with open(TEST_IMAGE_PATH, 'rb') as f:
        image_bytes = bytearray(f.read())
    
    print("📸 Processing receipt...")
    result = process_receipt(image_bytes, api_key)
    
    if result:
        print("\n✅ Receipt processed!")
        print(f"Vendor: {result['vendor']}")
        print(f"Amount: ${result['amount']:.2f}")
        print(f"Date: {result.get('date', 'Not found')}")
        if result.get('items'):
            print(f"Items: {', '.join(result['items'][:3])}...")
    else:
        print("❌ Could not process receipt")

if __name__ == '__main__':
    test_with_file()
```

### Run the Test

```bash
python3 test_receipt.py
```

**Expected output:**
```
📸 Processing receipt...

✅ Receipt processed!
Vendor: NTUC FairPrice
Amount: $47.85
Date: 2024-02-19
```

---

## Step 3: Understand How It Works

### Find the Receipt Processor

Open `receipt_processor.py` and look at the `process_receipt` function:

```python
def process_receipt(photo_bytes: bytearray, api_key: str):
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Create prompt
    prompt = """
    Extract the following from this receipt:
    1. Vendor/Store name
    2. Total amount
    3. Date of purchase
    4. List of items
    
    Return ONLY JSON:
    {
        "vendor": "Store Name",
        "amount": 47.85,
        "date": "2024-02-19",
        "items": ["item1", "item2"]
    }
    """
    
    # Send to Gemini
    image = Image.open(io.BytesIO(photo_bytes))
    response = model.generate_content([prompt, image])
    
    # Parse JSON response
    # ... (see full code in file)
```

### Key Concepts

**Gemini Vision API:**
- Sends both text prompt AND image
- AI "looks" at the receipt and extracts data
- Returns structured JSON

**Prompt Engineering:**
- Tell AI exactly what format you want
- Be specific about field names
- Request JSON for easy parsing

---

## Step 4: Test with Your Bot

### Run the Bot

```bash
python3 bot.py
```

### Send a Receipt Photo

1. Find your bot in Telegram
2. Send a photo of any receipt (NTUC, Grab, restaurant, etc.)
3. The bot should respond with:
   ```
   ✅ Expense recorded!
   
   🏪 NTUC FairPrice
   💵 $47.85
   📁 groceries
   📅 2024-02-19
   ```

---

## Step 5: How the Bot Handles Photos

### Find the Photo Handler

In `bot.py`, find `handle_photo`:

```python
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process receipt photos."""
    
    # 1. Get the photo from Telegram
    photo = update.message.photo[-1]  # Largest size
    photo_file = await photo.get_file()
    
    # 2. Download to memory
    photo_bytes = await photo_file.download_as_bytearray()
    
    # 3. Process with Gemini
    receipt_data = process_receipt(photo_bytes, GEMINI_API_KEY)
    
    # 4. Categorize the vendor
    category = categorize_vendor(receipt_data['vendor'])
    
    # 5. Save to database
    transaction_id = add_transaction(...)
    
    # 6. Reply to user
    await update.message.reply_text(message)
```

---

## Troubleshooting

### "Gemini API error"

**Problem:** API key invalid or quota exceeded  
**Fix:**
1. Check key at https://makersuite.google.com/app/apikey
2. Ensure key is in `.env` file
3. Restart the bot

### "Could not process receipt"

**Problem:** Image quality or prompt issues  
**Try:**
- Better lighting when taking photo
- Ensure receipt text is readable
- Check that receipt isn't crumpled

### Wrong amount extracted

**Problem:** Gemini might pick up subtotal instead of total  
**Fix:** This is a known issue. You can:
1. Improve the prompt in `receipt_processor.py`
2. Add validation logic
3. Allow users to correct the amount

---

## Challenge: Improve the Prompt

The current prompt might miss some receipts. Try improving it:

```python
# Current prompt
prompt = """
Extract the following information from this receipt...
"""

# Your improved version
prompt = """
Look at this receipt carefully. Find:
1. Store name at the top
2. FINAL total amount (after GST, not subtotal)
3. Transaction date
4. Main items purchased

Return as JSON...
"""
```

Test with different receipts and see what works best!

---

## What You Learned

- How Gemini Vision API works
- Prompt engineering basics
- Processing images in Python
- Telegram photo handling
- JSON parsing from AI responses

---

## Next Exercise

[→ Exercise 3: Add a New Category](03_add_category.md)

We'll add "Electronics" as a new spending category!
