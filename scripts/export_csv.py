"""
export_csv.py
-------------
Generates two CSV exports from signals.json:

  data/signals.csv          — PUBLIC: last 10 days only (free sample)
  data/signals_full.csv     — PRIVATE: full history (for paid subscribers)

The public CSV is served on the website.
The full CSV is gitignored and can be delivered to subscribers separately.
"""

import csv
import json
import os
from datetime import date, timedelta

SIGNALS_FILE = "data/signals.json"
PUBLIC_CSV   = "data/signals.csv"
FULL_CSV     = "data/signals_full.csv"
FREE_WINDOW  = 10  # days

if not os.path.exists(SIGNALS_FILE):
    print("No signals.json found.")
    exit()

with open(SIGNALS_FILE) as f:
    signals = json.load(f)

# Sort by date descending
signals.sort(key=lambda s: s.get("date", ""), reverse=True)

# Cutoff date for public feed
cutoff = str(date.today() - timedelta(days=FREE_WINDOW))

public_signals = [s for s in signals if s.get("date", "") >= cutoff]
full_signals   = signals

# Define CSV columns (flat structure for easy analysis)
FIELDS = [
    "id", "date", "title", "channel", "signal_type",
    "direction", "confidence", "lead_indicator", "time_horizon",
    "economic_mechanism", "headline", "source",
    "expected_effects", "who_should_care"
]

def write_csv(filepath, data):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for s in data:
            row = dict(s)
            row["expected_effects"] = "; ".join(s.get("expected_effects", []))
            row["who_should_care"]  = "; ".join(s.get("who_should_care", []))
            row["source"] = s.get("source", "")
            writer.writerow(row)

write_csv(PUBLIC_CSV, public_signals)
write_csv(FULL_CSV, full_signals)

print(f"Public CSV:  {len(public_signals)} rows (last {FREE_WINDOW} days) -> {PUBLIC_CSV}")
print(f"Full CSV:    {len(full_signals)} rows (complete history) -> {FULL_CSV}")
