"""
collector.py
------------
Fetches Bangladesh economic headlines from multiple source types:
  1. Google News RSS — aggregates all BD newspapers
  2. Direct RSS feeds — The Business Standard subsections (verified working)

Articles older than 3 days are filtered out.
Writes: daily_candidates.json
"""

import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.request import urlopen, Request
from urllib.error import URLError

TODAY = str(date.today())
FRESHNESS_DAYS = 3

# ------------------------------------------------------------------ #
# Google News RSS — fewer broader queries to reduce request count
# ------------------------------------------------------------------ #

GOOGLE_NEWS_FEEDS = [
    {
        "name": "Google News — BD Economy & Finance",
        "url": "https://news.google.com/rss/search?q=bangladesh+economy+OR+GDP+OR+inflation+OR+forex+OR+remittance+OR+reserves&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Trade & Exports",
        "url": "https://news.google.com/rss/search?q=bangladesh+exports+OR+garment+OR+RMG+OR+trade+OR+tariff+OR+import&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Banking & Credit",
        "url": "https://news.google.com/rss/search?q=bangladesh+banking+OR+loan+OR+default+OR+interest+rate+OR+Bangladesh+Bank&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Energy & Infrastructure",
        "url": "https://news.google.com/rss/search?q=bangladesh+power+OR+energy+OR+gas+OR+electricity+OR+port+OR+logistics&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Prices & Agriculture",
        "url": "https://news.google.com/rss/search?q=bangladesh+rice+price+OR+food+price+OR+crop+OR+flood+OR+agriculture&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Markets & Investment",
        "url": "https://news.google.com/rss/search?q=bangladesh+stock+market+OR+DSE+OR+FDI+OR+investment+OR+revenue+OR+budget&hl=en-BD&gl=BD&ceid=BD:en"
    },
    {
        "name": "Google News — BD Labor & Industry",
        "url": "https://news.google.com/rss/search?q=bangladesh+factory+OR+worker+OR+wage+OR+layoff+OR+closure+OR+strike&hl=en-BD&gl=BD&ceid=BD:en"
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ------------------------------------------------------------------ #
# Date helpers
# ------------------------------------------------------------------ #

def parse_pub_date(pub_date_str):
    """Parse RSS pubDate to YYYY-MM-DD."""
    if not pub_date_str:
        return None
    try:
        dt = parsedate_to_datetime(pub_date_str)
        return str(dt.date())
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
        return str(dt.date())
    except Exception:
        return None

def is_fresh(date_str, max_days=FRESHNESS_DAYS):
    """Check if a date string is within the last N days."""
    if not date_str:
        return True
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days <= max_days
    except Exception:
        return True

# ------------------------------------------------------------------ #
# RSS Feed parser
# ------------------------------------------------------------------ #

def fetch_feed(url, timeout=20, retries=2):
    """Fetch RSS feed with retry logic."""
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            break
        except (URLError, Exception) as e:
            if attempt < retries:
                wait = 3 * (attempt + 1)
                print(f"  Retry {attempt+1} in {wait}s... ({e})")
                time.sleep(wait)
            else:
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
                "title": title, "link": link,
                "source_tag": source, "pubDate": pub
            })

    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.get("href", "") if link_el is not None else ""
        pub = (entry.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
        if title:
            items.append({
                "title": title, "link": link,
                "source_tag": "", "pubDate": pub
            })

    return items

# ------------------------------------------------------------------ #
# Text helpers
# ------------------------------------------------------------------ #

def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()

def strip_source_suffix(title):
    """Remove ' - Source Name' suffix from Google News headlines."""
    cleaned = re.sub(r'\s+[-–—]\s+[\w\s\.&\|\',]{2,50}$', '', title)
    if len(cleaned) < len(title) * 0.6:
        return title
    return cleaned if cleaned else title

# ------------------------------------------------------------------ #
# Main
# ------------------------------------------------------------------ #

def collect():
    all_candidates = []
    seen_titles = set()

    # Phase 1: Google News RSS
    print("=== Phase 1: Google News RSS ===")
    google_total = 0
    google_fresh = 0
    for i, feed in enumerate(GOOGLE_NEWS_FEEDS):
        if i > 0:
            time.sleep(2)  # polite delay between requests

        print(f"Fetching: {feed['name']}")
        items = fetch_feed(feed["url"])
        print(f"  Got {len(items)} items")
        google_total += len(items)

        for item in items:
            raw_title = clean(item["title"])
            if not raw_title:
                continue

            pub_date = parse_pub_date(item.get("pubDate", ""))
            article_date = pub_date or TODAY

            if not is_fresh(article_date):
                continue
            google_fresh += 1

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

    with open("daily_candidates.json", "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)

    print(f"\n=== Summary ===")
    print(f"Google News items:       {google_total}")
    print(f"Direct RSS items:        {direct_total}")
    print(f"Total unique candidates: {len(all_candidates)} (fresh only)")
    return all_candidates

if __name__ == "__main__":
    collect()
