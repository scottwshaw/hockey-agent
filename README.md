# Hockey Agent

A Python agent that periodically monitors hockey rink websites for new scrimmages and stick & puck sessions. Currently configured for **IceHQ Melbourne** (icehq.com.au).

**Run locally OR deploy to AWS Lambda!** ☁️

## Features

- **Smart monitoring**: Tracks session availability status, not just new sessions
- **Spot detection**: Notifies when previously sold-out sessions become available (someone dropped out!)
- **Day filtering**: Only monitor specific days of the week you care about
- **Session type filtering**: Choose which session types to track (stick & puck, scrimmage, etc.)
- **Booked session tracking**: Won't notify you about sessions you've already booked
- **Playwright-powered**: Fast, reliable browser automation that works locally and in AWS Lambda
- **Configurable check intervals**: Set how often to check (recommended: 15-30 minutes)
- **SMS notifications via Twilio**: Get texted when spots open up!
- **AWS Lambda ready**: Deploy to the cloud for ~$0/month (plus SMS costs)
- **Status tracking**: JSON-based storage tracks session availability over time

## How It Works

The agent:
1. Uses Playwright to load the IceHQ page and wait for JavaScript to render
2. Finds all product blocks with session data
3. Extracts JSON data containing session dates, times, and inventory status
4. Checks if sessions match your day/date filters
5. Filters out sessions you've already booked
6. Detects sold-out status from inventory data (soldOut field)
7. Compares current status with previous status in storage
8. Sends you an SMS notification when:
   - New sessions appear with availability
   - Previously sold-out sessions become available again (someone dropped out!)

## Quick Start

Choose how you want to run it:

### Option A: Run Locally (Traditional)

Best for: Testing, development, or if you prefer running on your own computer

```bash
# Install and run
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Configure (see Setup below)
cp .env.example .env
# Edit .env with your settings

# Run once to test
python test_scraper.py

# Run continuously (checks every 30 min)
python main.py
```

### Option B: Deploy to AWS Lambda (Recommended)

Best for: Set-it-and-forget-it automation, no computer needed, essentially free

```bash
# One-command deployment
./deploy.sh

# Or follow the detailed guide
See LAMBDA_DEPLOYMENT.md for full instructions
```

**Why Lambda?**
- Runs in the cloud 24/7
- No computer needed
- ~$0/month (within free tier)
- Only pay for SMS (~$0.01 each)
- Auto-scales, always reliable

## Setup

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

This will install Chrome WebDriver automatically via webdriver-manager:

```bash
pip install -r requirements.txt
```

### 3. Configure your preferences

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` to configure:

**Session Filtering:**
- `MONITOR_DAYS`: Days of week (0=Mon, 1=Tue, etc). Example: `0,2,4` for Mon/Wed/Fri
- `MONITOR_DATES`: Specific dates in YYYY-MM-DD format (optional)
- `MONITOR_SESSION_TYPES`: Which types to track (e.g., `stick & puck,scrimmage`)

**Timing:**
- `CHECK_INTERVAL_MINUTES`: How often to check (recommended: 15-30 minutes)

**Browser:**
- `HEADLESS_BROWSER`: Set to `false` to see the browser for debugging

Example `.env` for monitoring Mon/Wed/Fri stick & puck sessions:
```bash
CHECK_INTERVAL_MINUTES=20
MONITOR_DAYS=0,2,4
MONITOR_SESSION_TYPES=stick & puck
HEADLESS_BROWSER=true
```

## Usage

### Test the scraper (recommended first!)

Run the scraper once interactively to test your configuration:

```bash
python test_scraper.py
```

This will:
- Run a single check without starting the scheduler
- Show detailed logs of what it's doing
- Display any sessions found that match your filters
- Let you verify everything works before running continuously

**Tips for testing:**
- First run with `HEADLESS_BROWSER=false` to watch the browser
- Check if your day/date filters are working correctly
- Verify sessions are being detected and categorized properly
- Run it twice to test status change detection

### Run the agent continuously

Once testing looks good, start the scheduler:

```bash
python main.py
```

The agent will:
1. Run an initial check immediately
2. Schedule periodic checks based on `CHECK_INTERVAL_MINUTES`
3. Monitor for:
   - New sessions that match your filters and are available
   - Previously sold-out sessions that now have spots available
4. Track session availability status in `seen_sessions.json`
5. Notify you when spots open up!

Example notification output:
```
======================================================================
HOCKEY SESSIONS AVAILABLE!
======================================================================

