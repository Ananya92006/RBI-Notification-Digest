import sqlite3
from google import genai 
import json
import time
import os
from dotenv import load_dotenv


def classify_unclassified(db_path="finance_digest.db"):
    """Classify all unclassified notifications using Gemini AI.
    Only processes notifications that haven't been classified yet.
    Returns the number of successfully classified notifications."""

    # Load environment variables
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in .env file"
        )

    # Configure Gemini Client
    client = genai.Client(api_key=api_key)

    # Connect Database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Only unclassified notifications
    cursor.execute("""
    SELECT id, title, main_text
    FROM notifications
    WHERE gemini_category IS NULL
       OR gemini_summary IS NULL
       OR impact_level IS NULL
       OR target_audience IS NULL
    """)

    rows = cursor.fetchall()

    print(f"\nFound {len(rows)} unclassified notifications\n")

    classified_count = 0

    for notification_id, title, main_text in rows:

        prompt = f"""
You are an expert RBI financial analyst.

Analyze the RBI notification and determine its category, impact, audience, and relevance to ordinary citizens.

Choose the SINGLE most appropriate category from:

- Interest Rates
- Foreign Exchange
- Markets
- Banking Regulations
- Savings Schemes
- Insurance
- Taxes
- Other

Category Guidance (examples only, not strict rules):

- Interest Rates: repo rate, reverse repo, CRR, SLR, lending/deposit rates, monetary policy measures.
- Foreign Exchange: FEMA, FCNR, ECB, foreign currency transactions, remittances, cross-border payments.
- Markets: government securities, bonds, derivatives, FPI, market operations, trading-related measures.
- Banking Regulations: prudential norms, capital adequacy, governance, licensing, supervision, compliance requirements, risk management.
- Savings Schemes: currency withdrawal, banknotes, depositor-focused schemes, public savings initiatives.

Determine whether the notification DIRECTLY affects an ordinary citizen's personal finances.

Set affects_finance:

1 = Yes, if it can directly influence:
- savings
- deposits
- loans
- EMIs
- interest rates
- remittances
- investments
- personal banking
- currency usage

0 = No, if it primarily concerns:
- institutional regulation
- compliance requirements
- governance frameworks
- supervisory actions
- reporting obligations
- AML/CFT measures
- sanctions implementation
- operational requirements for banks and financial institutions

Determine:

- category
- affects_finance (0 or 1)
- impact_level (High, Medium, Low)
- target_audience
- summary (maximum 2 sentences)
- reason

Guidelines for impact_level:

- High: Significant effect on citizens, markets, banking system, or economy.
- Medium: Noticeable effect on a specific sector, institution type, or customer group.
- Low: Limited operational, compliance, or administrative impact.

Return ONLY valid JSON.

Example:

{{
  "category": "Foreign Exchange",
  "affects_finance": 1,
  "impact_level": "Medium",
  "target_audience": "NRI Depositors",
  "summary": "Introduces a swap facility for FCNR deposits.",
  "reason": "Impacts foreign currency deposits and remittance-related activities."
}}

Notification Title:
{title}

Notification Content:
{main_text[:4000]}
"""

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            text = response.text.strip()

            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

            try:
                result = json.loads(text)

            except json.JSONDecodeError:
                print(f"Invalid JSON for: {title}")
                continue

            gemini_category = result.get(
                "category",
                "Other"
            )

            gemini_affects = result.get(
                "affects_finance",
                0
            )

            gemini_summary = result.get(
                "summary",
                ""
            )

            impact_level = result.get(
                "impact_level",
                "Low"
            )

            target_audience = result.get(
                "target_audience",
                ""
            )

            gemini_reason = result.get(
                "reason",
                ""
            )

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

            classified_count += 1

            print(f"✓ {title}")
            print(f"  Category: {gemini_category}")
            print(f"  Affects Finance: {gemini_affects}")
            print(f"  Impact Level: {impact_level}")
            print(f"  Target Audience: {target_audience}")
            print(f"  Summary: {gemini_summary}")
            print(f"  Reason: {gemini_reason}")
            print()

            time.sleep(2)

        except Exception as e:

            print(f"\n✗ Failed: {title}")
            print(e)

            if "429" in str(e):
                print("\nQuota exceeded. Stopping classifier.")
                break

            print()

    conn.close()

    return classified_count


if __name__ == "__main__":

    count = classify_unclassified()
    print(f"\nGemini Classification Complete!")
    print(f"Classified {count} notifications.")