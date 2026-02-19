"""
Tests for receipt processor (with mocked Gemini API and PIL).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestProcessReceipt:
    """Test receipt processing with mocked dependencies."""
    
    @patch('receipt_processor.genai.Client')
    @patch('PIL.Image.open')
    def test_successful_extraction(self, mock_image_open, mock_client_class):
        """Should extract receipt data successfully."""
        from receipt_processor import process_receipt
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        # Mock the Gemini client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'vendor': 'NTUC FairPrice',
            'amount': 47.85,
            'date': '2024-02-19',
            'items': ['Milk', 'Bread'],
            'gst_amount': 3.95
        })
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        # Create dummy image bytes
        image_bytes = bytearray(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is not None
        assert result['vendor'] == 'NTUC FairPrice'
        assert result['amount'] == 47.85
        assert result['date'] == '2024-02-19'
        assert result['items'] == ['Milk', 'Bread']
        assert result['gst_amount'] == 3.95
    
    @patch('receipt_processor.genai.Client')
    @patch('PIL.Image.open')
    def test_missing_optional_fields(self, mock_image_open, mock_client_class):
        """Should handle missing optional fields."""
        from receipt_processor import process_receipt
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'vendor': 'Grab',
            'amount': 12.50
            # Missing date, items, and gst_amount
        })
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        image_bytes = bytearray(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is not None
        assert result['vendor'] == 'Grab'
        assert result['amount'] == 12.50
        assert result.get('date') is None
        assert result.get('items') == []
    
    @patch('receipt_processor.genai.Client')
    @patch('PIL.Image.open')
    def test_invalid_json_response(self, mock_image_open, mock_client_class):
        """Should handle invalid JSON from Gemini."""
        from receipt_processor import process_receipt
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Not valid JSON"
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        image_bytes = bytearray(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is None
    
    @patch('receipt_processor.genai.Client')
    @patch('PIL.Image.open')
    def test_missing_required_fields(self, mock_image_open, mock_client_class):
        """Should return None if required fields missing."""
        from receipt_processor import process_receipt
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'date': '2024-02-19'
            # Missing vendor and amount
        })
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        image_bytes = bytearray(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is None
    
    @patch('receipt_processor.genai.Client')
    @patch('PIL.Image.open')
    def test_api_error(self, mock_image_open, mock_client_class):
        """Should handle API errors gracefully."""
        from receipt_processor import process_receipt
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        mock_client_class.side_effect = Exception("API Error")
        
        image_bytes = bytearray(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is None
    
    @patch('receipt_processor.genai.Client')
    @patch('PIL.Image.open')
    def test_amount_as_string(self, mock_image_open, mock_client_class):
        """Should handle amount as string in JSON."""
        from receipt_processor import process_receipt
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            'vendor': 'NTUC',
            'amount': '47.85',  # String instead of number
            'date': '2024-02-19'
        })
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        image_bytes = bytearray(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        result = process_receipt(image_bytes, 'fake_api_key')
        
        assert result is not None
        assert result['amount'] == 47.85  # Converted to float
        assert isinstance(result['amount'], float)
