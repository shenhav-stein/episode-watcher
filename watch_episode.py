import requests
from bs4 import BeautifulSoup
import smtplib
import json
import re
import os
from email.mime.text import MIMEText

# =========================
# CONFIG
# =========================

SERIES_NAME = "A Knight of the Seven Kingdoms"
BASE_URL = "https://thepiratebay.org"
SEARCH_URL = "https://thepiratebay.org/search.php?q=A+Knight+of+the+Seven+Kingdoms&all=on&search=Pirate+Search&page=0&orderby="

STATE_FILE = "state.json"

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = "shenhavstein@gmail.com"

# =========================
# Load or initialize state
# =========================

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {"next_episode": 2}  # you've watched episode 01

episode_number = state["next_episode"]
episode_str = f"S01E{episode_number:02d}"

print(f"Looking for {episode_str}")

# =========================
# Fetch website
# =========================

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(SEARCH_URL, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", id="searchResult")

found_valid = False
valid_entry_text = ""

if table:
    rows = table.find_all("tr")[1:]  # skip header row

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 4:
            continue

        title = cols[1].get_text(" ", strip=True)
        se = int(cols[2].get_text(strip=True))
        le = int(cols[3].get_text(strip=True))

        size_text = cols[1].find("font").get_text()
        size_match = re.search(r"Size\s*([\d\.]+)\s*GiB", size_text)

        if not size_match:
            continue

        size = float(size_match.group(1))

        if SERIES_NAME in title and episode_str in title:
            if se > 100 and le > 100 and size > 1.00:
                found_valid = True
                valid_entry_text = f"{title}\nSE: {se} | LE: {le} | Size: {size} GiB"
                break

# =========================
# Send email if found
# =========================

if found_valid:

    msg = MIMEText(f"New episode available:\n\n{valid_entry_text}")
    msg["Subject"] = f"{SERIES_NAME} {episode_str} is Available!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())

    # increment episode
    state["next_episode"] += 1

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

    print("Email sent and episode incremented.")

else:
    print("No valid episode found.")