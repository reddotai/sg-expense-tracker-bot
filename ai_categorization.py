#!/usr/bin/env python3
"""
Smart vendor categorization using Gemini AI.
Toggle on/off per user preference.

NOTE: google-genai import is lazy (inside function) to allow bot startup
without the package installed. This lets beginners see friendly errors.
"""

import os
import json
import logging
from typing import Optional

from database import get_user_setting, set_user_setting, check_rate_limit

logger = logging.getLogger(__name__)

# Default categories for AI to choose from
CATEGORY_DESCRIPTIONS = {
    'groceries': 'Food items, supermarkets, convenience stores, daily essentials',
    'transport': 'Taxis, ride-hailing (Grab/Gojek), public transport (MRT/bus), fuel',
    'food_delivery': 'Food delivery apps and services like GrabFood, Foodpanda, Deliveroo',
    'hawker': 'Hawker centres, food courts, local coffee shops (kopitiam), wet market food',
    'dining': 'Restaurants, cafes, fast food, bakeries, bubble tea shops',
    'petrol': 'Gas stations, petrol, diesel, car washes at petrol kiosks',
    'shopping': 'Clothing, retail stores, online shopping platforms (Lazada, Shopee)',
    'electronics': 'Gadgets, computers, appliances, mobile phones, IT accessories',
    'utilities': 'Phone bills, internet, electricity, water, gas (SP Services, telcos)',
    'healthcare': 'Medical, dental, pharmacy, clinics, TCM, health supplements',
    'entertainment': 'Movies, streaming subscriptions, games, gym, karaoke',
    'education': 'School fees, tuition, books, courses, enrichment classes',
    'travel': 'Flights, hotels, travel bookings, travel insurance',
    'insurance': 'Insurance premiums (life, health, car, home)',
    'subscriptions': 'Memberships, recurring subscriptions, gym memberships',
    'personal_care': 'Beauty products, skincare, hair salons, cosmetics, toiletries',
    'others': 'Miscellaneous or unclear expenses'
}


def is_ai_categorization_enabled(user_id: int) -> bool:
    """Check if user has AI categorization enabled."""
    setting = get_user_setting(user_id, 'ai_categorization', 'false')
    return setting.lower() == 'true'


def toggle_ai_categorization(user_id: int, enabled: bool) -> bool:
    """
    Toggle AI categorization for a user.
    
    Args:
        user_id: Telegram user ID
        enabled: True to enable, False to disable
    
    Returns:
        True if successful
    """
    set_user_setting(user_id, 'ai_categorization', 'true' if enabled else 'false')
    return True


def categorize_with_ai(vendor_name: str, api_key: Optional[str] = None) -> Optional[str]:
    """
    Use Gemini AI to categorize an unknown vendor.
    
    Args:
        vendor_name: The vendor name to categorize
        api_key: Gemini API key (optional, uses env var if not provided)
    
    Returns:
        Category string or None if AI categorization fails
    """
    # Lazy import - only load when this function is called
    try:
        from google import genai
    except ImportError:
        logger.warning("google-genai not installed. Cannot use AI categorization.")
        return None
    
    api_key = api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.warning("No Gemini API key available for AI categorization")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Build category descriptions
        categories_text = "\n".join([
            f"- {cat}: {desc}" 
            for cat, desc in CATEGORY_DESCRIPTIONS.items()
        ])
        
        prompt = f"""Categorize this vendor into ONE of these categories:

{categories_text}

Vendor: "{vendor_name}"

Respond with ONLY the category name (lowercase, no punctuation). If unsure, respond with "others".
"""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        category = response.text.strip().lower()
        
        # Validate the category
        valid_categories = list(CATEGORY_DESCRIPTIONS.keys())
        if category in valid_categories:
            logger.info(f"AI categorized '{vendor_name}' as '{category}'")
            return category
        else:
            logger.warning(f"AI returned invalid category '{category}' for '{vendor_name}'")
            return 'others'
            
    except Exception as e:
        logger.error(f"AI categorization failed: {e}")
        return None


def smart_categorize(vendor_name: str, user_id: int, api_key: Optional[str] = None, 
                     skip_ai_rate_limit: bool = False) -> str:
    """
    Smart categorization with fallback to AI if enabled.
    
    1. Try rule-based categorization first (fast, free)
    2. If 'others' and AI is enabled, try Gemini (slower, uses API)
    3. Return 'others' if AI fails or is disabled
    
    Args:
        vendor_name: Vendor name to categorize
        user_id: Telegram user ID (for preference check)
        api_key: Gemini API key (optional)
        skip_ai_rate_limit: If True, bypass AI rate limit (for internal use)
    
    Returns:
        Category string
    """
    from categories import categorize_vendor
    from database import check_rate_limit
    
    # Step 1: Rule-based (fast, always runs)
    category = categorize_vendor(vendor_name)
    
    # Step 2: If unknown and AI enabled, try Gemini
    if category == 'others' and is_ai_categorization_enabled(user_id):
        # Check AI rate limit (20/day) unless bypassed
        if not skip_ai_rate_limit:
            allowed, _ = check_rate_limit(user_id, 'ai_categorization', 20)
            if not allowed:
                logger.info(f"AI categorization rate limit hit for user {user_id}")
                return 'others'
        
        ai_category = categorize_with_ai(vendor_name, api_key)
        if ai_category:
            return ai_category
    
    return category


if __name__ == '__main__':
    # Test AI categorization
    test_vendors = [
        'Some Random Shop',
        'ABC Tuition Centre',
        'Dr Tan Dental Clinic',
        'Happy Gym Fitness',
        'Unknown Bookstore'
    ]
    
    print("Testing AI categorization (requires GEMINI_API_KEY):")
    for vendor in test_vendors:
        category = categorize_with_ai(vendor)
        print(f"  {vendor} → {category or 'AI failed'}")
