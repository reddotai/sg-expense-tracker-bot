"""
Tests for configuration.
"""

import pytest
import os
from unittest.mock import patch


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validate_config_missing_telegram_token(self):
        """Should return error if TELEGRAM_BOT_TOKEN missing."""
        from config import validate_config
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.TELEGRAM_BOT_TOKEN', None):
                with patch('config.GEMINI_API_KEY', 'test_key'):
                    result = validate_config()
        
        assert result is not None
        assert 'TELEGRAM_BOT_TOKEN' in result
    
    def test_validate_config_missing_gemini_key(self):
        """Should return error if GEMINI_API_KEY missing."""
        from config import validate_config
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.TELEGRAM_BOT_TOKEN', 'test_token'):
                with patch('config.GEMINI_API_KEY', None):
                    result = validate_config()
        
        assert result is not None
        assert 'GEMINI_API_KEY' in result
    
    def test_validate_config_valid(self):
        """Should return None if all config valid."""
        from config import validate_config
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.TELEGRAM_BOT_TOKEN', 'test_token'):
                with patch('config.GEMINI_API_KEY', 'test_key'):
                    result = validate_config()
        
        assert result is None


class TestConfigValues:
    """Test configuration values."""
    
    def test_gst_rate(self):
        """GST rate should be 9%."""
        from config import GST_RATE
        assert GST_RATE == 0.09
    
    def test_default_budgets_exist(self):
        """Should have default budgets for all categories."""
        from config import DEFAULT_BUDGETS
        
        expected_categories = [
            'groceries', 'transport', 'food_delivery', 'hawker',
            'dining', 'petrol', 'shopping', 'utilities',
            'healthcare', 'entertainment', 'others'
        ]
        
        for category in expected_categories:
            assert category in DEFAULT_BUDGETS
            assert DEFAULT_BUDGETS[category] > 0
    
    def test_gemini_model(self):
        """Should use appropriate Gemini model."""
        from config import GEMINI_MODEL
        assert GEMINI_MODEL == 'gemini-1.5-flash'
