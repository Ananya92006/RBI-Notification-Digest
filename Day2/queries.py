import sqlite3


def run_queries(db_path="finance_digest.db"):
    """Run sample queries against the notifications database."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\nQuery 1: Count notifications by date\n")

    cursor.execute("""
    SELECT date, COUNT(*)
    FROM notifications
    GROUP BY date
    ORDER BY date;
    """)

    for row in cursor.fetchall():
        print(row)


    print("\nQuery 2: Foreign Exchange Notifications\n")

    cursor.execute("""
    SELECT date, title
    FROM notifications
    WHERE title LIKE '%Foreign Exchange%';
    """)

    for row in cursor.fetchall():
        print(row)

    print("\nQuery 3: Latest Notifications\n")

    cursor.execute("""
    SELECT date, title
    FROM notifications
    ORDER BY date DESC
    LIMIT 5;
    """)

    for row in cursor.fetchall():
        print(row)

    print("\nQuery 4: Unclassified Count\n")

    cursor.execute("""
    SELECT COUNT(*)
    FROM notifications
    WHERE impact_level IS NULL
       OR target_audience IS NULL
       OR gemini_summary IS NULL;
    """)

    for row in cursor.fetchall():
        print(row)

    conn.close()


if __name__ == "__main__":
    run_queries()
