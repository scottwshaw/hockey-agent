#!/usr/bin/env python3
"""
Test SMS notification without running the full scraper.
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hockey_agent.notifier import send_sms_notification

def main():
    """Send a test SMS notification."""
    print("Sending test SMS notification...")

    # Create fake session data
    test_sessions = [
        {
            'session_type': 'Stick & Puck',
            'date_time': 'Saturday 9th November 10:00am-11:00am',
            'status': 'AVAILABLE',
            'site': 'IceHQ Melbourne',
            'url': 'https://www.icehq.com.au/playhockey',
            'qty_in_stock': 5
        }
    ]

    # Send as "newly available" (spot opened up)
    send_sms_notification(test_sessions, newly_available_count=1)

    print("\nDone! Check your phone for the SMS.")

if __name__ == "__main__":
    main()
