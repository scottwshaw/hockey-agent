"""Main entry point for the hockey agent."""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from hockey_agent.scraper import check_all_sites
from hockey_agent.config import CHECK_INTERVAL_MINUTES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Also enable APScheduler logging
logging.getLogger('apscheduler').setLevel(logging.INFO)


def job_listener(event):
    """Log when scheduled jobs run."""
    if event.exception:
        logger.error(f"Job failed with exception: {event.exception}")
    else:
        logger.info(f"Scheduled check completed successfully")


def main():
    """Run the hockey agent scheduler."""
    logger.info("Starting Hockey Agent...")

    # Run once immediately on startup
    logger.info("Running initial check...")
    check_all_sites()

    # Set up scheduler for periodic checks
    scheduler = BlockingScheduler()

    # Add listener to log when jobs execute
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.add_job(
        check_all_sites,
        'interval',
        minutes=CHECK_INTERVAL_MINUTES,
        id='check_hockey_sites'
    )

    logger.info(f"Scheduler started. Checking every {CHECK_INTERVAL_MINUTES} minutes.")
    logger.info("Press Ctrl+C to exit.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down Hockey Agent...")


if __name__ == "__main__":
    main()
