import sqlite3
import google.generativeai as genai
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )

# Configure Gemini
genai.configure(api_key=api_key)

# Load Model
model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# Connect Database
conn = sqlite3.connect("finance_digest.db")
cursor = conn.cursor()

# ONLY unclassified notifications
cursor.execute("""
SELECT id, title
FROM notifications
WHERE gemini_category IS NULL
""")

rows = cursor.fetchall()

print(f"\nFound {len(rows)} unclassified notifications\n")

for notification_id, title in rows:

    prompt = f"""
You are an expert RBI financial analyst.

Choose ONLY ONE category from:

- Interest Rates
- Foreign Exchange
- Markets
- Banking Regulations
- Savings Schemes
- Insurance
- Taxes
- Other

Classification Rules:

- Repo Rate, Reverse Repo, CRR, SLR -> Interest Rates
- FEMA, FCNR, ECB, Foreign Currency -> Foreign Exchange
- FPI, Government Securities, Bonds, Derivatives -> Markets
- Capital Adequacy, Prudential Norms, Governance -> Banking Regulations
- Currency withdrawal, banknotes, depositor schemes -> Savings Schemes

Determine:

1. category
2. affects_finance (0 or 1)
3. impact_level (High, Medium, Low)
4. target_audience
5. summary
6. reason

Return ONLY valid JSON.

Example:

{{
    "category": "Foreign Exchange",
    "affects_finance": 1,
    "impact_level": "Medium",
    "target_audience": "NRI Depositors",
    "summary": "Introduces a swap facility for FCNR deposits.",
    "reason": "Impacts foreign currency deposits held by NRIs."
}}

Notification:
{title}
"""

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

        # Remove markdown formatting
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        result = json.loads(text)

        gemini_category = result.get("category", "Other")
        gemini_affects = result.get("affects_finance", 0)
        gemini_summary = result.get("summary", "")
        impact_level = result.get("impact_level", "Low")
        target_audience = result.get("target_audience", "")
        gemini_reason = result.get("reason", "")

        cursor.execute("""
        UPDATE notifications
        SET gemini_category=?,
            gemini_affects_finance=?,
            gemini_summary=?,
            gemini_reason=?,
            impact_level=?,
            target_audience=?
        WHERE id=?
        """,
        (
            gemini_category,
            gemini_affects,
            gemini_summary,
            gemini_reason,
            impact_level,
            target_audience,
            notification_id
        ))

        conn.commit()

        print(f"✓ {title}")
        print(f"  Category: {gemini_category}")
        print(f"  Affects Finance: {gemini_affects}")
        print(f"  Impact Level: {impact_level}")
        print(f"  Target Audience: {target_audience}")
        print(f"  Summary: {gemini_summary}")
        print(f"  Reason: {gemini_reason}")
        print()

        # Prevent hitting limits too quickly
        time.sleep(2)

    except Exception as e:

        print(f"\n✗ Failed: {title}")
        print(e)

        # Stop if Gemini quota exceeded
        if "429" in str(e):
            print("\nQuota exceeded. Stopping classifier.")
            break

        print()

conn.close()

print("\nGemini Classification Complete!")