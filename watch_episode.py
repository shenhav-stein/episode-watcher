import requests
import smtplib
import json
import os
from email.mime.text import MIMEText
import xml.etree.ElementTree as ET

SERIES_NAME = "A Knight of the Seven Kingdoms"
RSS_URL = "https://thepiratebay.org/search.php?q=A+Knight+of+the+Seven+Kingdoms&all=on&search=Pirate+Search&page=0&orderby="

STATE_FILE = "state.json"

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = "shenhavstein@gmail.com"

# Load state
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {"next_episode": 2}

episode_number = state["next_episode"]
episode_str = f"S01E{episode_number:02d}"

print(f"Looking for {episode_str}")

response = requests.get(RSS_URL, timeout=30)
root = ET.fromstring(response.content)

found_valid = False
valid_entry_text = ""

for item in root.findall(".//item"):
    title = item.find("title").text

    print("RSS TITLE:", title)

    if SERIES_NAME in title and episode_str in title:
        found_valid = True
        valid_entry_text = title
        break

if found_valid:

    msg = MIMEText(f"New episode available:\n\n{valid_entry_text}")
    msg["Subject"] = f"{SERIES_NAME} {episode_str} is Available!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())

    state["next_episode"] += 1

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

    print("Email sent and episode incremented.")

else:
    print("No valid episode found.")

