"""
scripts/compute_stress_index.py
--------------------------------
Composite Bangladesh Macro Stress Index (0-100) from classified signals.

Pipeline:
  1. Read data/signals.json
  2. For each channel and each day in the history, compute a weighted,
     time-decayed signed intensity over the trailing window
  3. Percentile-rank each channel's intensity against its own history -> [0, 100]
  4. Weighted average across channels -> composite stress index
  5. Write data/stress_index.json with the daily series + per-channel contributions

Output schema (data/stress_index.json):
  {
    "last_updated": ISO timestamp,
    "methodology_version": "1.0",
    "params": {half_life_days, window_days, ...},
    "channel_weights": {...},
    "series": [
      {
        "date": "YYYY-MM-DD",
        "composite": 72.3,          # 0-100, higher = more macro stress
        "zone": "amber",            # green / amber / red
        "channels": {
          "Foreign Exchange":   {"score": 80.1, "intensity": 5.42, "n_recent": 8},
          ...
        }
      },
      ...
    ]
  }
"""

import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ------------------------------------------------------------------ #
# Config
# ------------------------------------------------------------------ #

SIGNALS_FILE = Path("data/signals.json")
OUTPUT_FILE  = Path("data/stress_index.json")

HALF_LIFE_DAYS     = 14      # decay: a signal's weight halves every 14 days
WINDOW_DAYS        = 60      # only consider signals within trailing 60 days
MIN_HISTORY_DAYS   = 10      # need at least this much history before publishing index
METHODOLOGY_VERSION = "1.0"

CONFIDENCE_WEIGHT = {"high": 3, "medium": 2, "low": 1}

# Channel weights: structural importance to BD macro
# Sum = 100; these are priors — revise with empirical calibration later.
CHANNEL_WEIGHTS = {
    "Foreign Exchange":   15,
    "Exports":            12,
    "Remittances":        10,
    "Food Prices":        10,
    "Credit":              8,
    "Banking":             8,
    "Energy":              8,
    "Monetary Policy":     7,
    "Fiscal":              6,
    "Political Risk":      6,
    "Agriculture":         4,
    "Logistics":           3,
    "Trade Policy":        1,
    "Labor Market":        1,
    "Geopolitical Risk":   1,
    "Capital Markets":     0,   # hard-data anchor (DSEX) instead
}

# Stress zones for UI colour-coding
ZONE_GREEN_MAX = 35
ZONE_AMBER_MAX = 65


# ------------------------------------------------------------------ #
# Core math
# ------------------------------------------------------------------ #

def decay_weight(age_days, half_life=HALF_LIFE_DAYS):
    """Exponential decay; halves every `half_life` days."""
    return math.pow(2, -age_days / half_life)


def channel_intensity(signals_in_channel, as_of_date):
    """
    Signed, confidence-weighted, time-decayed sum of signals within
    the trailing WINDOW_DAYS. Positive = net tightening. Negative = net easing.
    """
    total = 0.0
    n_recent = 0
    for s in signals_in_channel:
        age = (as_of_date - s["_dt"]).days
        if age < 0 or age > WINDOW_DAYS:
            continue
        conf_w = CONFIDENCE_WEIGHT.get(s["confidence"], 1)
        dir_sign = 1 if s["direction"] == "tightening" else -1
        total += dir_sign * conf_w * decay_weight(age)
        n_recent += 1
    return total, n_recent


def percentile_rank(value, distribution):
    """Fraction of distribution <= value, in [0, 1]. Ties: midrank."""
    if not distribution:
        return 0.5
    below = sum(1 for x in distribution if x < value)
    equal = sum(1 for x in distribution if x == value)
    return (below + 0.5 * equal) / len(distribution)


def zone_for_score(score):
    if score <= ZONE_GREEN_MAX:
        return "green"
    if score <= ZONE_AMBER_MAX:
        return "amber"
    return "red"


# ------------------------------------------------------------------ #
# Main computation
# ------------------------------------------------------------------ #