SPOTS OPENED UP! 1 previously sold-out session(s) now available!

--- NEWLY AVAILABLE (were sold out) ---

1. Scrimmage - Drop In Hockey
   When: Monday, November 4 - 8:00pm
   Site: IceHQ Melbourne
   URL: https://www.icehq.com.au/playhockey
```

### Stop the agent

Press `Ctrl+C` to stop the scheduler.

### Managing booked sessions

Once you book a session, add it to your booked list so the agent stops notifying you about it:

```bash
# List your booked sessions
python manage_booked.py list

# Add a booked session (copy date/time from notifications)
python manage_booked.py add "Monday, November 4 - 8:00pm"
python manage_booked.py add "Saturday, Nov 9 - 10:00am"

# Remove a session (if you cancel)
python manage_booked.py remove "Monday, November 4"
```

**Tips:**
- Copy the exact date/time string from the agent's notifications
- Use quotes around date/time strings with spaces
- Partial matches work (e.g., just the date for removal)
- Your booked sessions are stored in `booked_sessions.json`

## Project Structure

```
hockey-agent/
├── hockey_agent/
│   ├── __init__.py
│   ├── config.py              # Configuration and environment variables
│   ├── scraper.py             # Main scraping coordinator
│   ├── storage.py             # Session availability tracking
│   ├── booked.py              # Booked session tracking
│   ├── notifier.py            # Notification system
│   └── scrapers/
│       ├── __init__.py
│       └── icehq.py           # IceHQ-specific Selenium scraper
├── tests/
│   └── (test files)
├── main.py                    # Entry point with scheduler
├── manage_booked.py           # CLI tool to manage booked sessions
├── requirements.txt           # Python dependencies
├── .env                       # Your configuration (not in git)
├── .env.example               # Example configuration
└── README.md
```

## Notifications

### Console (default)
Prints new sessions to the terminal.

### Email
Uncomment `sendgrid` in `requirements.txt` and implement in `notifier.py`.

### Telegram
Uncomment `python-telegram-bot` in `requirements.txt` and implement in `notifier.py`.

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black .
ruff check .
```

## Tips

- **Testing**: Start with a short check interval (5-10 minutes) and `HEADLESS_BROWSER=false` to watch it work
- **Day filtering**: Use `MONITOR_DAYS` to only track days you can actually attend
- **Storage**: Check `seen_sessions.json` to see session status history
- **Reset**: Delete `seen_sessions.json` to reset tracking and see all current sessions as "new"
- **Spots opening**: Most spots open up 24-48 hours before the session when people cancel

## Troubleshooting

**No sessions found?**
- Set `HEADLESS_BROWSER=false` in `.env` to watch the browser and see what's happening
- Check that Chrome is installed (Selenium uses Chrome by default)
- Verify your day/date filters aren't too restrictive
- Look at the logs to see if dropdowns are being found

**Browser/WebDriver errors?**
- Make sure Chrome is installed and up to date
- webdriver-manager should auto-download ChromeDriver, but you can manually install if needed
- Try running with `HEADLESS_BROWSER=false` to see any browser errors

**Not getting notified about sold-out sessions becoming available?**
- This is the main feature! The agent tracks status changes
- The first run will record current status
- Subsequent runs will detect when "SOLD OUT" changes to available
- Make sure your check interval is frequent enough (15-30 min recommended)

**Getting too many notifications?**
- Adjust `MONITOR_DAYS` to only track days you want
- Adjust `MONITOR_SESSION_TYPES` to filter session types
- Increase `CHECK_INTERVAL_MINUTES` if checking too often
