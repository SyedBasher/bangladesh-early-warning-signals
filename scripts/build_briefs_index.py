"""
scripts/build_briefs_index.py
------------------------------
Scan the `briefs/` directory for PDF files named YYYY-MM-DD.pdf and emit
`data/briefs.json` as a machine-readable index that the website reads to
render the briefs list.

Naming convention:
  briefs/2026-04-27.pdf            -> appears as "27 April 2026"
  briefs/2026-04-27-title-slug.pdf -> appears as "27 April 2026 — Title Slug"

Schema (data/briefs.json):
  {
    "last_updated": "2026-...",
    "count": 12,
    "briefs": [
      {"date": "2026-04-27", "title": "...", "path": "briefs/2026-04-27.pdf"},
      ...
    ]
  }
"""

import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path

BRIEFS_DIR = Path("briefs")
OUT_FILE   = Path("data/briefs.json")

FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-(.+))?\.pdf$", re.IGNORECASE)


def humanise_title(slug):
    if not slug:
        return ""
    words = re.split(r"[-_]+", slug)
    return " ".join(w.capitalize() for w in words if w)


def main():
    if not BRIEFS_DIR.exists():
        BRIEFS_DIR.mkdir(parents=True, exist_ok=True)

    items = []
    for f in sorted(BRIEFS_DIR.glob("*.pdf")):
        m = FILENAME_RE.match(f.name)
        if not m:
            print(f"  skipping (name doesn't match YYYY-MM-DD[-slug].pdf): {f.name}")
            continue
        d_str, slug = m.group(1), m.group(2)
        try:
            date.fromisoformat(d_str)
        except ValueError:
            print(f"  skipping (bad date): {f.name}")
            continue
        items.append({
            "date":  d_str,
            "title": humanise_title(slug),
            "path":  str(f).replace("\\", "/"),
            "size_kb": round(f.stat().st_size / 1024, 1),
        })

    # Most recent first
    items.sort(key=lambda x: x["date"], reverse=True)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "briefs": items,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Indexed {len(items)} brief(s) -> {OUT_FILE}")
    for it in items[:5]:
        print(f"  {it['date']}  {it['title'] or '(untitled)'}  [{it['size_kb']} KB]")


if __name__ == "__main__":
    main()
