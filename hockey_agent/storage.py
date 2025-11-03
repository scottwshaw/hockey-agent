"""Storage for tracking session availability status."""

import json
import os
from typing import Dict, Optional
from hockey_agent.config import STORAGE_FILE


def _load_sessions() -> Dict[str, Dict]:
    """Load session data from storage."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('sessions', {})
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_sessions(sessions: Dict[str, Dict]):
    """Save session data to storage."""
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump({'sessions': sessions}, f, indent=2)
    except IOError as e:
        print(f"Error saving sessions: {e}")


def get_session_status(session_id: str) -> Optional[str]:
    """
    Get the last known status of a session.

    Args:
        session_id: Unique identifier for the session

    Returns:
        Status string ('AVAILABLE', 'SOLD OUT') or None if not seen before
    """
    sessions = _load_sessions()
    session_data = sessions.get(session_id)
    return session_data.get('status') if session_data else None


def update_session_status(session_id: str, status: str, session_info: Dict):
    """
    Update the status of a session.

    Args:
        session_id: Unique identifier for the session
        status: Current status ('AVAILABLE', 'SOLD OUT')
        session_info: Additional info about the session
    """
    sessions = _load_sessions()
    sessions[session_id] = {
        'status': status,
        'info': session_info,
        'last_updated': session_info.get('timestamp', '')
    }
    _save_sessions(sessions)


def status_changed(session_id: str, new_status: str) -> bool:
    """
    Check if a session's status has changed.

    Args:
        session_id: Unique identifier for the session
        new_status: Current status to check against

    Returns:
        True if status has changed or session is new
    """
    old_status = get_session_status(session_id)

    # First time seeing this session
    if old_status is None:
        return True

    # Status changed
    if old_status != new_status:
        return True

    return False
