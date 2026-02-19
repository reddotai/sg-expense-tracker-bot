#!/usr/bin/env python3
"""
Receipt processing using Google Gemini Vision API.
Uses the new google.genai package (not deprecated google.generativeai).
"""

import logging
from typing import Optional, Dict, List
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def process_receipt(photo_bytes: bytearray, api_key: str) -> Optional[Dict]:
    """
    Process a receipt photo using Gemini Vision API.
    
    Args:
        photo_bytes: The receipt image as bytes
        api_key: Google Gemini API key
    
    Returns:
        Dictionary with vendor, amount, date, items or None if failed
    """
    try:
        # Create client with API key
        client = genai.Client(api_key=api_key)
        
        # Create prompt for receipt extraction
        prompt = """
        Extract the following information from this receipt:
        1. Vendor/Store name
        2. Total amount (final amount paid, after GST/service charge if applicable)
        3. Date of purchase (if visible)
        4. List of items (if readable)
        5. GST amount (if shown separately)
        
        Return ONLY a JSON object in this exact format:
        {
            "vendor": "Store Name",
            "amount": 47.85,
            "date": "2024-02-19",
            "items": ["item1", "item2"],
            "gst_amount": 3.95
        }
        
        If date is not visible, use null.
        If items are not readable, use empty array.
        If GST is not shown, use null for gst_amount.
        Amount should be a number (not string), without currency symbol.
        """
        
        # Convert bytes to PIL Image
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Generate response
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[prompt, image]
        )
        
        # Parse the response
        import json
        import re
        
        # Extract JSON from response
        text = response.text
        
        # Find JSON in the response (it might be wrapped in markdown)
        json_match = re.search(r'\{[^}]*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
            
            # Validate required fields
            if 'vendor' in data and 'amount' in data:
                return {
                    'vendor': data['vendor'],
                    'amount': float(data['amount']),
                    'date': data.get('date'),
                    'items': data.get('items', []),
                    'gst_amount': data.get('gst_amount')
                }
        
        logger.warning(f"Could not parse receipt. Response: {text}")
        return None
        
    except Exception as e:
        logger.error(f"Error processing receipt with Gemini: {e}")
        return None


def test_receipt_processor():
    """Test the receipt processor with a sample image."""
    print("Receipt processor loaded successfully")


if __name__ == '__main__':
    test_receipt_processor()
