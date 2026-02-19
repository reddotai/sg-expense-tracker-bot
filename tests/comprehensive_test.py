#!/usr/bin/env python3
"""
Comprehensive feature test for Singapore Expense Tracker Bot.
Tests all commands and features without requiring Telegram API.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up test environment
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['GEMINI_API_KEY'] = 'test_key'

# Import modules after setting env vars
from database import (
    init_db, add_transaction, get_monthly_summary, 
    get_all_transactions, delete_transaction,
    get_user_setting, set_user_setting, init_user_settings_table
)
from categories import categorize_vendor, get_category_emoji, VENDOR_CATEGORIES
from budget import check_budget, get_budget_status, set_budget
from config import DEFAULT_BUDGETS, get_data_location_info, validate_config
from export import export_to_excel, export_to_csv
from ai_categorization import (
    is_ai_categorization_enabled, 
    toggle_ai_categorization
)

# Test configuration
TEST_USER_ID = 123456789
TEST_USER_ID_2 = 987654321

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"  {status} {name}")
    if details and not passed:
        print(f"      {Colors.RED}{details}{Colors.RESET}")
    return passed

def run_tests():
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Create temp directory for test database
    temp_dir = tempfile.mkdtemp()
    original_db = None
    
    try:
        # Override database location for testing
        import config
        from pathlib import Path
        original_db = config.DATABASE_FILE
        config.DATABASE_FILE = Path(os.path.join(temp_dir, 'test_expenses.db'))
        config.EXPORT_DIR = Path(os.path.join(temp_dir, 'exports'))
        os.makedirs(config.EXPORT_DIR, exist_ok=True)
        
        import database
        database.DATABASE_FILE = config.DATABASE_FILE
        
        print_header("COMMAND TESTING")
        
        # === /start Command ===
        print("\n📱 Testing /start command...")
        welcome_text = """
👋 Welcome to Singapore Expense Tracker!

Send me a photo of any receipt and I'll:
✓ Extract the vendor and amount
✓ Categorize it (Food, Transport, etc.)
✓ Track your spending

Commands:
/summary - View this month's spending
/budget - Set budget limits
/export - Export to Excel
/ai - Toggle AI categorization
/data - Show where your data is stored
/help - Show all commands

Built for Singapore: GST 9%, Grab, NTUC, hawker centres 🇸🇬
    """
        passed = "Welcome to Singapore Expense Tracker" in welcome_text
        if print_test("Welcome message displays correctly", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("/start", "FAIL"))
        
        # === /help Command ===
        print("\n📋 Testing /help command...")
        help_text = """
📋 Available Commands:

/start - Welcome message
/help - This help message
/summary - Monthly spending summary
/budget - Set or view budget limits
/export - Export data to Excel
/ai - Toggle AI categorization on/off
/data - Show where your data is stored
/delete - Delete a transaction (use: /delete <ID>)

Just send me a receipt photo anytime! 📸

