def classify_notification(text):
    """Rule-based notification classifier.
    Returns (affects_finance, category) tuple."""

    text = text.lower()

    # Interest Rates
    if any(word in text for word in [
        "repo rate",
        "reverse repo",
        "interest rate",
        "cash reserve ratio",
        "crr",
        "statutory liquidity ratio",
        "slr"
    ]):
        return 1, "Interest Rates"

    # Foreign Exchange
    elif any(word in text for word in [
        "foreign exchange",
        "fema",
        "external commercial borrowing",
        "ecb",
        "fcnr",
        "cross border merger",
        "authorised dealer",
        "authorised dealer category-i",
        "remittance",
        "foreign currency",
        "export of goods and services",
        "nop-inr"
    ]):
        return 1, "Foreign Exchange"

    # Markets
    elif any(word in text for word in [
        "foreign portfolio investor",
        "fpi",
        "government securities",
        "derivative",
        "bond market",
        "trading",
        "market"
    ]):
        return 0, "Markets"

    # Banking Regulations
    elif any(word in text for word in [
        "governance",
        "prudential norms",
        "capital adequacy",
        "financial statements",
        "classification",
        "valuation",
        "investment portfolio",
        "co-operative banks",
        "commercial banks",
        "regional rural banks",
        "small finance banks",
        "payment banks",
        "local area banks"
    ]):
        return 0, "Banking Regulations"

    # Savings Schemes
    elif any(word in text for word in [
        "saving account",
        "savings account",
        "fixed deposit",
        "deposit",
        "pension",
        "banknote",
        "currency",
        "withdrawal of ₹2000",
        "withdrawal of old series"
    ]):
        return 1, "Savings Schemes"

    # Insurance
    elif any(word in text for word in [
        "insurance",
        "policyholder",
        "claim settlement"
    ]):
        return 1, "Insurance"

    # Taxes
    elif any(word in text for word in [
        "tax",
        "gst",
        "income tax",
        "tds"
    ]):
        return 1, "Taxes"

    # Everything else
    return 0, "Other"


def run_classification(db_path="finance_digest.db"):
    """Run rule-based classification on all notifications."""

    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title
    FROM notifications
    """)

    rows = cursor.fetchall()

    for row in rows:

        notification_id, title = row

        affects_finance, category = classify_notification(title)

        cursor.execute("""
        UPDATE notifications
        SET category = ?,
            affects_finance = ?
        WHERE id = ?
        """,
        (
            category,
            affects_finance,
            notification_id
        ))

    conn.commit()
    conn.close()

    print("Classification complete!")


if __name__ == "__main__":
    run_classification()