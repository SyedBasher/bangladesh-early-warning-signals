import json
import os
import re
import hashlib
from datetime import date
from html import unescape
from signal_definitions import SIGNALS

today = str(date.today())

# ------------------------------------------------
# Confidence detection
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

# ------------------------------------------------
# Helpers
# ------------------------------------------------

def hash_text(t):
    return hashlib.md5(t.encode()).hexdigest()

def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()

def normalize_text(text):
    t = text.lower()
    t = t.replace("exports", "export")
    t = t.replace("loans", "loan")
    t = t.replace("prices", "price")
    t = re.sub(r'\s+', ' ', t)
    return t

# ------------------------------------------------
# Classification
# ------------------------------------------------

def classify(headline):

    raw = clean_html(headline)
    h = normalize_text(raw)

    negative_words = ["drop","fall","decline","slump","plunge","contract","weak"]
    positive_words = ["rise","increase","surge","expand","grow"]

    for name, info in SIGNALS.items():

        keyword_hit = False

        for k in info["keywords"]:
            k_norm = normalize_text(k)

            if k_norm in h:
                keyword_hit = True
                break

            first_token = k_norm.split()[0]
            if first_token in h:
                keyword_hit = True
                break

        directional_hit = any(w in h for w in negative_words + positive_words)

        if keyword_hit and directional_hit:
            return name

    return None

# ------------------------------------------------
# Load candidate headlines
# ------------------------------------------------

if not os.path.exists("daily_candidates.json"):
    print("No daily_candidates.json found.")
    exit()

with open("daily_candidates.json") as f:
    headlines = json.load(f)

print("Total headlines loaded:", len(headlines))

# ------------------------------------------------
# Build structured signals
# ------------------------------------------------

signals_output = []
seen_hashes = set()

for item in headlines:

    title = clean_html(item.get("title", "")).strip()
    link = item.get("link", "")

    if not title:
        continue

    event_key = classify(title)
    if not event_key:
        continue

    # deduplicate
    h = hash_text(title)
    if h in seen_hashes:
        continue
    seen_hashes.add(h)

    signal_info = SIGNALS[event_key]

    structured_signal = {
        "title": signal_info["title"],
        "date": today,
        "signal_type": signal_info["signal_type"],
        "lead_indicator": signal_info["lead_indicator"],
        "time_horizon": signal_info["time_horizon"],
        "direction": signal_info["direction"],
        "confidence": confidence_level(title),
        "economic_mechanism": signal_info["economic_mechanism"],
        "who_should_care": signal_info["who_should_care"],
        "expected_effects": signal_info["expected_effects"],
        "headline": title,
        "sources": [link]
    }

    signals_output.append(structured_signal)

# ------------------------------------------------
# Ensure data folder exists
# ------------------------------------------------

if not os.path.exists("data"):
    os.makedirs("data")

# ------------------------------------------------
# Write JSON output
# ------------------------------------------------

with open("data/signals.json", "w", encoding="utf-8") as f:
    json.dump(signals_output, f, indent=2, ensure_ascii=False)

print("Signals written:", len(signals_output))
