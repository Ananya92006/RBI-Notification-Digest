"""
Scheduler — Runs daily_job.py automatically at midnight every day.

No external dependencies needed — uses only Python standard library.

How it works:
    - Calculates seconds until next midnight
    - Sleeps until midnight
    - Runs the daily job (scrape → classify → cleanup)
    - Repeats forever

Usage:
    python scheduler.py

To run in the background (Linux/Mac):
    nohup python scheduler.py > scheduler.log 2>&1 &

To run in the background (Windows):
    pythonw scheduler.py
    OR
    start /b python scheduler.py > scheduler.log 2>&1
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# -----------------------------------------
# Logging Setup
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def seconds_until_midnight():
    """Calculate seconds remaining until next midnight."""

    now = datetime.now()

    next_midnight = (
        now + timedelta(days=1)
    ).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    return (next_midnight - now).total_seconds()


def run_scheduler():
    """Run the daily job at midnight every day."""

    logger.info("=" * 60)
    logger.info("  RBI Notification Scheduler Started")
    logger.info("=" * 60)

    while True:

        wait_time = seconds_until_midnight()

        hours = int(wait_time // 3600)
        minutes = int((wait_time % 3600) // 60)

        logger.info(
            f"Next run at midnight "
            f"(in {hours}h {minutes}m)"
        )

        # Sleep until midnight
        time.sleep(wait_time)

        # Run the daily job
        logger.info("Midnight reached — starting daily job")

        try:
            from daily_job import run_daily_job
            run_daily_job()
            logger.info("Daily job completed successfully")

        except Exception as e:
            logger.error(f"Daily job failed: {e}")

        # Small delay to avoid running twice at midnight
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
