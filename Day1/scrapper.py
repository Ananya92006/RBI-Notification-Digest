import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
import sqlite3


def setup_database(db_path="finance_digest.db"):
    """Create the notifications table if it doesn't exist."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        source TEXT,
        title TEXT,
        link TEXT UNIQUE,
        main_text TEXT,
        category TEXT,
        affects_finance INTEGER
    )
    """)

    conn.commit()
    return conn, cursor


def scrape_notifications(db_path="finance_digest.db"):
    """Scrape RBI notifications and save to database.
    Returns the number of new notifications saved."""

    conn, cursor = setup_database(db_path)

    # -----------------------------
    # RBI Notifications Page
    # -----------------------------
    url = "https://rbi.org.in/Scripts/NotificationUser.aspx"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find_all("table")[0]

    rows = table.find_all("tr")

    notifications = []

    current_date = None

    date_pattern = r"^[A-Z][a-z]{2}\s\d{2},\s\d{4}$"

    # -----------------------------
    # Extract Notifications
    # -----------------------------
    for row in rows:

        text = row.get_text(" ", strip=True)

        if re.match(date_pattern, text):
            # Convert "Jun 10, 2026" to ISO "2026-06-10"
            try:
                parsed = datetime.strptime(text, "%b %d, %Y")
                current_date = parsed.strftime("%Y-%m-%d")
            except ValueError:
                current_date = text

        else:
            links = row.find_all("a")

            for link in links:

                title = link.get_text(strip=True)

                if not title:
                    continue

                full_url = (
                    "https://rbi.org.in/Scripts/"
                    + link.get("href")
                )

                print(f"Scraping: {title[:60]}...")

                try:
                    notification_response = requests.get(
                        full_url,
                        headers=headers,
                        timeout=10
                    )

                    notification_soup = BeautifulSoup(
                        notification_response.text,
                        "html.parser"
                    )

                    tables = notification_soup.find_all("table")

                    if tables:
                        largest_table = max(
                            tables,
                            key=lambda t: len(
                                t.get_text(" ", strip=True)
                            )
                        )

                        main_text = largest_table.get_text(
                            "\n",
                            strip=True
                        )
                    else:
                        main_text = ""

                except Exception as e:
                    print("Error:", e)
                    main_text = ""

                notification = {
                    "date": current_date,
                    "source": "RBI",
                    "title": title,
                    "link": full_url,
                    "main_text": main_text
                }

                notifications.append(notification)

                # Save to database
                cursor.execute("""
                INSERT OR IGNORE INTO notifications
                (date, source, title, link, main_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    notification["date"],
                    notification["source"],
                    notification["title"],
                    notification["link"],
                    notification["main_text"]
                ))

                conn.commit()

                # Respect RBI server
                time.sleep(1)

    conn.close()

    return notifications


def cleanup_old_notifications(days=30, db_path="finance_digest.db"):
    """Delete notifications older than the specified days.
    Returns the number of deleted records."""

    cutoff_date = (
        datetime.now() - timedelta(days=days)
    ).strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM notifications WHERE date < ?",
        (cutoff_date,)
    )
    count = cursor.fetchone()[0]

    cursor.execute(
        "DELETE FROM notifications WHERE date < ?",
        (cutoff_date,)
    )

    conn.commit()
    conn.close()

    return count


if __name__ == "__main__":

    notifications = scrape_notifications()

    # -----------------------------
    # Final Output
    # -----------------------------
    print("\n" + "=" * 80)
    print("TOTAL NOTIFICATIONS")
    print("=" * 80)

    print(len(notifications))

    if notifications:
        print("\n" + "=" * 80)
        print("FIRST NOTIFICATION")
        print("=" * 80)

        print("Date:", notifications[0]["date"])
        print("Source:", notifications[0]["source"])
        print("Title:", notifications[0]["title"])
        print("Link:", notifications[0]["link"])

        print("\nMain Text Preview:\n")
        print(notifications[0]["main_text"][:1000])

        print("\nAll Dates:")

        dates = sorted(set(
            [item["date"] for item in notifications]
        ))

        for d in dates:
            print(d)

    print("\nSaved to Database Successfully!")