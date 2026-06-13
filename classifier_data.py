import sqlite3
from Day3.classifier import classify_notification

conn = sqlite3.connect("finance_digest.db")
cursor = conn.cursor()

cursor.execute("""
SELECT id, title, main_text
FROM notifications
""")

rows = cursor.fetchall()

for row in rows:
    id_, title, main_text = row

    text = f"{title} {main_text}"

    affects_finance, category = classify_notification(text)

    cursor.execute("""
    UPDATE notifications
    SET category = ?,
        affects_finance = ?
    WHERE id = ?
    """, (category, affects_finance, id_))

conn.commit()
conn.close()

print("Classification completed!")