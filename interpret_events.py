import json
import os
import yaml
import hashlib
from datetime import date

today = str(date.today())

# ---------------------------
# keyword groups (semantic buckets)
# ---------------------------

ENERGY = [
    "gas","lng","oil","diesel","fuel","petroleum",
    "electricity tariff","power tariff","energy price"
]

EXPORT = [
    "export","shipment","orders","rmg","apparel",
    "garment","buyers","factory","overtime",
    "export earnings","shipment receipts"
]

STRONG = ["surge","collapse","halt","freeze","spike","crisis","plunge","shortage"]
WEAK   = ["may","possible","expected","considering","proposal","plan"]

# ---------------------------
# helpers
# ---------------------------

def contains_any(text, words):
    return any(w in text for w in words)

def confidence_level(text):
    t = text.lower()
    if any(w in t for w in STRONG):
        return "high"
    if any(w in t for w in WEAK):
        return "low"
    return "medium"

def hash_text(t):
    return hashlib.md5(t.encode()).hexdigest()

# ---------------------------
# classification logic
# ---------------------------

def classify(headline):

    h = headline.lower()

    # ENERGY SHOCK
    if contains_any(h, ENERGY):
        return {
            "event": "energy_price_shock",
            "channel": "cost_push",
            "transmission": [
                "fuel import cost",
                "electricity tariff pressure",
                "food production cost",
                "CPI food"
            ],
            "expected_effect": "regressive welfare loss",
            "confidence": confidence_level(h)
        }

    # EXPORT DEMAND SHOCK
    if contains_any(h, EXPORT):
        return {
            "event": "export_demand_shock",
            "channel": "external_sector",
            "transmission": [
                "factory hours",
                "labor income",
                "urban consumption"
            ],
            "expected_effect": "income slowdown",
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

    title = item["title"].strip()
    link = item["link"]

    result = classify(title)
    if not result:
        continue

    # deduplicate repeated news stories
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
