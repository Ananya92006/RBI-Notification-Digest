import requests
from bs4 import BeautifulSoup

url = "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=13475&Mode=0"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

print("\nPage Title:")
print(soup.title.text)

tables = soup.find_all("table")

print("\nTotal Tables:", len(tables))

for i, table in enumerate(tables):
    print(f"TABLE {i} Length:", len(table.get_text(strip=True)))

print("\n" + "="*80)
print("MAIN CONTENT")
print("="*80)

# Notification content table
main_text = tables[2].get_text(" ", strip=True)

print(main_text[:5000])  # First 5000 chars

print("\n" + "="*80)
print("TOTAL CHARACTERS")
print("="*80)

print(len(main_text))