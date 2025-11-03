#!/usr/bin/env python3
"""CLI tool to manage your booked hockey sessions."""

import sys
from hockey_agent.booked import (
    add_booked_session,
    remove_booked_session,
    list_booked_sessions
)


def print_help():
    """Print usage information."""
    print("""
Hockey Agent - Manage Booked Sessions

Usage:
    python manage_booked.py list              - List all booked sessions
    python manage_booked.py add <date_time>   - Add a booked session
    python manage_booked.py remove <date_time> - Remove a booked session

Examples:
    # List all booked sessions
    python manage_booked.py list

    # Add a booked session (copy the date/time string from notifications)
    python manage_booked.py add "Monday, November 4 - 8:00pm"
    python manage_booked.py add "Saturday, Nov 9 - 10:00am"

    # Remove a booked session (can use partial match)
    python manage_booked.py remove "Monday, November 4"
    python manage_booked.py remove "Nov 9"

Tips:
    - Use quotes around date/time strings with spaces
    - Copy the exact date/time format from the agent's notifications
    - Partial matches work for removal (e.g., just the date)
""")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == 'list':
        booked = list_booked_sessions()
        if booked:
            print(f"\nYou have {len(booked)} booked session(s):\n")
            for i, session in enumerate(booked, 1):
                print(f"{i}. {session}")
            print()
        else:
            print("\nNo booked sessions tracked yet.\n")

    elif command == 'add':
        if len(sys.argv) < 3:
            print("Error: Please provide a date/time string to add.")
            print('Example: python manage_booked.py add "Monday, November 4 - 8:00pm"')
            return

        date_time = ' '.join(sys.argv[2:])
        add_booked_session(date_time)
        print(f"\nAdded: {date_time}\n")

    elif command == 'remove':
        if len(sys.argv) < 3:
            print("Error: Please provide a date/time string to remove.")
            print('Example: python manage_booked.py remove "Monday, November 4"')
            return

        date_time = ' '.join(sys.argv[2:])
        remove_booked_session(date_time)
        print(f"\nRemoved session(s) matching: {date_time}\n")

    elif command in ['help', '-h', '--help']:
        print_help()

    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == '__main__':
    main()
