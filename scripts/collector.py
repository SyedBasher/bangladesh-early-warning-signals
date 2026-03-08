"""
collector.py
------------
Fetches headlines from Bangladesh news sources.
Uses RSS where available, falls back to lightweight HTML scraping
for major sources that have killed their RSS feeds.

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
# Sources
# ------------------------------------------------------------------ #

RSS_FEEDS = [
    # VERIFIED WORKING
    {
        "name": "The Business Standard",
        "url": "https://www.tbsnews.net/economy/rss.xml",
        "section": "economy"
    },
    {
        "name": "The Business Standard — Banking",
        "url": "https://www.tbsnews.net/economy/banking/rss.xml",
        "section": "banking"
    },
    {
        "name": "The Business Standard — Stock",
        "url": "https://www.tbsnews.net/economy/stock/rss.xml",
        "section": "stock"
    },
    {
        "name": "The Business Standard — Industry",
        "url": "https://www.tbsnews.net/economy/industry/rss.xml",
        "section": "industry"
    },
    # TRY MULTIPLE PATTERNS — some may work
    {
        "name": "The Daily Star — Business",
        "url": "https://www.thedailystar.net/business/rss.xml",
        "section": "business"
    },
    {
        "name": "The Daily Star — Frontpage",
        "url": "https://www.thedailystar.net/frontpage/rss.xml",
        "section": "frontpage"
    },
    {
        "name": "The Daily Star — Economy",
        "url": "https://www.thedailystar.net/business/economy/rss.xml",
        "section": "economy"
    },
    {
        "name": "Dhaka Tribune — Business",
        "url": "https://www.dhakatribune.com/business/rss.xml",
        "section": "business"
    },
    {
        "name": "Dhaka Tribune — Economy",
        "url": "https://www.dhakatribune.com/business/economy/rss.xml",
        "section": "economy"
    },
    {
        "name": "Financial Express",
        "url": "https://thefinancialexpress.com.bd/feed",
        "section": "general"
    },
    {
        "name": "New Age — Business",
        "url": "https://www.newagebd.net/rss/business",
        "section": "business"
    },
    {
        "name": "bdnews24 — Economy",
        "url": "https://bdnews24.com/economy/rss",
        "section": "economy"
    },
    {
        "name": "bdnews24 — Main",
        "url": "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true",
        "section": "general"
    },
    {
        "name": "UNB — Business",
        "url": "https://unb.com.bd/rss/Business",
        "section": "business"
    },
    {
        "name": "Bangladesh Post",
        "url": "https://bangladeshpost.net/feed",
        "section": "general"
    },
]

# HTML scraping targets — for sources without working RSS
SCRAPE_TARGETS = [
    {
        "name": "The Daily Star — Business (scrape)",
        "url": "https://www.thedailystar.net/business",
        "link_pattern": r'href="(/business/[^"]+)"[^>]*>\s*<[^>]*>([^<]+)',
        "base_url": "https://www.thedailystar.net"
    },
    {
        "name": "Financial Express — Economy (scrape)",
        "url": "https://thefinancialexpress.com.bd/economy",
        "link_pattern": r'href="(https://thefinancialexpress\.com\.bd/economy/[^"]+)"[^>]*>([^<]{20,})',
        "base_url": ""
    },
    {
        "name": "Dhaka Tribune — Economy (scrape)",
        "url": "https://www.dhakatribune.com/business/economy",
        "link_pattern": r'href="(/business/economy/[^"]+)"[^>]*>\s*(?:<[^>]*>)*\s*([^<]{20,})',
        "base_url": "https://www.dhakatribune.com"
    },
    {
        "name": "New Age — Business (scrape)",
        "url": "https://www.newagebd.net/business",
        "link_pattern": r'href="(/[^"]+)"[^>]*>\s*(?:<[^>]*>)*\s*([^<]{25,})',
        "base_url": "https://www.newagebd.net"
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ------------------------------------------------------------------ #
# RSS Feed parser
# ------------------------------------------------------------------ #

def fetch_feed(url, timeout=15):
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
        if title:
            items.append({"title": title, "link": link})

    # Atom
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        if title:
            items.append({"title": title, "link": link})

    return items

# ------------------------------------------------------------------ #
# HTML scraper — lightweight headline extraction
# ------------------------------------------------------------------ #

def scrape_headlines(url, link_pattern, base_url="", timeout=15):
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except (URLError, Exception) as e:
        print(f"  FAIL (scrape): {url} — {e}")
        return []

    items = []
    seen = set()

    for match in re.finditer(link_pattern, html):
        link = match.group(1)
        title = match.group(2).strip()

        # Clean
        title = re.sub(r'<[^>]+>', '', title)
        title = unescape(title).strip()

        if not title or len(title) < 15:
            continue

        if base_url and not link.startswith("http"):
            link = base_url + link

        # Deduplicate
        norm = title.lower()
        if norm in seen:
            continue
        seen.add(norm)

        items.append({"title": title, "link": link})

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
    working_sources = []
    failed_sources = []

    # Phase 1: RSS feeds
    print("=== Phase 1: RSS Feeds ===")
    for feed in RSS_FEEDS:
        print(f"Fetching: {feed['name']} ({feed['url']})")
        items = fetch_feed(feed["url"])
        count = len(items)
        print(f"  Got {count} items")

        if count > 0:
            working_sources.append(feed["name"])
        else:
            failed_sources.append(feed["name"])

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

    # Phase 2: HTML scraping for sources where RSS failed
    print("\n=== Phase 2: HTML Scraping ===")
    for target in SCRAPE_TARGETS:
        # Only scrape if the RSS version didn't work
        source_base = target["name"].replace(" (scrape)", "")
        rss_worked = any(source_base in ws for ws in working_sources)
        if rss_worked:
            print(f"Skipping {target['name']} — RSS already working")
            continue

        print(f"Scraping: {target['name']} ({target['url']})")
        items = scrape_headlines(
            target["url"],
            target["link_pattern"],
            target.get("base_url", "")
        )
        print(f"  Got {len(items)} headlines")

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
                "source": target["name"].replace(" (scrape)", ""),
                "date": TODAY
            })

    # Write output
    with open("daily_candidates.json", "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)

    print(f"\n=== Summary ===")
    print(f"Working RSS sources: {len(working_sources)}")
    print(f"Failed RSS sources:  {len(failed_sources)}")
    print(f"Total unique candidates: {len(all_candidates)}")
    return all_candidates

if __name__ == "__main__":
    collect()
