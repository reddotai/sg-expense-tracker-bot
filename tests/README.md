# Test Suite for Singapore Expense Tracker Bot

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_categories.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## Test Structure

| File | Tests |
|------|-------|
| `test_categories.py` | Vendor categorization |
| `test_database.py` | Database operations |
| `test_budget.py` | Budget calculations |
| `test_receipt_processor.py` | Receipt parsing (mocked) |
| `test_export.py` | Excel/CSV export |
| `test_config.py` | Configuration validation |
| `conftest.py` | Shared fixtures |
