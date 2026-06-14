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

        notification = request.form["notification"]

        prompt = f"""
You are an RBI financial analyst.

Analyze this RBI notification and provide:

1. Category
2. Affects Personal Finance (Yes/No)
3. Impact Level
4. Target Audience
5. Short Summary
6. Reason

Notification:
{notification}
"""

        try:
            response = model.generate_content(prompt)
            result = response.text

        except Exception as e:
            result = f"Error: {str(e)}"

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