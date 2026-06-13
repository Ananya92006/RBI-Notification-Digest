import sqlite3

conn = sqlite3.connect("finance_digest.db")
cursor = conn.cursor()

cursor.execute("""
SELECT date, title, category, affects_finance, link
FROM notifications
ORDER BY id DESC
""")

rows = cursor.fetchall()

with open("finance_digest.txt", "w", encoding="utf-8") as f:

    f.write("PERSONAL FINANCE NOTIFICATION DIGEST\n")
    f.write("=" * 50 + "\n\n")

    for row in rows:
        date, title, category, affects_finance, link = row

        affects = "Yes" if affects_finance else "No"

        f.write(f"Date: {date}\n")
        f.write(f"Category: {category}\n")
        f.write(f"Affects Personal Finance: {affects}\n\n")

        f.write(f"Title: {title}\n\n")

        f.write(f"Link: {link}\n")

        f.write("-" * 50 + "\n\n")

conn.close()

print("Digest generated successfully!")