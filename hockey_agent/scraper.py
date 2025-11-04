"""Web scraper for hockey rink websites."""

import logging
from datetime import datetime
from typing import List, Dict
from hockey_agent.config import SITES_TO_MONITOR
from hockey_agent.storage import get_session_status, update_session_status, status_changed
from hockey_agent.notifier import send_notification
from hockey_agent.scrapers.icehq_playwright import scrape_icehq
from hockey_agent.booked import is_booked

logger = logging.getLogger(__name__)


def scrape_site(site: Dict) -> List[Dict[str, str]]:
    """
    Scrape a single site for hockey sessions using the appropriate scraper.

    Args:
        site: Site configuration dictionary with 'url', 'name', 'type' keys

    Returns:
        List of session dictionaries
    """
    url = site['url']
    name = site['name']
    site_type = site.get('type', 'generic')

    if site_type == 'icehq':
        return scrape_icehq(url, name)
    else:
        logger.warning(f"Unknown site type '{site_type}' for {name}")
        return []


def check_all_sites():
    """Check all configured sites for new or newly available hockey sessions."""
    logger.info("=" * 50)
    logger.info("Starting check for hockey sessions...")

    newly_available_sessions = []
    new_sessions = []
    all_sessions = []  # Track all sessions for display

    for site in SITES_TO_MONITOR:
        sessions = scrape_site(site)

        # Check each session for status changes
        for session in sessions:
            # Mark if already booked
            session['is_booked'] = is_booked(session['date_time'])

            # Add to all sessions list for display
            all_sessions.append(session)

            # Skip notifications if already booked
            if session['is_booked']:
                logger.debug(f"Already booked: {session['date_time']}")
                continue

            # Create unique ID for this session
            session_id = f"{session['site']}:{session['session_type']}:{session['date_time']}"

            # Add timestamp
            session['timestamp'] = datetime.now().isoformat()

            current_status = session['status']
            previous_status = get_session_status(session_id)

            # Check if this is a status change we care about
            if status_changed(session_id, current_status):
                if previous_status is None:
                    # New session
                    if current_status == 'AVAILABLE':
                        new_sessions.append(session)
                        logger.info(f"NEW AVAILABLE: {session['session_type']} - {session['date_time']}")
                elif previous_status == 'SOLD OUT' and current_status == 'AVAILABLE':
                    # Previously sold out, now available!
                    newly_available_sessions.append(session)
                    logger.info(f"SPOT OPENED: {session['session_type']} - {session['date_time']}")

            # Update storage with current status
            update_session_status(session_id, current_status, session)

    # Display all sessions
    if all_sessions:
        print("\n" + "=" * 70)
        print("ALL MATCHING SESSIONS")
        print("=" * 70)
        for session in all_sessions:
            status_label = session['status']
            if session['is_booked']:
                status_label += " (BOOKED)"

            qty = session.get('qty_in_stock', '?')
            print(f"\n{session['session_type']}")
            print(f"  When: {session['date_time']}")
            print(f"  Status: {status_label} ({qty} spots)")
        print("=" * 70 + "\n")

    # Send notifications
    all_notifiable_sessions = newly_available_sessions + new_sessions

    if newly_available_sessions:
        logger.info(f"Found {len(newly_available_sessions)} newly available session(s) (were sold out)")

    if new_sessions:
        logger.info(f"Found {len(new_sessions)} new available session(s)")

    if all_notifiable_sessions:
        send_notification(all_notifiable_sessions, newly_available_count=len(newly_available_sessions))
    else:
        logger.info("No new or newly available sessions found.")

    logger.info("Check complete.")
    logger.info("=" * 50)
