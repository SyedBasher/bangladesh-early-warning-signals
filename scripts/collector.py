"""
collector.py
------------
Fetches Bangladesh economic headlines from multiple source types:
  1. Google News RSS — aggregates all BD newspapers (last 3 days only)
  2. Direct RSS feeds — The Business Standard subsections (verified working)

Writes: daily_candidates.json
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.request import urlopen, Request
from urllib.error import URLError

TODAY = str(date.today())
FRESHNESS_DAYS = 3  # only keep articles from the last N days

# ------------------------------------------------------------------ #
# Google News RSS searches — limited to last 3 days with "when:3d"
# ------------------------------------------------------------------ #

GOOGLE_NEWS_FEEDS = [
    {
        "name": "Google News — BD Economy",
        "url": "https://news.google.com/rss/search?q=bangladesh+economy+OR+GDP+OR+inflation+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Exports & Trade",
        "url": "https://news.google.com/rss/search?q=bangladesh+exports+OR+garment+OR+RMG+OR+trade+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Banking & Finance",
        "url": "https://news.google.com/rss/search?q=bangladesh+bank+OR+loan+OR+banking+OR+interest+rate+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Forex & Remittance",
        "url": "https://news.google.com/rss/search?q=bangladesh+dollar+OR+forex+OR+remittance+OR+reserves+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Energy & Power",
        "url": "https://news.google.com/rss/search?q=bangladesh+power+OR+energy+OR+gas+OR+electricity+OR+load+shedding+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Food Prices",
        "url": "https://news.google.com/rss/search?q=bangladesh+rice+price+OR+food+price+OR+onion+price+OR+inflation+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Stock Market",
        "url": "https://news.google.com/rss/search?q=bangladesh+stock+market+OR+DSE+OR+share+price+OR+FDI+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Revenue & Fiscal",
        "url": "https://news.google.com/rss/search?q=bangladesh+NBR+revenue+OR+budget+OR+tax+OR+fiscal+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Climate & Agriculture",
        "url": "https://news.google.com/rss/search?q=bangladesh+flood+OR+cyclone+OR+crop+OR+agriculture+OR+drought+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Labor & Industry",
        "url": "https://news.google.com/rss/search?q=bangladesh+factory+OR+worker+OR+garment+closure+OR+layoff+OR+wage+when:3d&hl=en-BD&gl=BD&ceid=BD:en"
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
# RSS Feed parser — extracts pubDate for real article dates
# ------------------------------------------------------------------ #

def parse_pub_date(pub_date_str):
    """Parse RSS pubDate to YYYY-MM-DD. Returns None if unparseable."""
    if not pub_date_str:
        return None
    try:
        dt = parsedate_to_datetime(pub_date_str)
        return str(dt.date())
    except Exception:
        pass
    # Try ISO format
    try:
        dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
        return str(dt.date())
    except Exception:
        return None

def is_fresh(date_str, max_days=FRESHNESS_DAYS):
    """Check if a date string is within the last N days."""
    if not date_str:
        return True  # if we can't parse date, keep it
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days <= max_days
    except Exception:
        return True

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
        pub   = (item.findtext("pubDate") or "").strip()
        if title:
            items.append({
                "title": title,
                "link": link,
                "source_tag": source,
                "pubDate": pub
            })

    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        pub = (entry.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
        if title:
            items.append({
                "title": title,
                "link": link,
                "source_tag": "",
                "pubDate": pub
            })

    return items

# ------------------------------------------------------------------ #
# Text helpers
# ------------------------------------------------------------------ #

def clean(text):
    """Remove HTML tags, unescape entities."""
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()

def strip_source_suffix(title):
    """Remove ' - Source Name' suffix that Google News appends."""
    # Match " - Source Name" at end (source is typically 1-5 words)
    cleaned = re.sub(r'\s+[-–—]\s+[\w\s\.&\|\',]{2,50}$', '', title)
    # Don't strip if it removed too much (more than 40% of title)
    if len(cleaned) < len(title) * 0.6:
        return title
    return cleaned if cleaned else title

# ------------------------------------------------------------------ #
# Main collection
# ------------------------------------------------------------------ #

def collect():
    all_candidates = []
    seen_titles = set()

    cutoff = str(date.today() - timedelta(days=FRESHNESS_DAYS))

    # Phase 1: Google News RSS
    print("=== Phase 1: Google News RSS (last 3 days) ===")
    google_total = 0
    google_fresh = 0
    for feed in GOOGLE_NEWS_FEEDS:
        print(f"Fetching: {feed['name']}")
        items = fetch_feed(feed["url"])
        print(f"  Got {len(items)} items")
        google_total += len(items)

        for item in items:
            raw_title = clean(item["title"])
            if not raw_title:
                continue

            # Use real publication date, not today
            pub_date = parse_pub_date(item.get("pubDate", ""))
            article_date = pub_date or TODAY

            # Skip stale articles
            if not is_fresh(article_date):
                continue
            google_fresh += 1

            # Clean headline for display and classification
            title = strip_source_suffix(raw_title)
            source_name = item.get("source_tag", "") or feed["name"]

            norm = title.lower().strip()
            if norm in seen_titles:
                continue
            seen_titles.add(norm)

            all_candidates.append({
                "title": title,
                "link": item.get("link", ""),
                "source": source_name,
                "date": article_date
            })

    print(f"  Fresh articles: {google_fresh}/{google_total}")

    # Phase 2: Direct RSS feeds
    print("\n=== Phase 2: Direct RSS Feeds ===")
    direct_total = 0
    for feed in DIRECT_FEEDS:
        print(f"Fetching: {feed['name']} ({feed['url']})")
        items = fetch_feed(feed["url"])
        print(f"  Got {len(items)} items")
        direct_total += len(items)

        for item in items:
            raw_title = clean(item["title"])
            if not raw_title:
                continue

            pub_date = parse_pub_date(item.get("pubDate", ""))
            article_date = pub_date or TODAY

            if not is_fresh(article_date):
                continue

            title = strip_source_suffix(raw_title)
            norm = title.lower().strip()
            if norm in seen_titles:
                continue
            seen_titles.add(norm)

            all_candidates.append({
                "title": title,
                "link": item.get("link", ""),
                "source": feed["name"],
                "date": article_date
            })

    # Write output
    with open("daily_candidates.json", "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)

    print(f"\n=== Summary ===")
    print(f"Google News items:       {google_total}")
    print(f"Direct RSS items:        {direct_total}")
    print(f"Total unique candidates: {len(all_candidates)} (after freshness filter)")
    return all_candidates

if __name__ == "__main__":
    collect()
