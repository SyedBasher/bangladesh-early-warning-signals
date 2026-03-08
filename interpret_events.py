"""
interpret_events.py
-------------------
Classifies daily headline candidates into structured economic signals.
Reads:  daily_candidates.json   (list of {title, link, source?, date?})
Writes: data/signals.json       (structured signal feed)
        signals/YYYY-MM-DD.json (daily snapshot)
"""

import json
import os
import re
import hashlib
from datetime import date
from html import unescape
from signal_definitions import SIGNALS

TODAY = str(date.today())

# ------------------------------------------------------------------ #
# Confidence scoring
# ------------------------------------------------------------------ #

HIGH_CONF = [
    "surge", "collapse", "halt", "freeze", "spike", "crisis",
    "plunge", "shortage", "slump", "soar", "crash", "panic",
    "record high", "record low", "all-time", "unprecedented",
    "suspend", "shut down", "emergency"
]
LOW_CONF = [
    "may", "possible", "expected", "considering", "proposal",
    "plan", "talk", "explore", "likely", "could", "might",
    "under review", "preliminary", "draft"
]

def confidence_level(text):
    t = text.lower()
    if any(w in t for w in HIGH_CONF):
        return "high"
    if any(w in t for w in LOW_CONF):
        return "low"
    return "medium"

# ------------------------------------------------------------------ #
# Text helpers
# ------------------------------------------------------------------ #

def hash_text(t):
    return hashlib.md5(t.encode()).hexdigest()

def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()

