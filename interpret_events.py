"""
interpret_events.py
-------------------
LLM-based classifier for Bangladesh economic early warning signals.

Pipeline:
  1. Read daily_candidates.json (produced by scripts/collector.py)
  2. For each headline, check the persistent cache; on miss, call Claude
     Haiku to classify (channel, direction, confidence, is_bangladesh)
  3. Look up metadata from signal_definitions.CHANNELS and emit a
     structured signal for each classified headline
  4. Persist cache to data/classification_cache.json (survives across runs)

Environment:
  ANTHROPIC_API_KEY (required) — set via GitHub Actions secret
"""

import hashlib
import json
import os
import re
import sys
import time
from datetime import date, datetime, timezone
from html import unescape

import anthropic

from signal_definitions import CHANNELS

# ------------------------------------------------------------------ #
# Config
# ------------------------------------------------------------------ #

TODAY = str(date.today())

CANDIDATES_FILE = "daily_candidates.json"
SIGNALS_FILE    = "data/signals.json"
SNAPSHOT_DIR    = "signals"
META_FILE       = "data/meta.json"
CACHE_FILE      = "data/classification_cache.json"

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 200
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 2

# ------------------------------------------------------------------ #
# Text helpers
# ------------------------------------------------------------------ #

def hash_text(t):
    return hashlib.md5(t.encode("utf-8")).hexdigest()


def clean_html(text):
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text).strip()


# ------------------------------------------------------------------ #
# Persistent classification cache
# ------------------------------------------------------------------ #

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------ #
# LLM classification
# ------------------------------------------------------------------ #

CHANNEL_DESCRIPTIONS = {
    "Foreign Exchange":  "FX reserves, dollar-taka rate, BoP, LC financing, import payments",
    "Exports":           "garment/RMG exports, shipments, export orders, apparel, leather, jute",
    "Remittances":       "wage earner remittances, migrant workers, expatriate income, hundi",
    "Energy":            "power, gas, fuel, electricity, load shedding, LNG, diesel",
    "Logistics":         "ports (Chittagong/Chattogram), transport, shipping, freight, customs",
    "Credit":            "bank lending, credit growth, loan disbursement, ADR, private sector credit",
    "Banking":           "NPLs, bank capital, deposits, bank governance, liquidity stress",
    "Monetary Policy":   "Bangladesh Bank policy rate, repo, treasury yields, MPS, money supply",
    "Food Prices":       "rice/onion/staple prices, TCB, food inflation, CPI, cost of living",
    "Agriculture":       "crops (boro, aman), floods, drought, fertilizer, fisheries, livestock",
    "Fiscal":            "NBR revenue, budget deficit, government borrowing, treasury bills",
    "Political Risk":    "governance, elections, caretaker government, hartals, institutional crisis",
    "Trade Policy":      "tariffs, import bans, GSP, anti-dumping, duty changes",
    "Labor Market":      "factory closures, layoffs, wages, garment workers, minimum wage",
    "Geopolitical Risk": "Middle East conflicts, Gulf policy, India-BD relations, sanctions affecting BD",
    "Capital Markets":   "DSE, stock market, FDI, bonds, portfolio flows, BSEC",
}


SYSTEM_PROMPT = """You are classifying news headlines for a Bangladesh macroeconomic early warning system.

Your job: for each headline, decide if it reports a concrete economic SIGNAL about the Bangladesh economy that shifts conditions in a discernible direction.

For each headline, return:
1. channel: one of the 16 channels below, or "NONE" if not a macro signal
2. direction: "tightening" (conditions deteriorating) or "easing" (conditions improving), or "none"
3. confidence: "high" (concrete numbers, completed actions), "medium" (qualitative but factual), or "low" (speculative, conditional, proposed), or "none"
4. is_bangladesh: true only if the headline is substantively about the Bangladesh economy

CHANNELS:
""" + "\n".join(f"- {ch}: {desc}" for ch, desc in CHANNEL_DESCRIPTIONS.items()) + """

DIRECTION GUIDANCE:
- tightening = a constraint binds harder: reserves fall, exports drop, load shedding rises, NPLs increase, food prices rise, rates hiked, FDI exits, trade restrictions imposed
- easing = a constraint relaxes: reserves rise, exports grow, load shedding eases, NPLs fall, food prices stabilize, rate cuts materialize, FDI arrives, tariffs reduced
- A policy announcement causing tightening later is tightening today (e.g., "BB hikes policy rate" = Monetary Policy tightening)

RETURN channel="NONE" IF:
- Pure commentary, opinion, analytical think-piece (no new event)
- Ministerial speeches, urgings, exhortations (unless announcing concrete action with numbers or dates)
- Minor corporate news unrelated to macro conditions
- About another country's economy (even if sourced from a BD outlet)
- Descriptive headlines ("Numbers tell the story...", "Why X matters...")
- Crime, sports, entertainment, foreign politics not affecting Bangladesh

Respond with ONLY a JSON object, no other text, no markdown fences. Schema:
{"channel": "...", "direction": "...", "confidence": "...", "is_bangladesh": true}"""


