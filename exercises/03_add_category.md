# Exercise 3: Add a New Category

## Goal
Add "Electronics" category with vendors like Challenger, Courts, Best Denki.

**Time:** 30 minutes  
**Prerequisites:** Exercises 1-2 complete

---

## Step 1: Find the Categories File

Open `categories.py` and look at `VENDOR_CATEGORIES`:

```python
VENDOR_CATEGORIES = {
    'groceries': [
        'ntuc', 'fairprice', 'cold storage', ...
    ],
    'transport': [
        'grab', 'gojek', 'comfortdelgro', ...
    ],
    # ... more categories
}
```

---

## Step 2: Add Electronics Category

### Add to VENDOR_CATEGORIES

Find this section in `categories.py`:

```python
    # Shopping / Retail
    'shopping': [
        'uniqlo', 'h&m', 'zara', ...
    ],
```

Add after it:

```python
    # Electronics
    'electronics': [
        'challenger', 'courts', 'best denki', 'harvey norman',
        'gain city', 'audio house', 'lazada', 'shopee',
        'apple store', 'istudio', 'samsung', 'sony centre'
    ],
```

---

## Step 3: Add Emoji

### Find get_category_emoji

Look for this function in `categories.py`:

```python
def get_category_emoji(category: str) -> str:
    """Get emoji for category."""
    emojis = {
        'groceries': '🛒',
        'transport': '🚗',
        # ... more emojis
    }
```

### Add Electronics Emoji

Add to the emojis dictionary:

```python
def get_category_emoji(category: str) -> str:
    """Get emoji for category."""
    emojis = {
        'groceries': '🛒',
        'transport': '🚗',
        'food_delivery': '🛵',
        'hawker': '🍜',
        'dining': '🍽️',
        'petrol': '⛽',
        'shopping': '🛍️',
        'electronics': '💻',  # <-- ADD THIS
        'utilities': '💡',
        'healthcare': '🏥',
        'entertainment': '🎬',
        'others': '📦'
    }
    return emojis.get(category, '📦')
```

---

## Step 4: Test Your Changes

### Run the Test Script

Create `test_category.py`:

```python
#!/usr/bin/env python3
"""Test the new electronics category."""

from categories import categorize_vendor, get_category_emoji

# Test vendors
test_vendors = [
    'Challenger',
    'Courts Megastore',
    'Best Denki',
    'Harvey Norman',
    'Apple Store Orchard',
    'Lazada',
    'Shopee',
    'Some Random Shop'
]

print("Testing Electronics Category:\n")

for vendor in test_vendors:
    category = categorize_vendor(vendor)
    emoji = get_category_emoji(category)
    status = "✅" if category == 'electronics' else "❌"
    print(f"{status} {vendor} → {emoji} {category}")
```

### Run It

```bash
python3 test_category.py
```

**Expected output:**
```
Testing Electronics Category:

✅ Challenger → 💻 electronics
✅ Courts Megastore → 💻 electronics
✅ Best Denki → 💻 electronics
✅ Harvey Norman → 💻 electronics
✅ Apple Store Orchard → 💻 electronics
✅ Lazada → 💻 electronics
✅ Shopee → 💻 electronics
❌ Some Random Shop → 📦 others
```

---

## Step 5: Test with Real Receipt

### Run Your Bot

```bash
python3 bot.py
```

### Send an Electronics Receipt

Find an old receipt from:
- Challenger
- Courts
- Best Denki
- Apple Store
- Or any online electronics purchase

Send the photo to your bot. It should now categorize it as **💻 electronics**!

---

## Step 6: Understanding the Logic

### How categorize_vendor Works

```python
def categorize_vendor(vendor_name: str) -> str:
    vendor_lower = vendor_name.lower()
    
    for category, vendors in VENDOR_CATEGORIES.items():
        for vendor_pattern in vendors:
            if vendor_pattern in vendor_lower:  # <-- Key line!
                return category
    
    return 'others'  # Default if no match
```

**How it matches:**
- `'challenger' in 'Challenger'` → True ✅
- `'challenger' in 'Challenger Funan'` → True ✅
- `'challenger' in 'NTUC'` → False ❌

The matching is **case-insensitive** and works with **partial matches**.

---

## Challenge: Add More Categories

Try adding these categories:

### Beauty & Personal Care
```python
'beauty': [
    'watsons', 'guardian', 'sasa', 'sephora',
    'innisfree', 'the body shop', 'l\'occitane'
],
```

### Fitness
```python
'fitness': [
    'gym', 'fitness', 'anytime fitness', 'gymmboxx',
    'active sg', 'pure fitness', 'virgin active'
],
```

Remember to:
1. Add the category to `VENDOR_CATEGORIES`
2. Add an emoji to `get_category_emoji()`
3. Test with real or example receipts

---

## Troubleshooting

### Vendor not matching

**Problem:** Pattern not found  
**Check:**
```python
# Test in Python
vendor = "Courts Nojima"
pattern = "courts"
print(pattern in vendor.lower())  # Should be True
```

### Wrong category assigned

**Problem:** Vendor matches multiple patterns  
**Example:**
- `'shopee'` might match both `shopping` and `electronics`
- **Solution:** The first match wins, so order matters in `VENDOR_CATEGORIES`

---

## What You Learned

- How vendor categorization works
- Pattern matching in Python
- Adding features to existing code
- Testing changes incrementally

---

## Next Exercise

[→ Exercise 4: Export to Excel](04_export_data.md)

We'll add the `/export` command to download your expenses!
