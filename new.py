from bs4 import BeautifulSoup
import re

with open("rbi.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

table = soup.find_all("table")[0]

rows = table.find_all("tr")

date_pattern = r"^[A-Z][a-z]{2}\s\d{2},\s\d{4}$"

current_date = None

for row in rows[:20]:
    text = row.get_text(" ", strip=True)

    if re.match(date_pattern, text):
        current_date = text
        print("\nDATE FOUND:", current_date)

    else:
        print("NOTIFICATION:", current_date, "->", text[:80])