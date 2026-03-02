import json
from datetime import date
import yaml

today = str(date.today())

def classify(headline):

    h = headline.lower()

    if any(k in h for k in ["gas", "lng", "oil", "fuel"]):
        return {
            "event": "energy_price_shock",
            "transmission": [
                "fuel import cost",
                "electricity tariff pressure",
                "food production cost",
                "CPI food"
            ],
            "expected_effect": "regressive welfare loss",
            "confidence": "medium"
        }

    if any(k in h for k in ["export", "garment export", "shipment fall"]):
        return {
            "event": "export_demand_shock",
            "transmission": [
                "factory hours",
                "labor income",
                "urban consumption"
            ],
            "expected_effect": "income slowdown",
            "confidence": "medium"
        }

    return None


# read headlines
with open("daily_candidates.json") as f:
    headlines = json.load(f)

notes = []

for item in headlines:
    result = classify(item["title"])
    if result:
        note = {
            "date": today,
            "country": "Bangladesh",
            "summary": item["title"],
            **result,
            "sources": [item["link"]]
        }
        notes.append(note)

with open("draft_notes.yaml", "w") as f:
    yaml.dump(notes, f, sort_keys=False)

print("Draft signals generated:", len(notes))
