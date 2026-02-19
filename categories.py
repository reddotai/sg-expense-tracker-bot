#!/usr/bin/env python3
"""
Singapore vendor categorization.
Maps common vendors to spending categories.
"""

# Singapore vendor categories
# NOTE: Order matters! More specific patterns should come BEFORE general ones
# e.g., 'grabfood' before 'grab', 'cs fresh' before 'cs'
VENDOR_CATEGORIES = {
    # Groceries
    'groceries': [
        'ntuc', 'fairprice', 'cold storage', 'sheng siong', 'giant',
        'prime supermarket', 'market place', 'little farms', 'cs fresh',
        'fair price', 'shengsiong', '7-eleven', 'cheers'
    ],
    
    # Food Delivery (MUST come before transport to match GrabFood before Grab)
    'food_delivery': [
        'grabfood', 'foodpanda', 'deliveroo', 'whyq', 'honestbee'
    ],
    
    # Transport
    'transport': [
        'grab', 'gojek', 'comfortdelgro', 'comfort', 'citycab', 'taxi',
        'go-jek', 'grabshare', 'grabcar', 'grabhitch', 'cdg', 'transcab',
        'gojek'
    ],
    
    # Hawker / Food Court
    'hawker': [
        'hawker', 'kopitiam', 'food court', 'food republic', 'koufu',
        'food junction', 'ntuc foodfare', 'kopitiam card'
    ],
    
    # Dining / Restaurants
    'dining': [
        'restaurant', 'cafe', 'coffee', 'starbucks', 'coffee bean',
        'toast box', 'ya kun', 'kfc', 'mcdonald', 'burger king',
        'pizza hut', 'domino', 'subway', 'sushi', 'ramen', 'steakhouse',
        'saizeriya', 'sushi tei', 'crystal jade'
    ],
    
    # Petrol
    'petrol': [
        'shell', 'esso', 'caltex', 'spc', 'sinopec'
    ],
    
    # Electronics (separate from shopping for Exercise 3)
    'electronics': [
        'challenger', 'courts', 'best denki', 'harvey norman',
        'gain city', 'audio house', 'apple store', 'istudio'
    ],
    
    # Shopping / Retail (general)
    'shopping': [
        'uniqlo', 'h&m', 'zara', 'cotton on', 'muji', 'daiso',
        'miniso', 'watsons', 'guardian', 'ntuc unity', 'ikea',
        'lazada', 'shopee', 'amazon'
    ],
    
    # Utilities / Bills
    'utilities': [
        'sp services', 'singtel', 'starhub', 'm1', 'circles.life',
        'gomo', 'giga', 'tpg', 'myrepublic'
    ],
    
    # Healthcare
    'healthcare': [
        'clinic', 'hospital', 'dental', 'pharmacy', 'polyclinic',
        'nuh', 'sgh', 'ttsh', 'mount elizabeth', 'raffles medical'
    ],
    
    # Entertainment
    'entertainment': [
        'cinema', 'golden village', 'shaw', 'cathay', 'netflix',
        'spotify', 'disney+', 'hbo', 'amazon prime', 'youtube'
    ],
}


def categorize_vendor(vendor_name: str) -> str:
    """
    Categorize a vendor based on its name.
    
    Args:
        vendor_name: The vendor/store name
    
    Returns:
        Category string (e.g., 'groceries', 'transport', etc.)
    """
    vendor_lower = vendor_name.lower()
    
    for category, vendors in VENDOR_CATEGORIES.items():
        for vendor_pattern in vendors:
            if vendor_pattern in vendor_lower:
                return category
    
    # Default category if no match
    return 'others'


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
        'electronics': '💻',
        'utilities': '💡',
        'healthcare': '🏥',
        'entertainment': '🎬',
        'others': '📦'
    }
    return emojis.get(category, '📦')


def add_custom_vendor(user_id: int, vendor_pattern: str, category: str) -> None:
    """
    Add a custom vendor pattern for a user.
    This would be stored in the database.
    """
    # TODO: Implement custom vendor storage
    pass


if __name__ == '__main__':
    # Test categorization
    test_vendors = [
        'NTUC FairPrice',
        'Grab',
        'Starbucks',
        'Shell',
        'Uniqlo',
        'Some Random Shop'
    ]
    
    for vendor in test_vendors:
        category = categorize_vendor(vendor)
        emoji = get_category_emoji(category)
        print(f"{vendor} → {emoji} {category}")
