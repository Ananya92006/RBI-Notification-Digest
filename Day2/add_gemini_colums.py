import sqlite3


def add_gemini_columns(db_path="finance_digest.db"):
    """Add gemini_category and gemini_affects_finance columns."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add gemini_category column
    try:
        cursor.execute("""
        ALTER TABLE notifications
        ADD COLUMN gemini_category TEXT
        """)
        print("gemini_category column added")
    except Exception:
        print("gemini_category already exists")

    # Add gemini_affects_finance column
    try:
        cursor.execute("""
        ALTER TABLE notifications
        ADD COLUMN gemini_affects_finance INTEGER
        """)
        print("gemini_affects_finance column added")
    except Exception:
        print("gemini_affects_finance already exists")

    conn.commit()
    conn.close()

    print("Done!")


if __name__ == "__main__":
    add_gemini_columns()