import sqlite3


def update_database(db_path="finance_digest.db"):
    """Add summary, reason, impact, and audience columns."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns = [
        ("gemini_summary", "TEXT"),
        ("gemini_reason", "TEXT"),
        ("impact_level", "TEXT"),
        ("target_audience", "TEXT")
    ]

    for column_name, column_type in columns:

        try:
            cursor.execute(
                f"ALTER TABLE notifications ADD COLUMN "
                f"{column_name} {column_type}"
            )
            print(f"{column_name} added")

        except Exception:
            print(f"{column_name} already exists")

    conn.commit()
    conn.close()

    print("\nDatabase Updated Successfully!")


if __name__ == "__main__":
    update_database()