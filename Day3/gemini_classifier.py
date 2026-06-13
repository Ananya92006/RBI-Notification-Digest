import sqlite3
import google.generativeai as genai
import json
import time

# Gemini API Key
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# Connect Database
conn = sqlite3.connect("finance_digest.db")
cursor = conn.cursor()

# Read all notifications
cursor.execute("""
SELECT id, title
FROM notifications
""")

rows = cursor.fetchall()

print(f"Found {len(rows)} notifications\n")

for notification_id, title in rows:

    prompt = f"""
Classify this RBI notification.

Possible categories:
- Interest Rates
- Foreign Exchange
- Markets
- Banking Regulations
- Savings Schemes
- Insurance
- Taxes
- Other

Also determine whether it affects a common person's personal finance.

Return ONLY JSON.

Example:

{{
  "category": "Foreign Exchange",
  "affects_finance": 1
}}

Notification:
{title}
"""

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

        text = text.replace("```json", "")
        text = text.replace("```", "")

        result = json.loads(text)

        gemini_category = result["category"]
        gemini_affects = result["affects_finance"]

        cursor.execute("""
        UPDATE notifications
        SET gemini_category=?,
            gemini_affects_finance=?
        WHERE id=?
        """,
        (
            gemini_category,
            gemini_affects,
            notification_id
        ))

        conn.commit()

        print(f"✓ {title}")
        print(f"  Category: {gemini_category}")
        print()

        time.sleep(1)

    except Exception as e:

        print(f"✗ Failed: {title}")
        print(e)
        print()

conn.close()

print("Gemini Classification Complete!")