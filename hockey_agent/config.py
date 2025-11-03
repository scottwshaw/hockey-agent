"""Configuration for the hockey agent."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# How often to check websites (in minutes)
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '60'))

# Sites to monitor
SITES_TO_MONITOR = [
    {
        'name': 'IceHQ Melbourne',
        'url': 'https://www.icehq.com.au/playhockey',
        'type': 'icehq',  # Custom scraper type
    },
]

# Days of week to monitor (0=Monday, 6=Sunday)
# Example: [0, 2, 4] = Monday, Wednesday, Friday
MONITOR_DAYS = [int(d.strip()) for d in os.getenv('MONITOR_DAYS', '').split(',') if d.strip()]

# Specific dates to monitor (format: YYYY-MM-DD)
# Example: 2025-11-15,2025-11-20
MONITOR_DATES = [d.strip() for d in os.getenv('MONITOR_DATES', '').split(',') if d.strip()]

# Session types to monitor
MONITOR_SESSION_TYPES = [s.strip().lower() for s in os.getenv('MONITOR_SESSION_TYPES', 'stick & puck,scrimmage').split(',') if s.strip()]

# Browser settings for Selenium
HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true'
BROWSER_WAIT_TIME = int(os.getenv('BROWSER_WAIT_TIME', '10'))  # seconds

# Notification settings
NOTIFICATION_METHOD = os.getenv('NOTIFICATION_METHOD', 'console')  # console, email, telegram, sms
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Twilio SMS settings
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')  # Main auth token (legacy)
TWILIO_API_KEY = os.getenv('TWILIO_API_KEY', '')  # API Key SID (recommended)
TWILIO_API_SECRET = os.getenv('TWILIO_API_SECRET', '')  # API Key Secret (recommended)
TWILIO_FROM_PHONE = os.getenv('TWILIO_FROM_PHONE', '')  # Your Twilio phone number (e.g., +1234567890)
TWILIO_TO_PHONE = os.getenv('TWILIO_TO_PHONE', '')  # Your personal phone number

# Storage
STORAGE_FILE = os.getenv('STORAGE_FILE', 'seen_sessions.json')
BOOKED_SESSIONS_FILE = os.getenv('BOOKED_SESSIONS_FILE', 'booked_sessions.json')
