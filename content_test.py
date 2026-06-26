
import sqlite3

conn = sqlite3.connect("finance_digest.db")
cursor = conn.cursor()

cursor.execute("""
SELECT date, COUNT(*)
FROM notifications
GROUP BY date
ORDER BY date
""")

for row in cursor.fetchall():
    print(row)

conn.close()
