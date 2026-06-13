import sqlite3

conn = sqlite3.connect("finance_digest.db")
cursor = conn.cursor()

# Add gemini_category column
try:
    cursor.execute("""
    ALTER TABLE notifications
    ADD COLUMN gemini_category TEXT
    """)
    print("gemini_category column added")
except:
    print("gemini_category already exists")

# Add gemini_affects_finance column
try:
    cursor.execute("""
    ALTER TABLE notifications
    ADD COLUMN gemini_affects_finance INTEGER
    """)
    print("gemini_affects_finance column added")
except:
    print("gemini_affects_finance already exists")

conn.commit()
conn.close()

print("Done!")