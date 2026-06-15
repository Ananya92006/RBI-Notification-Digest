from flask import Flask, render_template, request
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        notification = request.form.get(
            "notification",
            ""
        ).strip()

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

YES = Directly affects savings, deposits, loans, EMIs, interest rates, remittances, investments, personal banking, or currency usage.

NO = Primarily concerns institutional regulation, compliance, governance, supervisory actions, AML/CFT measures, sanctions implementation, or operational requirements for financial institutions.

Provide the analysis in the following format:

Category:
Affects Personal Finance:
Impact Level:
Target Audience:
Summary:
Reason:

Notification:
{notification}
"""

        try:

            if not notification:

                result = """
⚠️ Please enter an RBI notification.
"""

            else:

                response = model.generate_content(prompt)

                result = response.text.strip()

                result = result.replace("```", "")
                result = result.replace("**", "")

        except Exception as e:

            error_text = str(e)

            if "429" in error_text:

                result = """
⚠️ Gemini API quota exceeded.

Please try again later or switch to another API key.

The dashboard is still working normally.
"""

            elif "API_KEY" in error_text.upper():

                result = """
⚠️ API authentication failed.

Please check your Gemini API key.
"""

            else:

                result = f"""
⚠️ Analysis could not be completed.

Reason:
{error_text}

Please try again later.
"""

    search = request.args.get("search", "")

    conn = sqlite3.connect("finance_digest.db")
    cursor = conn.cursor()

    # Stats
    cursor.execute("SELECT COUNT(*) FROM notifications")
    total_notifications = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM notifications
    WHERE gemini_affects_finance = 1
    """)
    personal_finance_count = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM notifications
    WHERE impact_level = 'High'
    """)
    high_impact_count = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM notifications
    WHERE gemini_category = 'Foreign Exchange'
    """)
    foreign_exchange_count = cursor.fetchone()[0]

    # Search
    if search:

        cursor.execute("""
        SELECT date,
               title,
               gemini_category,
               gemini_affects_finance,
               impact_level,
               target_audience,
               gemini_summary,
               link
        FROM notifications
        WHERE title LIKE ?
        ORDER BY id DESC
        """, (f"%{search}%",))

    else:

        cursor.execute("""
        SELECT date,
               title,
               gemini_category,
               gemini_affects_finance,
               impact_level,
               target_audience,
               gemini_summary,
               link
        FROM notifications
        ORDER BY id DESC
        """)

    notifications = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        notifications=notifications,
        result=result,
        search=search,
        total_notifications=total_notifications,
        personal_finance_count=personal_finance_count,
        high_impact_count=high_impact_count,
        foreign_exchange_count=foreign_exchange_count
    )


if __name__ == "__main__":
    app.run(debug=True)