def classify_with_llm(client, title, source):
    """Call Claude Haiku to classify a single headline. Returns dict or None."""
    user_msg = f"Headline: {title}\nSource: {source}"

    for attempt in range(MAX_RETRIES):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = resp.content[0].text.strip()
            # Strip possible markdown fences defensively
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
            return json.loads(text)
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.APIStatusError) as e:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF_SEC * (2 ** attempt)
                print(f"  API error (retry {attempt + 1}/{MAX_RETRIES} in {wait}s): {e}")
                time.sleep(wait)
            else:
                print(f"  API error (giving up): {e}")
                return None
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            print(f"  Parse error for '{title[:60]}': {e}")
            return None
    return None


def validate_classification(c):
    """Check that the classification has sensible fields."""
    if not isinstance(c, dict):
        return False
    required = ["channel", "direction", "confidence", "is_bangladesh"]
    if not all(k in c for k in required):
        return False
    # Valid rejection cases
    if c["channel"] == "NONE":
        return True
    if not c.get("is_bangladesh"):
        return True
    # Positive classifications must have valid values
    if c["channel"] not in CHANNELS:
        return False
    if c["direction"] not in ("tightening", "easing"):
        return False
    if c["confidence"] not in ("high", "medium", "low"):
        return False
    return True


# ------------------------------------------------------------------ #
# Main
# ------------------------------------------------------------------ #

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set. Aborting.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    if not os.path.exists(CANDIDATES_FILE):
        print(f"No {CANDIDATES_FILE} found — nothing to process.")
        return

    with open(CANDIDATES_FILE, encoding="utf-8") as f:
        candidates = json.load(f)
    print(f"Candidates loaded: {len(candidates)}")

    cache = load_cache()
    print(f"Cache entries at start: {len(cache)}")

    signals_output = []
    seen_hashes = set()
    cache_hits = 0
    cache_misses = 0
    rejected_non_bd = 0
    rejected_none = 0
    llm_errors = 0
    invalid_outputs = 0

    for i, item in enumerate(candidates):
        title  = clean_html(item.get("title", "")).strip()
        link   = item.get("link", "")
        source = item.get("source", "")
        dt     = item.get("date", TODAY)

        if not title:
            continue

        h = hash_text(title)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)

        # Check cache first
        if h in cache:
            classification = cache[h]
            cache_hits += 1
        else:
            classification = classify_with_llm(client, title, source)
            cache_misses += 1
            if classification is None:
                llm_errors += 1
                continue
            if not validate_classification(classification):
                print(f"  Invalid classification for '{title[:60]}': {classification}")
                invalid_outputs += 1
                continue
            cache[h] = classification
            # Persist cache periodically to survive partial failures
            if cache_misses % 25 == 0:
                save_cache(cache)
                print(f"  Progress: {cache_misses} LLM calls, cache saved")

        # Apply filters
        if not classification.get("is_bangladesh"):
            rejected_non_bd += 1
            continue
        if classification["channel"] == "NONE":
            rejected_none += 1
            continue

        channel = classification["channel"]
        direction = classification["direction"]
        metadata = CHANNELS.get(channel, {}).get(direction)
        if not metadata:
            print(f"  Missing metadata for {channel}/{direction}")
            continue

        signal = {
            "id": f"{dt}_{channel.replace(' ', '_')}_{direction}_{h[:8]}",
            "title": metadata["title"],
            "date": dt,
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
            "source": source,
            "sources": [link] if link else [],
        }
        signals_output.append(signal)

    # Final cache save
    save_cache(cache)

    # Merge with existing signals
    existing = []
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    existing_ids = {s["id"] for s in existing if "id" in s}
    new_signals = [s for s in signals_output if s["id"] not in existing_ids]
    merged = existing + new_signals

    # Write outputs
    os.makedirs("data", exist_ok=True)
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    with open(SIGNALS_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    snapshot_file = f"{SNAPSHOT_DIR}/{TODAY}.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(signals_output, f, indent=2, ensure_ascii=False)

    # Meta
    dir_counts = {}
    for s in merged:
        d = s.get("direction", "unknown")
        dir_counts[d] = dir_counts.get(d, 0) + 1

    meta = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_signals": len(merged),
        "new_today": len(new_signals),
        "candidates_processed": len(candidates),
        "active_channels": len(set(s["channel"] for s in merged if "channel" in s)),
        "direction_breakdown": dir_counts,
        "cache_size": len(cache),
    }
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("\n=== Summary ===")
    print(f"Candidates:         {len(candidates)}")
    print(f"Cache hits:         {cache_hits}")
    print(f"Cache misses (LLM calls): {cache_misses}")
    print(f"LLM errors:         {llm_errors}")
    print(f"Invalid outputs:    {invalid_outputs}")
    print(f"Rejected non-BD:    {rejected_non_bd}")
    print(f"Rejected NONE:      {rejected_none}")
    print(f"New signals today:  {len(new_signals)}")
    print(f"Total signals:      {len(merged)}")
    print(f"Direction breakdown: {dir_counts}")


if __name__ == "__main__":
    main()
