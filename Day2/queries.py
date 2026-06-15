import sqlite3

conn = sqlite3.connect("finance_digest.db")
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
ORDER BY id DESC
LIMIT 5;
""")

for row in cursor.fetchall():
    print(row)

print("\nQuery 4: Classification Results\n")

cursor.execute("""
SELECT title, category, affects_finance
FROM notifications
LIMIT 10;
""")
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


