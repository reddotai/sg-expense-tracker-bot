"""
Tests for vendor categorization.
"""

import pytest
from categories import categorize_vendor, get_category_emoji, VENDOR_CATEGORIES


class TestCategorizeVendor:
    """Test vendor categorization logic."""

    def test_groceries_ntuc(self):
        """NTUC should be categorized as groceries."""
        assert categorize_vendor('NTUC FairPrice') == 'groceries'
        assert categorize_vendor('NTUC Xtra') == 'groceries'
        assert categorize_vendor('FairPrice') == 'groceries'

    def test_groceries_cold_storage(self):
        """Cold Storage should be categorized as groceries."""
        assert categorize_vendor('Cold Storage') == 'groceries'
        assert categorize_vendor('CS Fresh') == 'groceries'

    def test_transport_grab(self):
        """Grab should be categorized as transport."""
        assert categorize_vendor('Grab') == 'transport'
        assert categorize_vendor('GrabShare') == 'transport'
        assert categorize_vendor('GrabCar') == 'transport'

    def test_transport_gojek(self):
        """Gojek should be categorized as transport."""
        assert categorize_vendor('Gojek') == 'transport'
        assert categorize_vendor('Go-Jek') == 'transport'

    def test_food_delivery(self):
        """Food delivery apps should be categorized correctly."""
        assert categorize_vendor('GrabFood') == 'food_delivery'
        assert categorize_vendor('Foodpanda') == 'food_delivery'
        assert categorize_vendor('Deliveroo') == 'food_delivery'

    def test_hawker(self):
        """Hawker centres should be categorized correctly."""
        assert categorize_vendor('Kopitiam') == 'hawker'
        assert categorize_vendor('Food Republic') == 'hawker'
        assert categorize_vendor('Koufu') == 'hawker'

    def test_dining(self):
        """Restaurants should be categorized as dining."""
        assert categorize_vendor('Starbucks') == 'dining'
        assert categorize_vendor('KFC') == 'dining'
        assert categorize_vendor('McDonald\'s') == 'dining'

    def test_petrol(self):
        """Petrol stations should be categorized correctly."""
        assert categorize_vendor('Shell') == 'petrol'
        assert categorize_vendor('Esso') == 'petrol'
        assert categorize_vendor('Caltex') == 'petrol'

    def test_shopping(self):
        """Retail stores should be categorized as shopping."""
        assert categorize_vendor('Uniqlo') == 'shopping'
        assert categorize_vendor('H&M') == 'shopping'
        assert categorize_vendor('IKEA') == 'shopping'

    def test_electronics(self):
        """Electronics stores should be categorized correctly."""
        assert categorize_vendor('Challenger') == 'electronics'
        assert categorize_vendor('Courts') == 'electronics'
        assert categorize_vendor('Best Denki') == 'electronics'

    def test_utilities(self):
        """Utility providers should be categorized correctly."""
        assert categorize_vendor('SP Services') == 'utilities'
        assert categorize_vendor('Singtel') == 'utilities'
        assert categorize_vendor('Starhub') == 'utilities'

    def test_healthcare(self):
        """Healthcare providers should be categorized correctly."""
        assert categorize_vendor('Raffles Medical') == 'healthcare'
        assert categorize_vendor('Polyclinic') == 'healthcare'

    def test_personal_care(self):
        """Beauty/Personal care stores should be categorized correctly."""
        assert categorize_vendor('Watsons') == 'personal_care'
        assert categorize_vendor('Guardian') == 'personal_care'
        assert categorize_vendor('Sephora') == 'personal_care'

    def test_case_insensitive(self):
        """Categorization should be case-insensitive."""
        assert categorize_vendor('NTUC') == 'groceries'
        assert categorize_vendor('ntuc') == 'groceries'
        assert categorize_vendor('Ntuc') == 'groceries'
        assert categorize_vendor('nTuC') == 'groceries'

    def test_partial_match(self):
        """Partial matches should work."""
        assert categorize_vendor('NTUC FairPrice Xtra') == 'groceries'
        assert categorize_vendor('My Local NTUC') == 'groceries'

    def test_unknown_vendor(self):
        """Unknown vendors should default to 'others'."""
        assert categorize_vendor('Some Random Shop') == 'others'
        assert categorize_vendor('Unknown Vendor 123') == 'others'
        assert categorize_vendor('') == 'others'


class TestCategoryEmoji:
    """Test emoji retrieval."""

    def test_all_categories_have_emojis(self):
        """Every category should have an emoji."""
        for category in VENDOR_CATEGORIES.keys():
            emoji = get_category_emoji(category)
            assert emoji is not None
            assert len(emoji) > 0

    def test_specific_emojis(self):
        """Test specific emoji mappings."""
        assert get_category_emoji('groceries') == '🛒'
        assert get_category_emoji('transport') == '🚗'
        assert get_category_emoji('dining') == '🍽️'
        assert get_category_emoji('electronics') == '💻'
        assert get_category_emoji('personal_care') == '💄'

    def test_unknown_category_returns_default(self):
        """Unknown categories should return default emoji."""
        assert get_category_emoji('unknown_category') == '📦'
