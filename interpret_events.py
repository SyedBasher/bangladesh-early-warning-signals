import json
import os
import yaml
import hashlib
import re
from datetime import date
from signal_definitions import SIGNALS

today = str(date.today())

# ---------------------------
# confidence detection
# ---------------------------

STRONG = ["surge","collapse","halt","freeze","spike","crisis","plunge","shortage"]
WEAK   = ["may","possible","expected","considering","proposal","plan"]

def confidence_level(text):
    t = text.lower()
    if any(w in t for w in STRONG):
        return "high"
    if any(w in t for w in WEAK):
        return "low"
    return "medium"

# ---------------------------
# deduplication helper
# ---------------------------

def hash_text(t):
    return hashlib.md5(t.encode()).hexdigest()

def clean_html(text):
    return re.sub('<.*?>', '', text)

# ---------------------------
# classification logic
# ---------------------------

def classify(headline):

    h = headline.lower()

    for name, info in SIGNALS.items():
        if any(keyword in h for keyword in info["keywords"]):
            return {
                "event": name,
                "channel": info["channel"],
                "transmission": info["transmission"],
                "expected_effect": info["effect"],
                "confidence": confidence_level(h)
            }

    return None

# ---------------------------
# read candidate headlines
# ---------------------------

with open("daily_candidates.json") as f:
    headlines = json.load(f)

notes = []
seen_hashes = set()

for item in headlines:

    title = clean_html(item["title"]).strip()
    link = item["link"]

    result = classify(title)
    if not result:
        continue

    # remove duplicates
    h = hash_text(title)
    if h in seen_hashes:
        continue
    seen_hashes.add(h)

    note = {
        "date": today,
        "country": "Bangladesh",
        "summary": title,
        **result,
        "sources": [link]
    }

    notes.append(note)

# ---------------------------
# write individual YAML drafts
# ---------------------------

os.makedirs("drafts", exist_ok=True)

for i, note in enumerate(notes, 1):

    short = note["event"].replace("_", "-")
    filename = f"drafts/{today}-{short}-{i}.yaml"

    with open(filename, "w") as f:
        yaml.dump(note, f, sort_keys=False, allow_unicode=True)

print("Draft signals generated:", len(notes))
