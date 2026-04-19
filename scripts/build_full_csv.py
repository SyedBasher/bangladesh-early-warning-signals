"""
Aggregates all daily signal snapshots in signals/ into a single CSV.
Runs as the final step in the daily GitHub Actions workflow.
Pure stdlib — no dependencies.
"""
import csv
import json
from pathlib import Path

SIGNALS_DIR = Path("signals")
OUTPUT_PATH = Path("data/signals_full.csv")


def load_snapshot(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  skipping {path.name}: {e}")
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("signals", [data])
    return []


def flatten(value):
    """Convert lists/dicts to JSON strings so they fit in a CSV cell."""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def main():
    rows = []
    files = sorted(SIGNALS_DIR.rglob("*.json"))
    print(f"Found {len(files)} snapshot files in {SIGNALS_DIR}/")

    for path in files:
        for r in load_snapshot(path):
            if not isinstance(r, dict):
                continue
            r = dict(r)
            r["snapshot_date"] = path.stem
            r["snapshot_country"] = (
                path.parent.name if path.parent.name != "signals" else "root"
            )
            rows.append(r)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        print("No signals found — writing empty CSV.")
        OUTPUT_PATH.write_text("", encoding="utf-8")
        return

    # Union of all keys across all rows (schema may vary across snapshots)
    seen, fieldnames = set(), []
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)

    priority = ["snapshot_date", "date", "channel", "direction",
                "confidence", "title", "headline"]
    fieldnames.sort(key=lambda k: (priority.index(k) if k in priority else 999, k))

    rows.sort(key=lambda r: (
        r.get("snapshot_date", ""),
        r.get("date", ""),
        r.get("channel", ""),
    ))

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: flatten(r.get(k, "")) for k in fieldnames})

    dates = [r.get("snapshot_date", "") for r in rows if r.get("snapshot_date")]
    print(f"Wrote {len(rows):,} rows to {OUTPUT_PATH} "
          f"spanning {min(dates)} → {max(dates)}")


if __name__ == "__main__":
    main()
