import requests
from bs4 import BeautifulSoup
import re

url = "https://rbi.org.in/Scripts/NotificationUser.aspx"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

table = soup.find_all("table")[0]

# rows define karo
rows = table.find_all("tr")

notifications = []

current_date = None

date_pattern = r"^[A-Z][a-z]{2}\s\d{2},\s\d{4}$"

for row in rows:
    text = row.get_text(" ", strip=True)

    if re.match(date_pattern, text):
        current_date = text

    else:
        links = row.find_all("a")

        for link in links:
            title = link.get_text(strip=True)

            if title:
                notifications.append({
                    "date": current_date,
                    "title": title,
                    "link": link.get("href")
                })

print("Total Notifications:", len(notifications))

for item in notifications[:5]:
    print(item)