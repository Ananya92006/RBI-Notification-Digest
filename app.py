from flask import Flask, render_template, request
import sqlite3
from google import genai as genai
from dotenv import load_dotenv
from datetime import datetime, date
from collections import defaultdict
import secrets
import time
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))


# -----------------------------------------------
# Built-in Rate Limiter (no external dependency)
# -----------------------------------------------
class RateLimiter:
    """Simple in-memory rate limiter per IP address.
    Allows max_requests within window_seconds."""

    def __init__(self, max_requests=5, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(list)

    def is_allowed(self, ip):
        """Check if the IP is within rate limits."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old entries
        self._requests[ip] = [
            t for t in self._requests[ip] if t > cutoff
        ]

        if len(self._requests[ip]) >= self.max_requests:
            return False

        self._requests[ip].append(now)
        return True


# 5 Gemini analysis requests per minute per IP
rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


# -----------------------------------------------
# Gemini Client — lazy initialization
# -----------------------------------------------
_gemini_client = None


def get_gemini_client():
    """Lazy-initialize the Gemini client so the app
    doesn't crash at startup if no API key is set."""

    global _gemini_client

    if _gemini_client is None:

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key == "your_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please set it in the .env file."
            )

        _gemini_client = genai.Client(
            api_key=api_key
        )

    return _gemini_client


# -----------------------------------------------
# Daily Quota — max 50 Gemini calls per day
# -----------------------------------------------
DAILY_GEMINI_QUOTA = 50


def get_daily_usage():
    """Get the number of Gemini API calls made today."""
    conn = sqlite3.connect("finance_digest.db")
    cursor = conn.cursor()

    # Create usage tracking table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_date TEXT,
        call_count INTEGER DEFAULT 0
    )
    """)
    conn.commit()

    today = date.today().isoformat()

    cursor.execute(
        "SELECT call_count FROM api_usage WHERE call_date = ?",
        (today,)
    )
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 0


def increment_daily_usage():
    """Record a Gemini API call for today."""
    conn = sqlite3.connect("finance_digest.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_date TEXT,
        call_count INTEGER DEFAULT 0
    )
    """)

    today = date.today().isoformat()

    cursor.execute(
        "SELECT id FROM api_usage WHERE call_date = ?",
        (today,)
    )
    row = cursor.fetchone()

    if row:
        cursor.execute(
            "UPDATE api_usage SET call_count = call_count + 1 "
            "WHERE call_date = ?",
            (today,)
        )
    else:
        cursor.execute(
            "INSERT INTO api_usage (call_date, call_count) "
            "VALUES (?, 1)",
            (today,)
        )

    conn.commit()
    conn.close()


# -----------------------------------------------
# Helper — format ISO date for display
# -----------------------------------------------
def format_date(iso_date):
    """Convert '2026-06-10' to '10 Jun 2026' for display."""
    if not iso_date:
        return ""
    try:
        parsed = datetime.strptime(iso_date, "%Y-%m-%d")
        return parsed.strftime("%d %b %Y")
    except ValueError:
        return iso_date


# -----------------------------------------------
# Routes
# -----------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    quota_remaining = DAILY_GEMINI_QUOTA - get_daily_usage()

    if request.method == "POST":

        # --- Rate limit check ---
        client_ip = request.remote_addr or "unknown"
        if not rate_limiter.is_allowed(client_ip):

            result = (
                "⚠️ Too many requests. "
                "Please wait a minute before trying again."
            )

        else:

            # --- Honeypot check ---
            # Hidden field "website" should be empty
            # (bots auto-fill it)
            honeypot = request.form.get("website", "")
            if honeypot:
                result = "⚠️ Request rejected."

            else:

                notification = request.form.get(
                    "notification",
                    ""
                ).strip()

                # --- Minimum input length ---
                if len(notification) < 20:

                    result = (
                        "⚠️ Please enter at least 20 characters "
                        "of RBI notification text for "
                        "meaningful analysis."
                    )

                # --- Daily quota check ---
                elif quota_remaining <= 0:

                    result = (
                        "⚠️ Daily analysis limit reached "
                        f"({DAILY_GEMINI_QUOTA} per day).\n\n"
                        "The dashboard data is still available "
                        "below.\n"
                        "Please try again tomorrow."
                    )

                else:

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

                        client = get_gemini_client()
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt
                        )

                        result = response.text.strip()
                        result = result.replace("```", "")
                        result = result.replace("**", "")

                        # Record usage
                        increment_daily_usage()
                        quota_remaining -= 1

                    except ValueError as e:
                        # API key not configured
                        result = f"⚠️ {str(e)}"

                    except Exception as e:

                        error_text = str(e)

                        if "429" in error_text:

                            result = (
                                "⚠️ Gemini API quota exceeded."
                                "\n\nPlease try again later or "
                                "switch to another API key."
                                "\n\nThe dashboard is still "
                                "working normally."
                            )

                        elif "API_KEY" in error_text.upper():

                            result = (
                                "⚠️ API authentication failed."
                                "\n\nPlease check your Gemini "
                                "API key."
                            )

                        else:

                            result = (
                                "⚠️ Analysis could not be "
                                "completed.\n\n"
                                f"Reason:\n{error_text}\n\n"
                                "Please try again later."
                            )

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

    # Search — ordered by date (ISO format sorts correctly)
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
        ORDER BY date DESC
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
        ORDER BY date DESC
        """)

    rows = cursor.fetchall()

    # Format dates for display
    notifications = []
    for row in rows:
        formatted_row = (format_date(row[0]),) + row[1:]
        notifications.append(formatted_row)

    conn.close()

    return render_template(
        "index.html",
        notifications=notifications,
        result=result,
        search=search,
        total_notifications=total_notifications,
        personal_finance_count=personal_finance_count,
        high_impact_count=high_impact_count,
        foreign_exchange_count=foreign_exchange_count,
        quota_remaining=quota_remaining
    )


if __name__ == "__main__":
    app.run(debug=True)