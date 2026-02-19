"""
Tests for receipt processor (with mocked Gemini API).
"""

import pytest
from unittest.mock import Mock, patch
import json


class TestProcessReceipt:
    """Test receipt processing with mocked Gemini."""
    
    @patch('receipt_processor.genai')
    def test_successful_extraction(self, mock_genai):
        """Should extract receipt data successfully."""
        from receipt_processor import process_receipt
        
        # Mock the Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'vendor': 'NTUC FairPrice',
            'amount': 47.85,
            'date': '2024-02-19',
            'items': ['Milk', 'Bread']
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create dummy image bytes
        image_bytes = bytearray(b'dummy_image_data')
        
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is not None
        assert result['vendor'] == 'NTUC FairPrice'
        assert result['amount'] == 47.85
        assert result['date'] == '2024-02-19'
        assert result['items'] == ['Milk', 'Bread']
    
    @patch('receipt_processor.genai')
    def test_missing_optional_fields(self, mock_genai):
        """Should handle missing optional fields."""
        from receipt_processor import process_receipt
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'vendor': 'Grab',
            'amount': 12.50
            # Missing date and items
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        image_bytes = bytearray(b'dummy_image_data')
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is not None
        assert result['vendor'] == 'Grab'
        assert result['amount'] == 12.50
        assert result.get('date') is None
        assert result.get('items') == []
    
    @patch('receipt_processor.genai')
    def test_invalid_json_response(self, mock_genai):
        """Should handle invalid JSON from Gemini."""
        from receipt_processor import process_receipt
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Not valid JSON"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        image_bytes = bytearray(b'dummy_image_data')
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is None
    
    @patch('receipt_processor.genai')
    def test_missing_required_fields(self, mock_genai):
        """Should return None if required fields missing."""
        from receipt_processor import process_receipt
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'date': '2024-02-19'
            # Missing vendor and amount
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        image_bytes = bytearray(b'dummy_image_data')
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is None
    
    @patch('receipt_processor.genai')
    def test_api_error(self, mock_genai):
        """Should handle API errors gracefully."""
        from receipt_processor import process_receipt
        
        mock_genai.configure.side_effect = Exception("API Error")
        
        image_bytes = bytearray(b'dummy_image_data')
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is None
    
    @patch('receipt_processor.genai')
    def test_amount_as_string(self, mock_genai):
        """Should handle amount as string in JSON."""
        from receipt_processor import process_receipt
        
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'vendor': 'NTUC',
            'amount': '47.85',  # String instead of number
            'date': '2024-02-19'
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        image_bytes = bytearray(b'dummy_image_data')
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is not None
        assert result['amount'] == 47.85  # Converted to float
        assert isinstance(result['amount'], float)
