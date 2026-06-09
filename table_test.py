from bs4 import BeautifulSoup

with open("rbi.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

table = soup.find_all("table")[0]

rows = table.find_all("tr")

print("Rows:", len(rows))

for row in rows[:20]:
    print(row.get_text(" ", strip=True))
    print("-"*80)