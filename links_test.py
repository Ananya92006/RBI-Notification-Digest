from bs4 import BeautifulSoup

with open("rbi.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

links = soup.find_all("a")

print("Total links:", len(links))

for a in links[:100]:
    text = a.get_text(strip=True)
    href = a.get("href")

    if text:
        print(text, "->", href)