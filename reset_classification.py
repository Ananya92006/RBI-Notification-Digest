import sqlite3

conn = sqlite3.connect("finance_digest.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE notifications
SET gemini_category = NULL,
    gemini_affects_finance = NULL,
    gemini_summary = NULL,
    gemini_reason = NULL,
    impact_level = NULL,
    target_audience = NULL;
""")

conn.commit()

print("All classifications reset successfully.")

conn.close()