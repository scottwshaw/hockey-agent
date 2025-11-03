"""Notification system for new hockey sessions."""

import logging
from typing import List, Dict
from hockey_agent.config import (
    NOTIFICATION_METHOD,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_API_KEY,
    TWILIO_API_SECRET,
    TWILIO_FROM_PHONE,
    TWILIO_TO_PHONE
)

logger = logging.getLogger(__name__)


def send_notification(sessions: List[Dict[str, str]], newly_available_count: int = 0):
    """
    Send notification about new hockey sessions.

    Args:
        sessions: List of session dictionaries
        newly_available_count: Number of sessions that were sold out but now have spots
    """
    if NOTIFICATION_METHOD == 'console':
        send_console_notification(sessions, newly_available_count)
    elif NOTIFICATION_METHOD == 'email':
        send_email_notification(sessions, newly_available_count)
    elif NOTIFICATION_METHOD == 'telegram':
        send_telegram_notification(sessions, newly_available_count)
    elif NOTIFICATION_METHOD == 'sms':
        send_sms_notification(sessions, newly_available_count)
    else:
        logger.warning(f"Unknown notification method: {NOTIFICATION_METHOD}")


def send_console_notification(sessions: List[Dict[str, str]], newly_available_count: int = 0):
    """Print notification to console."""
    print("\n" + "=" * 70)
    print("HOCKEY SESSIONS AVAILABLE!")
    print("=" * 70)

    if newly_available_count > 0:
        print(f"\nSPOTS OPENED UP! {newly_available_count} previously sold-out session(s) now available!")

    newly_available = sessions[:newly_available_count]
    new_sessions = sessions[newly_available_count:]

    if newly_available:
        print("\n--- NEWLY AVAILABLE (were sold out) ---")
        for i, session in enumerate(newly_available, 1):
            print(f"\n{i}. {session.get('session_type', 'Unknown Type')}")
            print(f"   When: {session.get('date_time', 'Unknown')}")
            print(f"   Site: {session.get('site', 'Unknown')}")
            print(f"   URL: {session.get('url', '')}")

    if new_sessions:
        print("\n--- NEW SESSIONS ---")
        for i, session in enumerate(new_sessions, 1):
            print(f"\n{i}. {session.get('session_type', 'Unknown Type')}")
            print(f"   When: {session.get('date_time', 'Unknown')}")
            print(f"   Site: {session.get('site', 'Unknown')}")
            print(f"   URL: {session.get('url', '')}")

    print("\n" + "=" * 70 + "\n")


def send_email_notification(sessions: List[Dict[str, str]], newly_available_count: int = 0):
    """Send email notification (requires email service setup)."""
    # TODO: Implement email notification
    # You can use SendGrid, Gmail SMTP, etc.
    logger.warning("Email notification not yet implemented")
    send_console_notification(sessions, newly_available_count)  # Fallback to console


def send_telegram_notification(sessions: List[Dict[str, str]], newly_available_count: int = 0):
    """Send Telegram notification (requires bot setup)."""
    # TODO: Implement Telegram notification
    # from telegram import Bot
    # bot = Bot(token=TELEGRAM_BOT_TOKEN)
    # message = format_message(sessions)
    # bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    logger.warning("Telegram notification not yet implemented")
    send_console_notification(sessions, newly_available_count)  # Fallback to console


def send_sms_notification(sessions: List[Dict[str, str]], newly_available_count: int = 0):
    """Send SMS notification via Twilio."""
    try:
        from twilio.rest import Client

        # Validate Twilio credentials - support both API Keys and Auth Token
        if not TWILIO_ACCOUNT_SID or not TWILIO_FROM_PHONE or not TWILIO_TO_PHONE:
            logger.error("Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_FROM_PHONE, and TWILIO_TO_PHONE in .env")
            send_console_notification(sessions, newly_available_count)  # Fallback
            return

        # Create Twilio client - prefer API Key if available, fallback to Auth Token
        if TWILIO_API_KEY and TWILIO_API_SECRET:
            # Using API Key (recommended)
            client = Client(TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_ACCOUNT_SID)
            logger.info("Using Twilio API Key for authentication")
        elif TWILIO_AUTH_TOKEN:
            # Using Auth Token (legacy)
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            logger.info("Using Twilio Auth Token for authentication")
        else:
            logger.error("No Twilio authentication credentials found. Please set either TWILIO_API_KEY+TWILIO_API_SECRET or TWILIO_AUTH_TOKEN in .env")
            send_console_notification(sessions, newly_available_count)  # Fallback
            return

        # Build message text
        newly_available = sessions[:newly_available_count]
        new_sessions = sessions[newly_available_count:]

        message_parts = ["🏒 Hockey Sessions Available!"]

        if newly_available:
            message_parts.append(f"\n🔥 {len(newly_available)} SPOTS OPENED UP:")
            for session in newly_available:
                message_parts.append(f"• {session.get('session_type')}")
                message_parts.append(f"  {session.get('date_time')}")

        if new_sessions:
            message_parts.append(f"\n✨ {len(new_sessions)} NEW SESSION(S):")
            for session in new_sessions:
                message_parts.append(f"• {session.get('session_type')}")
                message_parts.append(f"  {session.get('date_time')}")

        message_parts.append(f"\n🔗 {sessions[0].get('url', '')}")

        message_text = "\n".join(message_parts)

        # Send SMS
        message = client.messages.create(
            body=message_text,
            from_=TWILIO_FROM_PHONE,
            to=TWILIO_TO_PHONE
        )

        logger.info(f"SMS sent successfully! Message SID: {message.sid}")
        print(f"✅ SMS notification sent to {TWILIO_TO_PHONE}")

        # Also print to console for debugging
        send_console_notification(sessions, newly_available_count)

    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        print(f"❌ Failed to send SMS: {e}")
        send_console_notification(sessions, newly_available_count)  # Fallback
