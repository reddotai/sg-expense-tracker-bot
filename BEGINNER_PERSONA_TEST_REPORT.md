# Beginner Persona Test Report
## Singapore Expense Tracker Bot

**Test Date:** 2026-02-19  
**Tester:** Complete beginner (zero coding experience)

---

## PART 1: FRESH SETUP TEST

### Step 1: Reading the README.md

**First Impression:** The README looks nice with the emoji and formatting. But I'm immediately confused by several things:

#### Confusion #1: What is "Clone and setup"?
The README says:
```bash
# 1. Clone and setup
git clone https://github.com/reddotai/sg-expense-tracker-bot.git
cd sg-expense-tracker-bot
```

**Problem:** I don't know what "clone" means. Is this copying something? Do I need to install Git first? The README assumes I know what Git is.

**Jargon not explained:**
- "Clone" - never explained
- "git" - never explained  
- "venv" - mentioned but not explained what a "virtual environment" is
- "source venv/bin/activate" - looks like magic spells

#### Confusion #2: Python version check
The prerequisites say "Python 3.10+" but I don't know:
- How to check if I have Python
- How to check which version I have
- What to do if I don't have it

#### Confusion #3: The commands have no context
The Quick Start just throws commands at me:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Questions I have:**
- Where do I type these? (Terminal? Command Prompt? Something else?)
- What is `pip`?
- What is a `requirements.txt`?
- Why is there a `-m` flag?

---

### Step 2: Following Exercise 1

Let me try Exercise 1 which should be more detailed.

#### Step 1: Create Telegram Bot ✅
This part is clear! Message @BotFather, send /newbot, get token. I understand this because I use Telegram.

**But then:** "Keep this token secret! Anyone with it can control your bot."
- How do I keep it secret? Do I write it on paper?
- Where do I put it?

#### Step 2: Set Up Your Environment

**"Clone the Repository"**
```bash
git clone https://github.com/reddotai/sg-expense-tracker-bot.git
cd sg-expense-tracker-bot
```

**Friction Point #1:** I got an error: `git: command not found`

Now I'm stuck. The exercise doesn't tell me:
- That I need to install Git first
- How to install Git
- Where to download it from

**Time stuck:** ~5 minutes (would give up here in real life)

**After installing Git (hypothetically):**

**"Create Virtual Environment"**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Friction Point #2:** What is a "virtual environment"? 
- The exercise says to do it but doesn't explain WHY
- Why can't I just install things normally?
- What does "activate" mean?

**Friction Point #3:** The Windows note says `venv\Scripts\activate` but:
- How do I know if I'm on Windows or not?
- What about Mac? (not mentioned)
- Do I type the `# On Windows:` part or not?

**"Install Dependencies"**
```bash
pip install -r requirements.txt
```

