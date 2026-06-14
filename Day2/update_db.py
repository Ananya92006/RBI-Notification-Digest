import sqlite3

conn = sqlite3.connect("finance_digest.db")
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
            f"ALTER TABLE notifications ADD COLUMN {column_name} {column_type}"
        )
        print(f"{column_name} added")

    except Exception:
        print(f"{column_name} already exists")

conn.commit()
conn.close()

print("\nDatabase Updated Successfully!")