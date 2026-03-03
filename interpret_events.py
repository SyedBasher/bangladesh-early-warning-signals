import json
import os
import yaml
import hashlib
import re
from datetime import date
from signal_definitions import SIGNALS

today = str(date.today())

# ------------------------------------------------
# confidence detection
# ------------------------------------------------

STRONG = ["surge","collapse","halt","freeze","spike","crisis","plunge","shortage","slump"]
WEAK   = ["may","possible","expected","considering","proposal","plan","talks"]

def confidence_level(text):
    t = text.lower()
    if any(w in t for w in STRONG):
        return "high"
    if any(w in t for w in WEAK):
        return "low"
    return "medium"

def importance_from_confidence(c):
    return {"low":"low","medium":"medium","high":"high"}[c]

# ------------------------------------------------
# helpers
# ------------------------------------------------

from html import unescape

def hash_text(t):
    return hashlib.md5(t.encode()).hexdigest()

def clean_html(text):
    """
    Properly remove HTML tags and decode entities.
    Handles <a href="...">Title</a> safely.
    """
    text = re.sub(r'<[^>]+>', '', text)  # remove all HTML tags
    return unescape(text).strip()

def normalize_text(text):
    """
    Normalize common plural forms and spacing.
    Makes matching more flexible.
    """
    t = text.lower()
    t = t.replace("exports", "export")
    t = t.replace("loans", "loan")
    t = t.replace("prices", "price")
    t = re.sub(r'\s+', ' ', t)
    return t

def extract_percentage(text):
    """
    Detect percentage change like:
    'exports fall 12%'
    'inflation rises to 9.4 percent'
    """
    match = re.search(
        r'(\d+(\.\d+)?)\s?%|\b(\d+(\.\d+)?)\s?percent\b',
        text.lower()
    )
    if match:
        return float(match.group(1))
    return None

# ------------------------------------------------
# improved classification logic
# ------------------------------------------------

def classify(headline):

    raw = clean_html(headline)
    h = normalize_text(raw)

    negative_words = ["drop","fall","decline","slump","plunge","contract","weak"]
    positive_words = ["rise","increase","surge","expand","grow"]

    for name, info in SIGNALS.items():

        # Relax keyword matching:
        # Instead of requiring full phrase match,
        # match any core token inside keywords.
        keyword_hit = False

        for k in info["keywords"]:
            k_norm = normalize_text(k)
            if k_norm in h:
                keyword_hit = True
                break

            # Also allow partial token match (first word)
            first_token = k_norm.split()[0]
            if first_token in h:
                keyword_hit = True
                break

        directional_hit = any(w in h for w in negative_words + positive_words)

        if keyword_hit and directional_hit:
            return {
                "event": name,
                "channel": info["channel"],
                "transmission": info["transmission"],
                "expected_effect": info["effect"],
                "confidence": confidence_level(h)
            }

    return None
    
# ------------------------------------------------
# read candidate headlines
# ------------------------------------------------

if not os.path.exists("daily_candidates.json"):
    print("No daily_candidates.json found.")
    exit()

with open("daily_candidates.json") as f:
    headlines = json.load(f)
print("Total headlines loaded:", len(headlines))

for h in headlines[:10]:
    print("Sample headline:", h.get("title"))
notes = []
seen_hashes = set()

for item in headlines:

    title = clean_html(item.get("title", "")).strip()
    link = item.get("link", "")

    if not title:
        continue

    result = classify(title)
    if not result:
        continue

    # deduplicate
    h = hash_text(title)
    if h in seen_hashes:
        continue
    seen_hashes.add(h)

    note = {
        "date": today,
        "country": "Bangladesh",
        "summary": title,
        **result,
        "importance": importance_from_confidence(result["confidence"]),
        "sources": [link]
    }

    notes.append(note)

# ------------------------------------------------
# write YAML drafts
# ------------------------------------------------

os.makedirs("drafts", exist_ok=True)

for i, note in enumerate(notes, 1):

    short = note["event"].replace("_", "-")
    filename = f"drafts/{today}-{short}-{i}.yaml"

    with open(filename, "w") as f:
        yaml.dump(note, f, sort_keys=False, allow_unicode=True)

print("Draft signals generated:", len(notes))
