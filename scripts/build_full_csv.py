"""
Aggregates all daily signal snapshots in signals/ into a single CSV.
Runs as the final step in the daily GitHub Actions workflow.
"""
import json
from pathlib import Path
import pandas as pd

SIGNALS_DIR = Path("signals")
OUTPUT_PATH = Path("data/signals_full.csv")

def load_snapshot(path: Path) -> list[dict]:
    """Load a daily snapshot, handling both list and dict JSON shapes."""
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  skipping {path.name}: {e}")
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("signals", [data])
    return []

def main():
    rows = []
    files = sorted(SIGNALS_DIR.rglob("*.json"))
    print(f"Found {len(files)} snapshot files in {SIGNALS_DIR}/")

    for path in files:
        records = load_snapshot(path)
        for r in records:
            if not isinstance(r, dict):
                continue
            r = dict(r)  # don't mutate in place
            r["snapshot_date"] = path.stem
            r["snapshot_country"] = path.parent.name if path.parent.name != "signals" else "root"
            rows.append(r)

    if not rows:
        print("No signals found — writing empty CSV.")
        pd.DataFrame().to_csv(OUTPUT_PATH, index=False)
        return

    df = pd.DataFrame(rows)
    sort_cols = [c for c in ["snapshot_date", "date", "channel"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    date_min = df.get("snapshot_date", pd.Series()).min()
    date_max = df.get("snapshot_date", pd.Series()).max()
    print(f"Wrote {len(df):,} rows to {OUTPUT_PATH} spanning {date_min} → {date_max}")

if __name__ == "__main__":
    main()
