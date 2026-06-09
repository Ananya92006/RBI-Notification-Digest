import requests

url = "https://rbi.org.in/Scripts/NotificationUser.aspx"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

with open("rbi.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTML Saved")