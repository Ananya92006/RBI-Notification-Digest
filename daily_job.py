"""
Daily Job — Scrape, Classify, and Cleanup

This script performs the complete daily pipeline:
1. Scrapes new RBI notifications
2. Runs rule-based classification on all notifications
3. Runs Gemini AI classification (only unclassified ones)
4. Deletes notifications older than 30 days

Usage:
    python daily_job.py

Can be called directly or imported by scheduler.py
"""

import sys
import os
from datetime import datetime

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_daily_job():
    """Execute the complete daily pipeline."""

    print("=" * 60)
    print(f"  DAILY JOB — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # -----------------------------------------
    # Step 1: Scrape new notifications
    # -----------------------------------------
    print("\n[1/4] Scraping RBI notifications...\n")

    try:
        from Day1.scrapper import scrape_notifications
        notifications = scrape_notifications()
        print(f"\n✓ Scraped {len(notifications)} notifications")
    except Exception as e:
        print(f"✗ Scraping failed: {e}")

    # -----------------------------------------
    # Step 2: Rule-based classification
    # -----------------------------------------
    print("\n[2/4] Running rule-based classification...\n")

    try:
        from Day3.classifier import run_classification
        run_classification()
        print("✓ Rule-based classification complete")
    except Exception as e:
        print(f"✗ Rule-based classification failed: {e}")

    # -----------------------------------------
    # Step 3: Gemini AI classification
    #         (only unclassified notifications)
    # -----------------------------------------
    print("\n[3/4] Running Gemini AI classification...\n")

    try:
        from Day3.gemini_classifier import classify_unclassified
        count = classify_unclassified()
        print(f"✓ Gemini classified {count} notifications")
    except ValueError as e:
        print(f"⚠ Gemini skipped: {e}")
    except Exception as e:
        print(f"✗ Gemini classification failed: {e}")

    # -----------------------------------------
    # Step 4: Cleanup old notifications (>30 days)
    # -----------------------------------------
    print("\n[4/4] Cleaning up old notifications...\n")

    try:
        from Day1.scrapper import cleanup_old_notifications
        deleted = cleanup_old_notifications(days=30)
        print(f"✓ Deleted {deleted} notifications older than 30 days")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")

    # -----------------------------------------
    # Done
    # -----------------------------------------
    print("\n" + "=" * 60)
    print(f"  DAILY JOB COMPLETE — {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    run_daily_job()
