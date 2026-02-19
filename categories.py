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
        'fair price', 'shengsiong', '7-eleven', 'cheers', 'shell select',
        'petrol station mart', 'mobil', 'essomart', 'coldstorage'
    ],
    
    # Food Delivery (MUST come before transport to match GrabFood before Grab)
    'food_delivery': [
        'grabfood', 'foodpanda', 'deliveroo', 'whyq', 'honestbee',
        'panda', 'deliveroo', 'food panda'
    ],
    
    # Transport
    'transport': [
        'grab', 'gojek', 'comfortdelgro', 'comfort', 'citycab', 'taxi',
        'go-jek', 'grabshare', 'grabcar', 'grabhitch', 'cdg', 'transcab',
        'gojek', 'ryde', 'tada', 'zig', 'public transport', 'bus', 'mrt',
        'smrt', 'sbs transit', 'simplygo', 'simply go', 'ez-link', 'ezlink'
    ],
    
    # Hawker / Food Court
    'hawker': [
        'hawker', 'kopitiam', 'food court', 'food republic', 'koufu',
        'food junction', 'ntuc foodfare', 'kopitiam card', 'hawker centre',
        'market', 'coffee shop', 'coffeeshop', 'taman jurong', 'maxwell',
        'newton', 'chomp chomp', 'east coast lagoon', 'satay by the bay'
    ],
    
    # Dining / Restaurants
    'dining': [
        'restaurant', 'cafe', 'coffee', 'starbucks', 'coffee bean',
        'toast box', 'ya kun', 'kfc', 'mcdonald', 'burger king',
        'pizza hut', 'domino', 'subway', 'sushi', 'ramen', 'steakhouse',
        'saizeriya', 'sushi tei', 'crystal jade', 'din tai fung',
        'jollibean', 'mr bean', 'breadtalk', 'four leaves', 'prima deli',
        ' Bengawan Solo', 'tiong bahru bakery', 'artisan', 'baker',
        'old chang kee', 'bugis street', 'pasta', 'pizza', 'hotpot',
        'bbq', 'steamboat', 'buffet', 'dim sum', 'yum cha'
    ],
    
    # Petrol
    'petrol': [
        'shell', 'esso', 'caltex', 'spc', 'sinopec'
    ],
    
    # Electronics (separate from shopping for Exercise 3)
    'electronics': [
        'challenger', 'courts', 'best denki', 'harvey norman',
        'gain city', 'audio house', 'apple store', 'istudio',
        'sim lim', 'funan', 'mustafa', 'ban leong'
    ],
    
    # Shopping / Retail (general)
    'shopping': [
        'uniqlo', 'h&m', 'zara', 'cotton on', 'muji', 'daiso',
        'miniso', 'watsons', 'guardian', 'ntuc unity', 'ikea',
        'lazada', 'shopee', 'amazon', 'qoo10', 'carousell',
        'tangs', 'takashimaya', 'isetan', 'metro', 'robinsons',
        'og', 'bugis junction', 'vivo city', 'ion orchard',
        'paragon', 'suntec', 'marina bay sands', 'jewel',
        'plaza singapura', 'centrepoint', 'far east plaza'
    ],
    
    # Utilities / Bills
    'utilities': [
        'sp services', 'singtel', 'starhub', 'm1', 'circles.life',
        'gomo', 'giga', 'tpg', 'myrepublic', 'senoko', 'sembcorp',
        'pacific light', 'keppel electric', 'tuas power',
        'pUB', 'water', 'electricity', 'gas'
    ],
    
    # Healthcare
    'healthcare': [
        'clinic', 'hospital', 'dental', 'pharmacy', 'polyclinic',
        'nuh', 'sgh', 'ttsh', 'mount elizabeth', 'raffles medical',
        'parkway', 'gleneagles', 'thomson', 'kwong wai shiu',
        'tcm', 'traditional chinese medicine', 'physio', 'chiro'
    ],
    
    # Entertainment
    'entertainment': [
        'cinema', 'golden village', 'shaw', 'cathay', 'netflix',
        'spotify', 'disney+', 'hbo', 'amazon prime', 'youtube',
        'gym', 'fitness', 'anytime fitness', 'fitness first',
        'true fitness', 'amusement', 'arcade', 'bowling',
        'karaoke', 'ktv', 'party world', 'teo heng'
    ],
    
    # Education
    'education': [
        'school', 'tuition', 'enrichment', 'kumon', 'mindchamps',
        'learning lab', 'berkeley', 'british council', 'han',
        'book', 'popular', 'kinokuniya', 'times', 'mPH'
    ],
    
    # Travel
    'travel': [
        'airline', 'singapore airlines', 'scoot', 'jetstar', 'airasia',
        'hotel', 'agoda', 'booking.com', 'expedia', 'trip.com',
        'airbnb', 'traveloka', 'klook', 'changiairport'
    ],
    
    # Insurance
    'insurance': [
        'insurance', 'prudential', 'aia', 'ntuc income', 'great eastern',
        'manulife', 'axa', 'aviva', 'fwd', 'singlife'
    ],
    
    # Memberships/Subscriptions
    'subscriptions': [
        'membership', 'subscription', 'ntuc membership', 'costco',
        'amazon prime', 'ntuc plus'
    ]
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
        'education': '📚',
        'travel': '✈️',
        'insurance': '🛡️',
        'subscriptions': '📋',
        'others': '📦'
    }
    return emojis.get(category, '📦')


def get_all_categories() -> list:
    """Return list of all category names."""
    return list(VENDOR_CATEGORIES.keys()) + ['others']


if __name__ == '__main__':
    # Test categorization
    test_vendors = [
        'NTUC FairPrice',
        'Grab',
        'Starbucks',
        'Shell',
        'Uniqlo',
        'Some Random Shop',
        'Singapore Airlines',
        'Prudential Insurance',
        'Popular Bookstore',
        'Anytime Fitness'
    ]
    
    for vendor in test_vendors:
        category = categorize_vendor(vendor)
        emoji = get_category_emoji(category)
        print(f"{vendor} → {emoji} {category}")