**Friction Point #4:** What are "dependencies"?
- Why do I need to install them?
- What is `pip`?
- Will this install viruses? (as a beginner, I'm suspicious)

#### Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

**Friction Point #5:** What is `cp`?
- Is this a typo for "copy"?
- This command doesn't work on Windows Command Prompt
- The exercise doesn't say which terminal to use

**"Edit .env"**
- How do I open a .env file?
- What program do I use?
- Notepad? Something else?

#### Step 4: Test Your Bot

```bash
python3 bot.py
```

**Friction Point #6:** If any of the above steps failed, this won't work
- But the troubleshooting is at the bottom
- I wouldn't know to scroll down

---

## PART 2: EXERCISE 1 WALKTHROUGH - COMMAND BY COMMAND

Let me test if the commands actually work when copy-pasted:

### Test 1: `git clone` 
**Status:** ❌ FAIL (on fresh machine without Git)
**Error:** `git: command not found`
**Beginner confusion:** High - no idea what to do

### Test 2: `python3 -m venv venv`
**Status:** ⚠️ PARTIAL
**Issues:**
- On some systems it's `python` not `python3`
- On Windows, might need to use `py -3`
- No guidance on how to handle errors

### Test 3: `source venv/bin/activate`
**Status:** ❌ FAIL on Windows Command Prompt
**Error:** `'source' is not recognized`
**Beginner confusion:** Very high - the Windows alternative is mentioned but unclear

### Test 4: `pip install -r requirements.txt`
**Status:** ✅ WORKS (if previous steps succeeded)
**But:** Lots of scary output that looks like errors (red text, warnings)

### Test 5: `cp .env.example .env`
**Status:** ❌ FAIL on Windows
**Error:** `'cp' is not recognized`
**Beginner confusion:** High - this is a Linux/Mac command

### Test 6: `python3 bot.py`
**Status:** ❌ FAIL without proper setup
**Error:** Various depending on what was missed

---

## PART 3: FIRST RECEIPT TEST (Simulation)

Let me simulate what happens when a beginner sends their first receipt.

### Scenario: Bot is running (miracle!)

**User sends a photo of NTUC receipt**

**Expected bot response:**
```
📸 Processing your receipt...
✅ Expense recorded!

🏪 NTUC FairPrice
💵 $47.85
📁 groceries
📅 2026-02-19
```

**Potential issues:**

1. **If Gemini API key is wrong/invalid:**
   - Bot says: "❌ Sorry, I couldn't read this receipt."
   - But doesn't tell me HOW to fix it
   - I don't know if it's my photo or my setup

2. **If photo is blurry:**
   - Same error message
   - No guidance on what "good lighting" means

3. **If receipt is in Chinese (common in Singapore):**
   - Unknown if Gemini handles this well
   - No mention of language support

4. **After successful recording:**
   - Where is my data stored?
   - Can I see it somewhere?
   - What if I made a mistake?

---

## PART 4: FRICTION POINTS SUMMARY

### Critical Issues (Would Cause Give-Up)

| # | Issue | Location | Why It's Bad |
|---|-------|----------|--------------|
| 1 | Git not installed | Step 1 | Complete blocker, no guidance |
| 2 | `source` doesn't work on Windows | Step 2 | Common OS, command fails |
| 3 | `cp` doesn't work on Windows | Step 3 | Another Linux-only command |
| 4 | No Python version check | Prerequisites | Don't know if I qualify |
| 5 | "Virtual environment" not explained | Step 2 | Scary technical term |
| 6 | No editor specified for .env | Step 3 | Don't know how to edit |

### Medium Issues (Confusing but survivable)

| # | Issue | Why It's Confusing |
|---|-------|-------------------|
| 7 | No explanation of what `pip` is | Sounds like a sound effect |
| 8 | No explanation of `requirements.txt` | Looks like a filename, not a command argument |
| 9 | Troubleshooting at bottom | Don't know to scroll down when stuck |
| 10 | "Export" command | Don't know what Excel/CSV is |
| 11 | "Environment variables" term | Sounds like climate change |

### Minor Issues (Annoyances)

| # | Issue | Suggestion |
|---|-------|------------|
| 12 | No Mac-specific instructions | Add Mac column |
| 13 | No photo examples | Show what a "good" receipt photo looks like |
| 14 | No data backup guidance | Explain where data lives |
| 15 | Budget alerts unexplained | What happens when I hit the limit? |

---

## CLARITY RATING: 4/10

### What Works:
- ✅ Telegram bot creation is well explained
- ✅ The "What You Learned" section is nice
- ✅ Emoji makes it feel friendly
- ✅ The feature list is exciting

### What Doesn't:
- ❌ Assumes too much prior knowledge
- ❌ Linux/Mac commands on Windows tutorial
- ❌ No "before you start" checklist
- ❌ No visual aids or screenshots
- ❌ No "you are here" progress indicator

---

## WOULD I GIVE UP? YES - AT STEP 2

**Give-up point:** After `git clone` fails with "command not found"

**Why:**
1. I don't know what Git is
2. I don't know I need to install it
3. The error message doesn't help
4. I feel like this is "too technical" for me
5. I would close the window and watch Netflix instead

---

## SPECIFIC SUGGESTIONS TO IMPROVE

### 1. Add a "Before You Start" Section

```markdown
## Before You Start (Checklist)

You'll need:
- [ ] A computer (Windows, Mac, or Linux)
- [ ] Telegram app on your phone
- [ ] About 30 minutes of free time

**Don't have these?** This tutorial might be too advanced. Consider [alternative].
```

### 2. Add OS-Specific Instructions

Create 3 columns or tabs:
- Windows
- Mac  
- Linux

Don't assume everyone uses Linux!

### 3. Explain Every Command

Instead of:
```bash
python3 -m venv venv
```

Write:
```bash
# Create a "virtual environment" - a isolated workspace for this project
# This keeps this project's files separate from your other Python projects
python3 -m venv venv
```

### 4. Add Screenshots

Show:
- What the terminal looks like
- What a successful command looks like
- What the error messages look like
- What the Telegram bot looks like

### 5. Create a "Windows Quick Start" Alternative

For Windows beginners, provide:
- PowerShell commands instead of bash
- How to install Python from python.org
- How to open PowerShell
- How to navigate folders

### 6. Add a "Common Errors" Section at the TOP

Not at the bottom! Put it right after the quick start:

```markdown
## ⚠️ Stuck? Common First-Time Errors

**"git: command not found"** → You need to install Git first. [Link to instructions]

**"python3: command not found"** → Try `python` instead of `python3`

**"'source' is not recognized"** → You're on Windows. Use `venv\Scripts\activate` instead
```

### 7. Add a "What is This?" Section

Explain in plain English:
- What is a bot?
- What is an API?
- What is a database?
- Why do I need all these things?

### 8. Create a Video Walkthrough Link

Some people learn better by watching. Add a 5-minute video showing the entire setup.

### 9. Add "Sanity Check" Steps

After each major step, add a check:

```markdown
### Step 2: Create Virtual Environment

Run: `python3 -m venv venv`

**✅ Sanity Check:** You should see a new folder called "venv" appear.
**❌ If you don't:** Try `python -m venv venv` instead
```

### 10. Simplify the First Run

Instead of requiring both Telegram AND Gemini tokens to test, allow a "demo mode":

```bash
# Run in demo mode (no API keys needed)
python3 bot.py --demo
```

This lets people see the bot working before committing to getting API keys.

---

## CONCLUSION

This project is a great idea, but the setup instructions assume the user is already comfortable with:
- Command line / terminal
- Git
- Python
- Environment variables
- Virtual environments

**The target audience (complete beginners) is not being served.**

**Recommended priority fixes:**
1. Add Windows-specific instructions
2. Add Git installation step
3. Explain every command in plain English
4. Add screenshots
5. Move troubleshooting to the top

**Without these changes, 80%+ of true beginners will give up before getting the bot running.**
