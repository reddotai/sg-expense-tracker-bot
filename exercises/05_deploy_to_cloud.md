# Exercise 5: Deploy Your Bot to the Cloud (1-2 hours)

Your bot works on your computer, but what happens when you close your laptop? In this exercise, you'll deploy your bot to Fly.io's free tier so it stays online 24/7.

## What You'll Learn

- Deploy a Python app to the cloud
- Use Docker (lightly — just a config file)
- Keep secrets safe with environment variables
- Alternative: Run on an old phone or Raspberry Pi for free

---

## Option 1: Deploy to Fly.io (Recommended)

Fly.io offers a generous free tier: 3 small VMs, 256MB RAM each — plenty for a Telegram bot.

### Step 1: Install Fly.io CLI

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
Download from https://fly.io/docs/hands-on/install-flyctl/

### Step 2: Sign Up & Login

```bash
fly auth signup    # Creates account
fly auth login     # Logs you in
```

### Step 3: Create a Dockerfile

In your project folder, create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
```

### Step 4: Create fly.toml

Create `fly.toml` in your project folder:

```toml
app = "your-username-expense-bot"
primary_region = "sin"  # Singapore region

[build]
  dockerfile = "Dockerfile"

[env]
  # Don't put secrets here! We'll set them separately

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

Replace `your-username` with something unique.

### Step 5: Launch Your App

```bash
fly launch
```

This will:
- Create the app
- Ask if you want a database (say **no** — we use SQLite)
- Set up the configuration

### Step 6: Set Your Secrets

```bash
fly secrets set TELEGRAM_BOT_TOKEN="your_token_here"
fly secrets set GEMINI_API_KEY="your_key_here"
```

These are encrypted and only available to your app.

### Step 7: Create a Volume for Data

Your SQLite database needs persistent storage:

```bash
fly volumes create data --size 1 --region sin
```

Update `fly.toml` to mount the volume:

```toml
[mounts]
  source = "data"
  destination = "/app/data"
```

Update `config.py` to use the mounted path:

```python
# For Fly.io deployment
DATA_DIR = Path("/app/data")
```

### Step 8: Deploy!

```bash
fly deploy
```

Watch the logs:
```bash
fly logs
```

Your bot is now live! 🎉

### Step 9: Test It

Send a message to your bot on Telegram. It should respond even if your computer is off.

---

## Option 2: Railway (Alternative)

Railway is similar to Fly.io but has a "sleep after inactivity" limitation on the free tier.

**Pros:**
- Very easy web UI
- Native GitHub integration
- Free $5 credit monthly

**Cons:**
- Free tier sleeps after 1 hour of inactivity
- Bot takes 10-30 seconds to wake up

**Good for:** Low-traffic personal bots where occasional delay is OK.

**Steps:**
1. Go to https://railway.app/
2. Connect your GitHub repo
3. Add environment variables in the dashboard
4. Deploy

---

## Option 3: Old Phone or Raspberry Pi (Free Forever)

Don't want to deal with the cloud? Run it on hardware you already own.

### Using an Old Android Phone

**What you need:**
- Android phone (even old ones work)
- WiFi connection
- Charger (keep it plugged in)

**Steps:**

1. Install **Termux** from F-Droid (not Google Play — that version is outdated)
   ```
   https://f-droid.org/packages/com.termux/
   ```

2. Open Termux and install Python:
   ```bash
   pkg update
   pkg install python git
   ```

3. Clone your repo:
   ```bash
   git clone https://github.com/yourusername/sg-expense-tracker-bot.git
   cd sg-expense-tracker-bot
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export GEMINI_API_KEY="your_key"
   ```

6. Run the bot:
   ```bash
   python bot.py
   ```

7. **Keep it running:** Install `tmux` to keep bot running when you close Termux:
   ```bash
   pkg install tmux
   tmux new -s bot
   python bot.py
   # Press Ctrl+B, then D to detach
   ```

**Tips:**
- Disable battery optimization for Termux
- Keep phone plugged in
- Use a phone you don't need as a daily driver

### Using a Raspberry Pi

**What you need:**
- Raspberry Pi (any model, Zero 2 W works fine)
- SD card (8GB+)
- Power adapter
- WiFi or Ethernet

**Steps:**

1. Install Raspberry Pi OS Lite (headless)
2. Enable SSH and connect
3. Follow the same steps as local deployment:
   ```bash
   sudo apt update
   sudo apt install python3-pip git
   git clone https://github.com/yourusername/sg-expense-tracker-bot.git
   cd sg-expense-tracker-bot
   pip3 install -r requirements.txt
   ```

4. Set up environment variables in `~/.bashrc` or use a `.env` file

5. Run with `tmux` or set up as a systemd service:
   ```bash
   sudo nano /etc/systemd/system/expense-bot.service
   ```

   Add:
   ```ini
   [Unit]
   Description=Expense Tracker Bot
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/sg-expense-tracker-bot
   ExecStart=/usr/bin/python3 /home/pi/sg-expense-tracker-bot/bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable expense-bot
   sudo systemctl start expense-bot
   ```

**Pros:**
- One-time cost (~$15-50)
- No monthly fees
- Your data stays in your home
- Learn Linux basics

**Cons:**
- Requires some Linux knowledge
- Power/internet outages = bot down
- You maintain the hardware

---

## Comparison

| Option | Cost | Difficulty | Always On | Best For |
|--------|------|-----------|-----------|----------|
| **Fly.io** | Free | Medium | ✅ Yes | Learning cloud deployment |
| **Railway** | Free ($5 credit) | Easy | ⚠️ Sleeps | Quick experiments |
| **Old Phone** | Free | Medium | ✅ Yes | Zero cost, privacy-focused |
| **Raspberry Pi** | ~$50 one-time | Harder | ✅ Yes | Tinkerers, learning Linux |
| **VPS** | $5/month | Medium | ✅ Yes | Production, multiple bots |

---

## Troubleshooting

### Fly.io: "No such app"
Make sure your app name in `fly.toml` matches what you created.

### Fly.io: Bot can't write to database
Check that the volume is mounted correctly and `DATA_DIR` in `config.py` points to `/app/data`.

### Phone/Pi: Bot stops when I disconnect
Use `tmux` or `screen` to keep it running, or set up a systemd service.

### "Out of memory" on Fly.io
Your free VM only has 256MB. If you hit limits, reduce dependencies or upgrade to paid tier.

---

## What You Learned

- Cloud deployment basics
- Environment variables for secrets
- Persistent volumes for data
- Alternative: Self-hosting on cheap hardware

**Your bot is now running 24/7!** 🎉

---

## Bonus: Set Up a Custom Domain (Optional)

Want `bot.yourname.com` instead of the Fly.io URL?

```bash
fly certs create bot.yourname.com
```

Then add a CNAME record in your DNS provider pointing to your Fly.io app.

Not needed for Telegram bots (they use webhooks), but good to know!
