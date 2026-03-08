"""
export_csv.py
-------------
Generates a CSV export from signals.json for institutional subscribers.
Outputs: data/signals.csv
"""

import csv
import json
import os

SIGNALS_FILE = "data/signals.json"
CSV_FILE = "data/signals.csv"

if not os.path.exists(SIGNALS_FILE):
    print("No signals.json found.")
    exit()

with open(SIGNALS_FILE) as f:
    signals = json.load(f)

# Define CSV columns (flat structure for easy analysis)
FIELDS = [
    "id", "date", "title", "channel", "signal_type",
    "direction", "confidence", "lead_indicator", "time_horizon",
    "economic_mechanism", "headline", "source",
    "expected_effects", "who_should_care"
]

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()

    for s in signals:
        row = dict(s)
        # Flatten list fields
        row["expected_effects"] = "; ".join(s.get("expected_effects", []))
        row["who_should_care"]  = "; ".join(s.get("who_should_care", []))
        row["source"] = s.get("source", "")
        writer.writerow(row)

print(f"CSV exported: {len(signals)} rows → {CSV_FILE}")
