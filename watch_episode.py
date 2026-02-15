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
    rows = table.find_all("tr")[1:]

    print(f"Found {len(rows)} rows")

    for row in rows:
        title_tag = row.find("a", class_="detLink")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        print("TITLE FOUND:", title)

        if SERIES_NAME in title and episode_str in title:
            found_valid = True
            valid_entry_text = title
            break
else:
    print("No searchResult table found!")