def normalize(text):
    """Lowercase, collapse whitespace, basic plural normalization."""
    t = text.lower()
    # normalize common plurals/variants
    t = re.sub(r"exports?", "export", t)
    t = re.sub(r"imports?", "import", t)
    t = re.sub(r"loans?", "loan", t)
    t = re.sub(r"prices?", "price", t)
    t = re.sub(r"orders?", "order", t)
    t = re.sub(r"reserves?", "reserve", t)
    t = re.sub(r"workers?", "worker", t)
    t = re.sub(r"factories", "factory", t)
    t = re.sub(r"banks?(?!\w)", "bank", t)   # "banks" → "bank" but not "banking"
    t = re.sub(r"rates?(?!\w)", "rate", t)
    # verb forms
    t = re.sub(r"falls\b", "fall", t)
    t = re.sub(r"drops\b", "drop", t)
    t = re.sub(r"rises\b", "rise", t)
    t = re.sub(r"declines\b", "decline", t)
    t = re.sub(r"raises\b", "raise", t)
    t = re.sub(r"imposes\b", "impose", t)
    t = re.sub(r"demands?\b", "demand", t)
    t = re.sub(r"surges\b", "surge", t)
    t = re.sub(r"conditions?\b", "condition", t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# ------------------------------------------------------------------ #
# Keyword matching — supports multi-word phrases and partial matches
# ------------------------------------------------------------------ #

def keyword_score(headline_norm, keywords):
    """
    Returns (hit_count, best_match_length).
    Multi-word phrase match scores higher than single-word fragment.
    """
    hits = 0
    best_len = 0
    for kw in keywords:
        kw_norm = normalize(kw)
        # exact phrase match
        if kw_norm in headline_norm:
            hits += 1
            best_len = max(best_len, len(kw_norm.split()))
            continue
        # partial: check if all tokens of the keyword appear in headline
        tokens = kw_norm.split()
        if len(tokens) >= 2 and all(tok in headline_norm for tok in tokens):
            hits += 1
            best_len = max(best_len, len(tokens))
    return hits, best_len

# ------------------------------------------------------------------ #
# Directional words — distinguish tightening vs easing
# ------------------------------------------------------------------ #

NEGATIVE = [
    "drop", "fall", "decline", "slump", "plunge", "contract",
    "weak", "slow", "shrink", "cut", "reduce", "loss", "lose",
    "shortage", "crisis", "deficit", "down", "low", "worst",
    "collapse", "halt", "freeze", "suspend", "close", "shut",
    "damage", "destroy", "erode", "miss", "fail", "delay",
    "hike", "surge", "spike", "soar", "rise", "jump",
    "strike", "protest", "unrest", "block", "ban",
    "impose", "restrict", "raise", "demand", "condition",
    "short", "cancel", "crash", "wipe"
]

POSITIVE = [
    "rise", "increase", "surge", "expand", "grow", "growth",
    "improve", "gain", "boost", "recover", "rebound", "jump",
    "high", "record", "strong"
]

# Note: some words (rise, surge, jump) appear in both lists because
# their direction depends on context (price rise = tightening,
# export rise = easing). The signal direction comes from the
# signal definition, not the word polarity.

def has_directional_word(headline_norm):
    """Check if headline contains any action/direction word (substring match)."""
    for w in NEGATIVE + POSITIVE:
        if w in headline_norm:
            return True
    return False

# ------------------------------------------------------------------ #
# Classification
# ------------------------------------------------------------------ #

def classify(headline):
    """
    Returns the best-matching signal key, or None.
    Strategy: score each signal by keyword hits and match quality,
    require at least one directional word, pick the best match.
    """
    raw = clean_html(headline)
    h = normalize(raw)

    if not has_directional_word(h):
        return None

    best_key = None
    best_score = (0, 0)  # (hit_count, best_phrase_length)

    for name, info in SIGNALS.items():
        hits, phrase_len = keyword_score(h, info["keywords"])
        if hits > 0:
            score = (hits, phrase_len)
            if score > best_score:
                best_score = score
                best_key = name

    return best_key

# ------------------------------------------------------------------ #
# Load candidate headlines
# ------------------------------------------------------------------ #

CANDIDATES_FILE = "daily_candidates.json"

if not os.path.exists(CANDIDATES_FILE):
    print(f"No {CANDIDATES_FILE} found — nothing to process.")
    exit()

with open(CANDIDATES_FILE) as f:
    headlines = json.load(f)

print(f"Headlines loaded: {len(headlines)}")

# ------------------------------------------------------------------ #
# Build structured signals
# ------------------------------------------------------------------ #

signals_output = []
seen_hashes = set()

for item in headlines:

    title = clean_html(item.get("title", "")).strip()
    link  = item.get("link", "")
    src   = item.get("source", "")
    dt    = item.get("date", TODAY)

    if not title:
        continue

    event_key = classify(title)
    if not event_key:
        continue

    h = hash_text(title)
    if h in seen_hashes:
        continue
    seen_hashes.add(h)

    info = SIGNALS[event_key]

    structured_signal = {
        "id": f"{dt}_{event_key}_{h[:8]}",
        "title": info["title"],
        "date": dt,
        "signal_type": info["signal_type"],
        "channel": info["channel"],
        "lead_indicator": info["lead_indicator"],
        "time_horizon": info["time_horizon"],
        "direction": info["direction"],
        "confidence": confidence_level(title),
        "economic_mechanism": info["economic_mechanism"],
        "who_should_care": info["who_should_care"],
        "expected_effects": info["expected_effects"],
        "headline": title,
        "source": src,
        "sources": [link] if link else []
    }

    signals_output.append(structured_signal)

# ------------------------------------------------------------------ #
# Merge with existing signals (append, don't overwrite history)
# ------------------------------------------------------------------ #

SIGNALS_FILE = "data/signals.json"

existing = []
if os.path.exists(SIGNALS_FILE):
    with open(SIGNALS_FILE) as f:
        try:
            existing = json.load(f)
        except json.JSONDecodeError:
            existing = []

# Deduplicate by id
existing_ids = {s["id"] for s in existing if "id" in s}
new_signals  = [s for s in signals_output if s["id"] not in existing_ids]

merged = existing + new_signals

# ------------------------------------------------------------------ #
# Write outputs
# ------------------------------------------------------------------ #

os.makedirs("data", exist_ok=True)
os.makedirs("signals", exist_ok=True)

with open(SIGNALS_FILE, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

# Daily snapshot
snapshot_file = f"signals/{TODAY}.json"
with open(snapshot_file, "w", encoding="utf-8") as f:
    json.dump(signals_output, f, indent=2, ensure_ascii=False)

# Pipeline health metadata
from datetime import datetime, timezone
meta = {
    "last_updated": datetime.now(timezone.utc).isoformat(),
    "total_signals": len(merged),
    "new_today": len(new_signals),
    "candidates_processed": len(headlines),
    "active_channels": len(set(s["channel"] for s in merged if "channel" in s))
}
with open("data/meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)

print(f"New signals today:  {len(new_signals)}")
print(f"Total signals:      {len(merged)}")
print(f"Daily snapshot:     {snapshot_file}")
