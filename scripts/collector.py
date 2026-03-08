"""
collector.py
------------
Fetches Bangladesh economic headlines from multiple source types:
  1. Google News RSS — aggregates all BD newspapers (primary source)
  2. Direct RSS feeds — The Business Standard subsections (verified working)

Writes: daily_candidates.json
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from html import unescape
from urllib.request import urlopen, Request
from urllib.error import URLError

TODAY = str(date.today())

# ------------------------------------------------------------------ #
# Google News RSS searches — these aggregate ALL BD newspapers
# Each query targets a different economic channel
# ------------------------------------------------------------------ #

GOOGLE_NEWS_FEEDS = [
    {
        "name": "Google News — BD Economy",
        "url": "https://news.google.com/rss/search?q=bangladesh+economy+OR+GDP+OR+inflation&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Exports & Trade",
        "url": "https://news.google.com/rss/search?q=bangladesh+exports+OR+garment+OR+RMG+OR+trade&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Banking & Finance",
        "url": "https://news.google.com/rss/search?q=bangladesh+bank+OR+loan+OR+banking+OR+interest+rate&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Forex & Remittance",
        "url": "https://news.google.com/rss/search?q=bangladesh+dollar+OR+forex+OR+remittance+OR+reserves&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Energy & Power",
        "url": "https://news.google.com/rss/search?q=bangladesh+power+OR+energy+OR+gas+OR+electricity+OR+load+shedding&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Food Prices",
        "url": "https://news.google.com/rss/search?q=bangladesh+rice+price+OR+food+price+OR+onion+price+OR+inflation&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Stock Market",
        "url": "https://news.google.com/rss/search?q=bangladesh+stock+market+OR+DSE+OR+share+price+OR+FDI&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Revenue & Fiscal",
        "url": "https://news.google.com/rss/search?q=bangladesh+NBR+revenue+OR+budget+OR+tax+OR+fiscal&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Climate & Agriculture",
        "url": "https://news.google.com/rss/search?q=bangladesh+flood+OR+cyclone+OR+crop+OR+agriculture+OR+drought&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Labor & Industry",
        "url": "https://news.google.com/rss/search?q=bangladesh+factory+OR+worker+OR+garment+closure+OR+layoff+OR+wage&hl=en-BD&gl=BD&ceid=BD:en"
    },
]

# ------------------------------------------------------------------ #
# Direct RSS feeds — verified working
# ------------------------------------------------------------------ #

DIRECT_FEEDS = [
    {
        "name": "The Business Standard — Economy",
        "url": "https://www.tbsnews.net/economy/rss.xml"
    },
    {
        "name": "The Business Standard — Banking",
        "url": "https://www.tbsnews.net/economy/banking/rss.xml"
    },
    {
        "name": "The Business Standard — Industry",
        "url": "https://www.tbsnews.net/economy/industry/rss.xml"
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ------------------------------------------------------------------ #
# RSS Feed parser
# ------------------------------------------------------------------ #

def fetch_feed(url, timeout=20):
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

    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link") or "").strip()
        source = (item.findtext("source") or "").strip()
        if title:
            items.append({"title": title, "link": link, "source_tag": source})

    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        if title:
            items.append({"title": title, "link": link, "source_tag": ""})

    return items

# ------------------------------------------------------------------ #
# Text helpers
# ------------------------------------------------------------------ #

def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()

# ------------------------------------------------------------------ #
# Main collection
# ------------------------------------------------------------------ #

def collect():
    all_candidates = []
    seen_titles = set()

    # Phase 1: Google News RSS
    print("=== Phase 1: Google News RSS ===")
    google_total = 0
    for feed in GOOGLE_NEWS_FEEDS:
        print(f"Fetching: {feed['name']}")
        items = fetch_feed(feed["url"])
        print(f"  Got {len(items)} items")
        google_total += len(items)

        for item in items:
            title = clean(item["title"])
            if not title:
                continue

            # Google News titles sometimes include " - Source Name"
            # Keep it — helps identify the newspaper
            source_name = item.get("source_tag", "") or feed["name"]

            norm = title.lower().strip()
            if norm in seen_titles:
                continue
            seen_titles.add(norm)

            all_candidates.append({
                "title": title,
                "link": item.get("link", ""),
                "source": source_name,
                "date": TODAY
            })

    # Phase 2: Direct RSS feeds
    print("\n=== Phase 2: Direct RSS Feeds ===")
    direct_total = 0
    for feed in DIRECT_FEEDS:
        print(f"Fetching: {feed['name']} ({feed['url']})")
        items = fetch_feed(feed["url"])
        print(f"  Got {len(items)} items")
        direct_total += len(items)

        for item in items:
            title = clean(item["title"])
            if not title:
                continue
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

    print(f"\n=== Summary ===")
    print(f"Google News items:     {google_total}")
    print(f"Direct RSS items:      {direct_total}")
    print(f"Total unique candidates: {len(all_candidates)}")
    return all_candidates

if __name__ == "__main__":
    collect()
