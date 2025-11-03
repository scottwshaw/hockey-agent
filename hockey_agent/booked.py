"""Track sessions you've already booked."""

import json
import os
from typing import List, Set
from datetime import datetime
from hockey_agent.config import BOOKED_SESSIONS_FILE

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except:
    pass


def _load_booked_sessions() -> Set[str]:
    """Load the set of booked session identifiers from storage."""
    if os.path.exists(BOOKED_SESSIONS_FILE):
        try:
            with open(BOOKED_SESSIONS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('booked_sessions', []))
        except (json.JSONDecodeError, IOError) as e:
            if logger:
                logger.error(f"Error loading booked sessions: {e}")
            return set()
    return set()


def _save_booked_sessions(booked_sessions: Set[str]):
    """Save the set of booked session identifiers to storage."""
    try:
        with open(BOOKED_SESSIONS_FILE, 'w') as f:
            json.dump({
                'booked_sessions': sorted(list(booked_sessions)),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    except IOError as e:
        print(f"Error saving booked sessions: {e}")


def is_booked(date_time: str) -> bool:
    """
    Check if a session is already booked.

    Args:
        date_time: The date/time string from the session

    Returns:
        True if this session is already booked
    """
    booked_sessions = _load_booked_sessions()

    # Normalize the date_time string for matching
    normalized = date_time.lower().strip()

    # Check if any booked session matches
    for booked in booked_sessions:
        booked_lower = booked.lower().strip()

        # Try direct substring match first
        if booked_lower in normalized or normalized in booked_lower:
            return True

        # Try more flexible matching by extracting key date components
        # Extract numbers (day of month) from both strings
        import re

        # Get all numbers from both strings
        session_numbers = re.findall(r'\d+', normalized)
        booked_numbers = re.findall(r'\d+', booked_lower)

        # Get month names/abbreviations from both strings
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december',
                 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
                 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        session_month = None
        booked_month = None

        for month in months:
            if month in normalized:
                session_month = month[:3]  # Use 3-letter abbreviation
            if month in booked_lower:
                booked_month = month[:3]

        # Get day names from both strings
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

        session_day = None
        booked_day = None

        for day in days:
            if day in normalized:
                session_day = day[:3]  # Use 3-letter abbreviation
            if day in booked_lower:
                booked_day = day[:3]

        # If we have matching day of week, month, and day of month, it's a match
        if session_numbers and booked_numbers:
            # Check if day of month matches (first number is usually the day)
            if session_numbers[0] == booked_numbers[0]:  # Same day of month
                if session_month == booked_month:  # Same month
                    if session_day == booked_day or session_day is None or booked_day is None:
                        return True

    return False


def add_booked_session(date_time: str):
    """
    Add a session to your booked list.

    Args:
        date_time: The date/time string to mark as booked
    """
    booked_sessions = _load_booked_sessions()
    booked_sessions.add(date_time.strip())
    _save_booked_sessions(booked_sessions)
    if logger:
        logger.info(f"Added booked session: {date_time}")
    else:
        print(f"Added booked session: {date_time}")


def remove_booked_session(date_time: str):
    """
    Remove a session from your booked list.

    Args:
        date_time: The date/time string to remove
    """
    booked_sessions = _load_booked_sessions()
    # Try to remove exact match or partial match
    to_remove = set()
    normalized = date_time.lower().strip()

    for booked in booked_sessions:
        if booked.lower().strip() == normalized or normalized in booked.lower().strip():
            to_remove.add(booked)

    for item in to_remove:
        booked_sessions.discard(item)

    _save_booked_sessions(booked_sessions)
    if logger:
        logger.info(f"Removed booked session(s): {to_remove}")
    else:
        print(f"Removed booked session(s): {to_remove}")


def list_booked_sessions() -> List[str]:
    """
    Get a list of all booked sessions.

    Returns:
        Sorted list of booked session date/time strings
    """
    booked_sessions = _load_booked_sessions()
    return sorted(list(booked_sessions))


def clear_old_sessions():
    """
    Clear sessions that are in the past.

    Note: This is a placeholder. Actual implementation would need
    date parsing logic based on the format of your date strings.
    """
    # TODO: Implement if needed
    pass
