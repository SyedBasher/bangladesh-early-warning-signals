import feedparser
from datetime import datetime
import json

FEEDS = {
    "DailyStar": "https://www.thedailystar.net/business/rss.xml",
    "FinancialExpress": "https://thefinancialexpress.com.bd/rss/economy",
    "NewAge": "https://www.newagebd.net/rss/business"
}

KEYWORDS = [
    "import","export","remittance","inflation","dollar","reserve",
    "gas","power","tariff","bank","interest","loan","lc","fuel",
    "subsidy","tax","budget","wage","industry"
]

def relevant(title):
    t = title.lower()
    return any(k in t for k in KEYWORDS)

items = []

for source, url in FEEDS.items():
    feed = feedparser.parse(url)
    for e in feed.entries:
        if relevant(e.title):
            items.append({
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "source": source,
                "title": e.title,
                "link": e.link
            })

items = sorted(items, key=lambda x: x["title"])

with open("daily_candidates.json","w") as f:
    json.dump(items,f,indent=2)

print("Collected",len(items),"candidate signals")
