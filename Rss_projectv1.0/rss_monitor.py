import feedparser
import pandas as pd
import json
import os
import time
import schedule
from datetime import datetime

CONFIG_FILE = "feeds_config.json"
SEEN_FILE = "seen_articles.json"
EXCEL_FILE = "news_output.xlsx"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_seen_links():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_links(seen_links):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_links), f)

def fetch_and_update():
    feeds = load_config()
    seen_links = load_seen_links()
    new_entries = []

    for source, data in feeds.items():
        feed_url = data["url"]
        language = data.get("language", "Unknown")
        region = data.get("region", "Unknown")
        state = data.get("state", "Unknown")

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching: {source}")
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            link = entry.get("link", "")
            if not link or link in seen_links:
                continue

            new_entries.append({
                "Publication": source,
                "Language": language,
                "Region": region,
                "State": state,
                "Title": entry.get("title", ""),
                "Link": link,
                "Published": entry.get("published", ""),
                "Summary": entry.get("summary", "")
            })
            seen_links.add(link)

    if new_entries:
        df_new = pd.DataFrame(new_entries)
        if os.path.exists(EXCEL_FILE):
            df_existing = pd.read_excel(EXCEL_FILE)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_excel(EXCEL_FILE, index=False)
        print(f"✅ {len(new_entries)} new articles saved.")
    else:
        print("ℹ️ No new articles found.")

    save_seen_links(seen_links)

# Run every 30 minutes
schedule.every(30).minutes.do(fetch_and_update)

print("🚀 RSS Feed Monitor started... Running every 30 minutes.")
fetch_and_update()  # Initial run

while True:
    schedule.run_pending()
    time.sleep(1)
