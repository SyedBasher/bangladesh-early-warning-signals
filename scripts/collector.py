"""
collector.py
------------
Fetches headlines from Bangladesh newspaper RSS feeds.
Writes: daily_candidates.json
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from html import unescape
from urllib.request import urlopen, Request
from urllib.error import URLError

TODAY = str(date.today())

# ------------------------------------------------------------------ #
# RSS feed sources — Bangladesh business / economic news
# ------------------------------------------------------------------ #

FEEDS = [
    # The Daily Star — Business
    {
        "name": "The Daily Star",
        "url": "https://www.thedailystar.net/business/rss.xml",
        "section": "business"
    },
    # Dhaka Tribune — Business
    {
        "name": "Dhaka Tribune",
        "url": "https://www.dhakatribune.com/business/rss.xml",
        "section": "business"
    },
    # The Financial Express
    {
        "name": "The Financial Express",
        "url": "https://thefinancialexpress.com.bd/feed",
        "section": "general"
    },
    # New Age — Business
    {
        "name": "New Age",
        "url": "https://www.newagebd.net/rss/business",
        "section": "business"
    },
    # Bangladesh Post — National / Business
    {
        "name": "Bangladesh Post",
        "url": "https://bangladeshpost.net/feed",
        "section": "general"
    },
    # bdnews24 — Economy
    {
        "name": "bdnews24",
        "url": "https://bdnews24.com/economy/rss",
        "section": "economy"
    },
    # The Business Standard
    {
        "name": "The Business Standard",
        "url": "https://www.tbsnews.net/economy/rss.xml",
        "section": "economy"
    },
]

HEADERS = {
    "User-Agent": "BangladeshEWSCollector/1.0 (economic research)"
}

# ------------------------------------------------------------------ #
# Feed parser (handles RSS 2.0 and Atom)
# ------------------------------------------------------------------ #

def fetch_feed(url, timeout=15):
    """Fetch and parse an RSS/Atom feed, return list of items."""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except (URLError, Exception) as e:
        print(f"  FAIL: {url} — {e}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  PARSE ERROR: {url} — {e}")
        return []

    items = []

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link") or "").strip()
        pub   = (item.findtext("pubDate") or "").strip()
        if title:
            items.append({"title": title, "link": link, "pubDate": pub})

    # Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("atom:title", namespaces=ns) or
                 entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        pub  = (entry.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
        if title:
            items.append({"title": title, "link": link, "pubDate": pub})

    return items

def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()

# ------------------------------------------------------------------ #
# Main collection
# ------------------------------------------------------------------ #

def collect():
    all_candidates = []
    seen_titles = set()

    for feed in FEEDS:
        print(f"Fetching: {feed['name']} ({feed['url']})")
        items = fetch_feed(feed["url"])
        print(f"  Got {len(items)} items")

        for item in items:
            title = clean(item["title"])
            if not title:
                continue

            # basic dedup by normalized title
            norm = title.lower().strip()
            if norm in seen_titles:
                continue
            seen_titles.add(norm)

            all_candidates.append({
                "title": title,
                "link": item.get("link", ""),
                "source": feed["name"],
                "date": TODAY
            })

    # Write output
    with open("daily_candidates.json", "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)

    print(f"\nTotal unique candidates: {len(all_candidates)}")
    return all_candidates

if __name__ == "__main__":
    collect()
