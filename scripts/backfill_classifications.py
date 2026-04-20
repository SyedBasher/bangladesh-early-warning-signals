"""
scripts/backfill_classifications.py
------------------------------------
ONE-TIME script to re-classify all historical signals using the new
LLM-based classifier. Overwrites existing signals/*.json and data/signals.json
with corrected direction/channel/confidence labels.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python scripts/backfill_classifications.py

Run this ONCE after deploying the new interpret_events.py, to clean up
the historical record. After this, the daily pipeline handles everything.

Cost estimate: ~1,600 signals × ~$0.001 per classification = ~$2.
"""

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

# Ensure repo root is importable (for signal_definitions)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic

from signal_definitions import CHANNELS
from interpret_events import (
    CACHE_FILE,
    MODEL,
    MAX_TOKENS,
    SYSTEM_PROMPT,
    classify_with_llm,
    clean_html,
    hash_text,
    load_cache,
    save_cache,
    validate_classification,
)

SIGNALS_DIR = Path("signals")
SIGNALS_FILE = Path("data/signals.json")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    cache = load_cache()
    print(f"Starting backfill. Cache entries: {len(cache)}")

    # Gather all unique (title, source, date) triples from snapshots
    snapshot_files = sorted(SIGNALS_DIR.rglob("*.json"))
    print(f"Found {len(snapshot_files)} snapshot files")

    # Map title_hash -> list of signal records across snapshots
    # so we can preserve each signal's original date/id/source
    all_signals_by_file = {}
    unique_headlines = {}  # hash -> sample (title, source)

    for sf in snapshot_files:
        try:
            with open(sf, encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  skipping {sf}: {e}")
            continue
        if not isinstance(records, list):
            continue
        all_signals_by_file[sf] = records
        for r in records:
            title = clean_html(r.get("headline", "") or r.get("title", "")).strip()
            if not title:
                continue
            h = hash_text(title)
            if h not in unique_headlines:
                unique_headlines[h] = {
                    "title": title,
                    "source": r.get("source", "") or "",
                }

    print(f"Unique headlines to (re)classify: {len(unique_headlines)}")

    # Classify all unique headlines (using cache where possible)
    to_classify = [h for h in unique_headlines if h not in cache]
    print(f"Cache hits: {len(unique_headlines) - len(to_classify)}")
    print(f"New LLM calls needed: {len(to_classify)}")

    for i, h in enumerate(to_classify):
        info = unique_headlines[h]
        classification = classify_with_llm(client, info["title"], info["source"])
        if classification and validate_classification(classification):
            cache[h] = classification
        else:
            # Mark invalid/errored so we skip downstream
            cache[h] = {"channel": "NONE", "direction": "none",
                        "confidence": "none", "is_bangladesh": False,
                        "_backfill_error": True}
        if (i + 1) % 25 == 0:
            save_cache(cache)
            print(f"  {i + 1}/{len(to_classify)} classified, cache saved")

    save_cache(cache)
    print(f"Classification complete. Cache entries: {len(cache)}")

    # Rewrite each snapshot file with corrected signals
    total_rewritten = 0
    total_dropped = 0
    for sf, records in all_signals_by_file.items():
        new_records = []
        file_date = sf.stem  # e.g. "2026-03-08"
        for r in records:
            title = clean_html(r.get("headline", "") or r.get("title", "")).strip()
            if not title:
                continue
            h = hash_text(title)
            classification = cache.get(h)
            if not classification:
                continue
            if not classification.get("is_bangladesh"):
                total_dropped += 1
                continue
            if classification["channel"] == "NONE":
                total_dropped += 1
                continue

            channel = classification["channel"]
            direction = classification["direction"]
            metadata = CHANNELS.get(channel, {}).get(direction)
            if not metadata:
                total_dropped += 1
                continue

            orig_date = r.get("date", file_date)
            link = (r.get("sources") or [""])[0]

            new_records.append({
                "id": f"{orig_date}_{channel.replace(' ', '_')}_{direction}_{h[:8]}",
                "title": metadata["title"],
                "date": orig_date,
                "signal_type": metadata["signal_type"],
                "channel": channel,
                "lead_indicator": metadata["lead_indicator"],
                "time_horizon": metadata["time_horizon"],
                "direction": direction,
                "confidence": classification["confidence"],
                "economic_mechanism": metadata["economic_mechanism"],
                "who_should_care": metadata["who_should_care"],
                "expected_effects": metadata["expected_effects"],
                "headline": title,
                "source": r.get("source", ""),
                "sources": [link] if link else [],
            })
            total_rewritten += 1

        with open(sf, "w", encoding="utf-8") as f:
            json.dump(new_records, f, indent=2, ensure_ascii=False)

    # Rebuild data/signals.json from all snapshots
    all_merged = []
    for sf, _ in all_signals_by_file.items():
        with open(sf, encoding="utf-8") as f:
            try:
                all_merged.extend(json.load(f))
            except json.JSONDecodeError:
                pass

    seen_ids = set()
    deduped = []
    for s in all_merged:
        sid = s.get("id")
        if sid and sid not in seen_ids:
            seen_ids.add(sid)
            deduped.append(s)

    with open(SIGNALS_FILE, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

    # Direction breakdown sanity check
    dir_counts = {}
    for s in deduped:
        d = s.get("direction", "unknown")
        dir_counts[d] = dir_counts.get(d, 0) + 1

    print("\n=== Backfill Summary ===")
    print(f"Signals rewritten: {total_rewritten}")
    print(f"Signals dropped (non-BD or NONE): {total_dropped}")
    print(f"Final signals in data/signals.json: {len(deduped)}")
    print(f"Direction breakdown: {dir_counts}")


if __name__ == "__main__":
    main()
