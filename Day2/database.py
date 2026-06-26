import sqlite3


def create_database(db_path="finance_digest.db"):
    """Create the notifications table with all columns."""

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

        -- Rule Based Classification
        category TEXT,
        affects_finance INTEGER,

        -- Gemini Classification
        gemini_category TEXT,
        gemini_affects_finance INTEGER
    )
    """)

    conn.commit()
    conn.close()

    print("Database Created Successfully")


if __name__ == "__main__":
    create_database()