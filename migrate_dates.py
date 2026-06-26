"""
One-time migration script to convert dates from string format
(e.g., "Jun 10, 2026") to ISO format ("2026-06-10") for proper
chronological sorting.

Safe to run multiple times — skips already-converted dates.

Usage:
    python migrate_dates.py
"""

import sqlite3
from datetime import datetime


def migrate_dates(db_path="finance_digest.db"):
    """Convert all dates from string format to ISO format."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, date FROM notifications")
    rows = cursor.fetchall()

    converted = 0
    skipped = 0

    for row_id, date_str in rows:

        if not date_str:
            skipped += 1
            continue

        # Skip if already in ISO format (YYYY-MM-DD)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            skipped += 1
            continue
        except ValueError:
            pass

        # Convert from "Jun 10, 2026" to "2026-06-10"
        try:
            parsed = datetime.strptime(date_str, "%b %d, %Y")
            iso_date = parsed.strftime("%Y-%m-%d")

            cursor.execute(
                "UPDATE notifications SET date = ? WHERE id = ?",
                (iso_date, row_id)
            )

            converted += 1

        except ValueError:
            print(
                f"Could not parse date: '{date_str}' "
                f"(id={row_id})"
            )
            skipped += 1

    conn.commit()
    conn.close()

    print(f"\nDate Migration Complete!")
    print(f"  Converted: {converted}")
    print(f"  Skipped:   {skipped}")


if __name__ == "__main__":
    migrate_dates()