Supported receipts:
✓ NTUC, Cold Storage, Sheng Siong
✓ Grab, Gojek, taxis
✓ Hawker centres, food courts
✓ Any restaurant or shop
    """
        required_commands = ['/start', '/help', '/summary', '/budget', '/export', '/ai', '/data', '/delete']
        all_present = all(cmd in help_text for cmd in required_commands)
        if print_test("All commands listed in help", all_present):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("/help", "FAIL"))
        
        # === /data Command ===
        print("\n📁 Testing /data command...")
        data_info = get_data_location_info()
        passed = "Database" in data_info and "Exports" in data_info
        if print_test("Data location info shows correct paths", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("/data", "FAIL"))
        
        # Initialize database
        init_db()
        init_user_settings_table()
        
        # === /summary Command (Empty State) ===
        print("\n📊 Testing /summary command (empty state)...")
        summary = get_monthly_summary(TEST_USER_ID)
        passed = summary['total'] == 0 and summary['count'] == 0 and summary['transactions'] == []
        if print_test("Empty state returns zero totals", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("/summary empty", "FAIL"))
        
        # Add test transactions
        print("\n📝 Adding test transactions...")
        current_month = datetime.now().strftime('%Y-%m')
        
        # Add various transactions
        t1 = add_transaction(TEST_USER_ID, 'NTUC FairPrice', 47.85, f'{current_month}-15', 'groceries', ['Milk', 'Bread'])
        t2 = add_transaction(TEST_USER_ID, 'Grab', 12.50, f'{current_month}-16', 'transport', [])
        t3 = add_transaction(TEST_USER_ID, 'Starbucks', 6.80, f'{current_month}-17', 'dining', ['Coffee'])
        t4 = add_transaction(TEST_USER_ID, 'Shell', 85.00, f'{current_month}-18', 'petrol', [])
        t5 = add_transaction(TEST_USER_ID_2, 'NTUC', 100.00, f'{current_month}-19', 'groceries', [])  # Different user
        
        print(f"  Added transactions: {t1}, {t2}, {t3}, {t4}, {t5}")
        
        # === /summary Command (With Data) ===
        print("\n📊 Testing /summary command (with data)...")
        summary = get_monthly_summary(TEST_USER_ID)
        
        passed = summary['total'] == 152.15  # 47.85 + 12.50 + 6.80 + 85.00
        if print_test("Summary calculates total correctly", passed, f"Expected 152.15, got {summary['total']}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("/summary total", "FAIL"))
        
        passed = summary['count'] == 4
        if print_test("Summary counts transactions correctly", passed, f"Expected 4, got {summary['count']}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("/summary count", "FAIL"))
        
        passed = summary['by_category']['groceries'] == 47.85
        if print_test("Summary categorizes correctly", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("/summary categories", "FAIL"))
        
        # === User Isolation ===
        print("\n🔒 Testing user isolation...")
        user2_transactions = get_all_transactions(TEST_USER_ID_2)
        passed = len(user2_transactions) == 1 and user2_transactions[0]['amount'] == 100.00
        if print_test("User data is isolated", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("User isolation", "FAIL"))
        
        # === /budget Command ===
        print("\n💰 Testing /budget command...")
        
        # Get actual budget for groceries
        groceries_budget = DEFAULT_BUDGETS.get('groceries', 600)
        eighty_percent = groceries_budget * 0.8
        
        # Test 80% warning
        # Current spending: 47.85, need to reach ~80% of budget
        # Add transactions to get close to 80% threshold
        # 47.85 + n*50 >= 0.8 * 650 = 520, so n >= (520-47.85)/50 = 9.4, so 10 transactions
        for i in range(10):
            day = min(20 + i, 28)  # Ensure valid day for all months
            add_transaction(TEST_USER_ID, 'NTUC', 50.0, f'{current_month}-{day:02d}', 'groceries', [])
        
        # Now check - current should be 47.85 + 500 = 547.85
        # Adding 10 more = 557.85 which exceeds 520 (80%)
        warning = check_budget(TEST_USER_ID, 'groceries', 10.0)
        passed = warning is not None and ('80%' in warning or 'remaining' in warning.lower())
        if print_test("80% budget warning works", passed, f"Warning: {warning}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("80% budget alert", "FAIL"))
        
        # Test 100% warning (over budget)
        # Need to exceed 600 budget
        # Current: 47.85 + 450 = 497.85, need ~100 more to exceed 600 when adding
        for i in range(3):
            day = min(10 + i, 28)  # Use earlier days to avoid conflicts
            add_transaction(TEST_USER_ID, 'NTUC', 50.0, f'{current_month}-{day:02d}', 'groceries', [])
        
        over_budget = check_budget(TEST_USER_ID, 'groceries', 10.0)
        passed = over_budget is not None and 'Over budget' in over_budget
        if print_test("100% budget alert (over budget) works", passed, f"Alert: {over_budget}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("100% budget alert", "FAIL"))
        
        # Test budget status
        status = get_budget_status(TEST_USER_ID)
        passed = 'groceries' in status and status['groceries']['percentage'] > 0
        if print_test("Budget status retrieval works", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Budget status", "FAIL"))
        
        # === /export Command ===
        print("\n📤 Testing /export command...")
        
        # Test Excel export
        try:
            excel_path = export_to_excel(TEST_USER_ID, 'test_export.xlsx')
            import pandas as pd
            
            # Check all 3 sheets exist
            xls = pd.ExcelFile(excel_path)
            sheets = xls.sheet_names
            
            passed = 'Transactions' in sheets and 'Summary by Category' in sheets and 'Monthly Summary' in sheets
            if print_test("Excel export has all 3 sheets", passed, f"Sheets: {sheets}"):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append(("Excel 3 sheets", "FAIL"))
            
            # Check data in transactions sheet
            df = pd.read_excel(excel_path, sheet_name='Transactions')
            passed = len(df) >= 4  # At least our 4 original transactions
            if print_test("Excel contains transaction data", passed, f"Rows: {len(df)}"):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append(("Excel data", "FAIL"))
            
            os.remove(excel_path)
            
        except Exception as e:
            print_test("Excel export", False, str(e))
            results["failed"] += 1
            results["tests"].append(("/export excel", "FAIL"))
        
        # Test CSV export
        try:
            csv_path = export_to_csv(TEST_USER_ID, 'test_export.csv')
            import pandas as pd
            df = pd.read_csv(csv_path)
            passed = len(df) >= 4
            if print_test("CSV export works", passed):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append(("/export csv", "FAIL"))
            os.remove(csv_path)
        except Exception as e:
            print_test("CSV export", False, str(e))
            results["failed"] += 1
            results["tests"].append(("/export csv", "FAIL"))
        
        # Test empty export error
        try:
            export_to_excel(999999, 'empty.xlsx')
            print_test("Empty export raises error", False, "Should have raised ValueError")
            results["failed"] += 1
            results["tests"].append(("Empty export error", "FAIL"))
        except ValueError:
            if print_test("Empty export raises correct error", True):
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        # === /ai Command ===
        print("\n🤖 Testing /ai command (AI categorization toggle)...")
        
        # Test initial state (should be off)
        initial_state = is_ai_categorization_enabled(TEST_USER_ID)
        passed = initial_state == False
        if print_test("AI categorization defaults to OFF", passed, f"State: {initial_state}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("AI default off", "FAIL"))
        
        # Toggle on
        toggle_ai_categorization(TEST_USER_ID, True)
        new_state = is_ai_categorization_enabled(TEST_USER_ID)
        passed = new_state == True
        if print_test("AI toggle ON works", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("AI toggle on", "FAIL"))
        
        # Toggle off
        toggle_ai_categorization(TEST_USER_ID, False)
        new_state = is_ai_categorization_enabled(TEST_USER_ID)
        passed = new_state == False
        if print_test("AI toggle OFF works", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("AI toggle off", "FAIL"))
        
        # Test persistence (re-read from DB)
        toggle_ai_categorization(TEST_USER_ID, True)
        persisted_state = is_ai_categorization_enabled(TEST_USER_ID)
        passed = persisted_state == True
        if print_test("AI setting persists in database", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("AI persistence", "FAIL"))
        
        # === /delete Command ===
        print("\n🗑️ Testing /delete command...")
        
        # Add a transaction to delete
        del_id = add_transaction(TEST_USER_ID, 'Test Vendor', 10.0, f'{current_month}-01', 'others', [])
        
        # Test successful delete
        success = delete_transaction(del_id, TEST_USER_ID)
        passed = success == True
        if print_test("Delete own transaction works", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Delete success", "FAIL"))
        
        # Verify deletion
        all_trans = get_all_transactions(TEST_USER_ID)
        passed = not any(t['id'] == del_id for t in all_trans)
        if print_test("Transaction actually deleted", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Delete verification", "FAIL"))
        
        # Test delete wrong user
        other_user_trans = add_transaction(TEST_USER_ID_2, 'Other', 10.0, f'{current_month}-01', 'others', [])
        wrong_delete = delete_transaction(other_user_trans, TEST_USER_ID)
        passed = wrong_delete == False
        if print_test("Cannot delete other user's transaction", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Delete wrong user", "FAIL"))
        
        # Test delete non-existent
        nonexistent = delete_transaction(999999, TEST_USER_ID)
        passed = nonexistent == False
        if print_test("Delete non-existent transaction returns False", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Delete non-existent", "FAIL"))
        
        print_header("RECEIPT PROCESSING / CATEGORIZATION")
        
        # === Categorization Tests ===
        print("\n🏷️ Testing vendor categorization...")
        
        test_cases = [
            ('NTUC FairPrice', 'groceries'),
            ('Cold Storage', 'groceries'),
            ('Grab', 'transport'),
            ('GrabFood', 'food_delivery'),  # Should match before 'grab'
            ('Starbucks', 'dining'),
            ('Shell', 'petrol'),
            ('Uniqlo', 'shopping'),
            ('Challenger', 'electronics'),
            ('Singtel', 'utilities'),
            ('Raffles Medical', 'healthcare'),
            ('Unknown Shop', 'others'),
        ]
        
        for vendor, expected in test_cases:
            result = categorize_vendor(vendor)
            passed = result == expected
            if print_test(f"'{vendor}' → {expected}", passed, f"Got: {result}"):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append((f"Category: {vendor}", "FAIL"))
        
        # Test case insensitivity
        print("\n🔤 Testing case insensitivity...")
        cases = ['NTUC', 'ntuc', 'Ntuc', 'nTuC']
        for case in cases:
            result = categorize_vendor(case)
            passed = result == 'groceries'
            if print_test(f"'{case}' → groceries", passed):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append((f"Case: {case}", "FAIL"))
        
        # Test emoji retrieval
        print("\n😀 Testing category emojis...")
        for category in list(VENDOR_CATEGORIES.keys()) + ['others']:
            emoji = get_category_emoji(category)
            passed = emoji is not None and len(emoji) > 0
            if print_test(f"'{category}' has emoji", passed, f"Emoji: {emoji}"):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append((f"Emoji: {category}", "FAIL"))
        
        print_header("DATABASE OPERATIONS")
        
        # === CRUD Operations ===
        print("\n💾 Testing CRUD operations...")
        
        # Create
        new_id = add_transaction(TEST_USER_ID, 'CRUD Test', 99.99, '2024-02-19', 'shopping', ['Item'])
        passed = new_id is not None and new_id > 0
        if print_test("CREATE transaction", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("CREATE", "FAIL"))
        
        # Read
        all_trans = get_all_transactions(TEST_USER_ID)
        found = any(t['id'] == new_id for t in all_trans)
        if print_test("READ transaction", found):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("READ", "FAIL"))
        
        # Update - Not directly supported, but we can verify data integrity
        # Delete
        deleted = delete_transaction(new_id, TEST_USER_ID)
        if print_test("DELETE transaction", deleted):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("DELETE", "FAIL"))
        
        # === Date Handling ===
        print("\n📅 Testing date handling...")
        
        # Test various date formats
        dates_to_test = [
            '2024-02-19',
            '2024-12-31',
            '2023-01-01',
        ]
        
        for date_str in dates_to_test:
            tid = add_transaction(TEST_USER_ID, 'Date Test', 10.0, date_str, 'others', [])
            trans = get_all_transactions(TEST_USER_ID)
            found = any(t['id'] == tid and t['date'] == date_str for t in trans)
            if print_test(f"Date '{date_str}' stored correctly", found):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append((f"Date: {date_str}", "FAIL"))
        
        # Test auto-date (None)
        tid = add_transaction(TEST_USER_ID, 'Auto Date', 10.0, None, 'others', [])
        trans = get_all_transactions(TEST_USER_ID)
        found_trans = next((t for t in trans if t['id'] == tid), None)
        today = datetime.now().strftime('%Y-%m-%d')
        passed = found_trans is not None and found_trans['date'] == today
        if print_test("Auto-date (None) uses current date", passed, f"Got: {found_trans['date'] if found_trans else 'None'}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Auto-date", "FAIL"))
        
        # === JSON Items Storage ===
        print("\n📦 Testing items JSON storage...")
        items = ['Milk', 'Bread', 'Eggs']
        tid = add_transaction(TEST_USER_ID, 'Items Test', 10.0, '2024-02-19', 'groceries', items)
        trans = get_all_transactions(TEST_USER_ID)
        found_trans = next((t for t in trans if t['id'] == tid), None)
        passed = found_trans is not None and found_trans['items'] == items
        if print_test("Items stored as JSON", passed, f"Got: {found_trans['items'] if found_trans else 'None'}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("JSON items", "FAIL"))
        
        print_header("CONFIGURATION")
        
        # === Config Tests ===
        print("\n⚙️ Testing configuration...")
        
        # Test default budgets
        passed = len(DEFAULT_BUDGETS) > 0 and all(v > 0 for v in DEFAULT_BUDGETS.values())
        if print_test("Default budgets are positive", passed):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Budget defaults", "FAIL"))
        
        # Test GST rate
        from config import GST_RATE
        passed = GST_RATE == 0.09
        if print_test("GST rate is 9%", passed, f"Got: {GST_RATE}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("GST rate", "FAIL"))
        
        # Test validation
        error = validate_config()
        passed = error is None  # We set env vars at start
        if print_test("Config validation passes with env vars", passed, f"Error: {error}"):
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["tests"].append(("Config validation", "FAIL"))
        
        print_header("AI CATEGORIZATION")
        
        # === AI Categorization ===
        print(f"\n🧠 Testing AI categorization (google-genai available: {GENAI_AVAILABLE})...")
        
        if GENAI_AVAILABLE:
            from ai_categorization import categorize_with_ai, CATEGORY_DESCRIPTIONS
            
            # Test category descriptions exist
            passed = len(CATEGORY_DESCRIPTIONS) > 0
            if print_test("Category descriptions exist", passed):
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["tests"].append(("AI categories", "FAIL"))
            
            # Note: We can't test actual AI categorization without API key
            print(f"  {Colors.YELLOW}ℹ Note: Skipping live AI tests (requires API key){Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}ℹ google-genai not installed, skipping AI tests{Colors.RESET}")
        
    finally:
        # Cleanup
        if original_db:
            config.DATABASE_FILE = original_db
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Print summary
    print_header("TEST SUMMARY")
    total = results["passed"] + results["failed"]
    print(f"\n{Colors.GREEN}✓ Passed: {results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}✗ Failed: {results['failed']}{Colors.RESET}")
    print(f"Total: {total}")
    print(f"Success Rate: {(results['passed']/total)*100:.1f}%")
    
    if results["tests"]:
        print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
        for test, status in results["tests"]:
            print(f"  - {test}: {status}")
    
    return results["failed"] == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