def compute_index(signals):
    # Parse dates and group by channel
    by_channel = {ch: [] for ch in CHANNEL_WEIGHTS}
    all_dates = set()

    for s in signals:
        ch = s.get("channel")
        if ch not in CHANNEL_WEIGHTS:
            continue
        if s.get("direction") not in ("tightening", "easing"):
            continue
        try:
            s["_dt"] = datetime.strptime(s["date"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        by_channel[ch].append(s)
        all_dates.add(s["_dt"])

    if not all_dates:
        return None

    start_date = min(all_dates)
    end_date = max(all_dates)
    n_days = (end_date - start_date).days + 1

    if n_days < MIN_HISTORY_DAYS:
        print(f"Only {n_days} days of history; need at least {MIN_HISTORY_DAYS}.")

    # Build daily time series of intensity per channel
    intensity_series = {ch: [] for ch in CHANNEL_WEIGHTS}
    n_recent_series  = {ch: [] for ch in CHANNEL_WEIGHTS}
    date_list = []

    cur = start_date
    while cur <= end_date:
        date_list.append(cur)
        for ch in CHANNEL_WEIGHTS:
            I, n = channel_intensity(by_channel[ch], cur)
            intensity_series[ch].append(I)
            n_recent_series[ch].append(n)
        cur += timedelta(days=1)

    # Percentile-rank each channel against its own history → 0-100
    channel_scores = {ch: [] for ch in CHANNEL_WEIGHTS}
    for ch in CHANNEL_WEIGHTS:
        series = intensity_series[ch]
        # Use only non-zero observations as the comparison distribution
        # (a channel with zero signals is "neutral", not "historically low stress")
        nonzero = [x for x in series if x != 0]
        if not nonzero:
            channel_scores[ch] = [50.0] * len(series)
            continue
        for x in series:
            if x == 0:
                channel_scores[ch].append(50.0)  # neutral when no activity
            else:
                p = percentile_rank(x, nonzero)
                channel_scores[ch].append(100.0 * p)

    # Composite = weighted average of channel scores
    total_w = sum(CHANNEL_WEIGHTS.values())
    composite = []
    for i in range(len(date_list)):
        s = sum(channel_scores[ch][i] * w for ch, w in CHANNEL_WEIGHTS.items())
        composite.append(s / total_w)

    # Assemble output
    series_out = []
    for i, d in enumerate(date_list):
        row = {
            "date": d.isoformat(),
            "composite": round(composite[i], 2),
            "zone": zone_for_score(composite[i]),
            "channels": {
                ch: {
                    "score":     round(channel_scores[ch][i], 2),
                    "intensity": round(intensity_series[ch][i], 3),
                    "n_recent":  n_recent_series[ch][i],
                }
                for ch in CHANNEL_WEIGHTS
            },
        }
        series_out.append(row)

    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "methodology_version": METHODOLOGY_VERSION,
        "params": {
            "half_life_days":   HALF_LIFE_DAYS,
            "window_days":      WINDOW_DAYS,
            "confidence_weights": CONFIDENCE_WEIGHT,
            "zone_thresholds": {"green_max": ZONE_GREEN_MAX, "amber_max": ZONE_AMBER_MAX},
        },
        "channel_weights": CHANNEL_WEIGHTS,
        "series": series_out,
    }
    return output


def main():
    if not SIGNALS_FILE.exists():
        print(f"ERROR: {SIGNALS_FILE} not found.")
        return
    with open(SIGNALS_FILE, encoding="utf-8") as f:
        signals = json.load(f)

    result = compute_index(signals)
    if result is None:
        print("No usable signals. Skipping index update.")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Summary
    series = result["series"]
    latest = series[-1]
    print(f"Stress index computed: {len(series)} days, "
          f"{result['series'][0]['date']} to {latest['date']}")
    print(f"Latest composite: {latest['composite']} ({latest['zone']})")
    print(f"Top 3 stressed channels today:")
    top = sorted(latest["channels"].items(),
                 key=lambda kv: kv[1]["score"], reverse=True)[:3]
    for ch, d in top:
        print(f"  {ch:20s} score={d['score']:5.1f}  n_recent={d['n_recent']}")


if __name__ == "__main__":
    main()
