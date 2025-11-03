#!/usr/bin/env python3
"""
Test script to run the scraper once interactively.

Use this to test your configuration and see what sessions are found
without starting the scheduler.
"""

import logging
import sys
from hockey_agent.scraper import check_all_sites

# Set up detailed logging for testing
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Run a single check of all sites."""
    print("\n" + "=" * 70)
    print("HOCKEY AGENT - TEST MODE")
    print("=" * 70)
    print("\nRunning a single check of all configured sites...")
    print("This will show you what sessions are found with your current filters.\n")

    try:
        check_all_sites()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        print("Check the logs above for details.")
        return 1

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nTips:")
    print("- Check seen_sessions.json to see what status was recorded")
    print("- Check booked_sessions.json to see your booked sessions")
    print("- Run again to test if status changes are detected")
    print("- When ready, use 'python main.py' to start the scheduler\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
