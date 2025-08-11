!pip install feedparser schedule

import feedparser
import sqlite3
import schedule
import time
from datetime import datetime

# ========================
# CONFIG
# ========================
RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml",
    "https://indianexpress.com/feed/",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://www.reuters.com/rssFeed/worldNews",
    "https://www.cnn.com/rss/edition_world.rss"
]

DB_NAME = "articles.db"

# ========================
# DATABASE SETUP
# ========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            published TEXT,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

# ========================
# FETCH & STORE
# ========================
def fetch_and_store():
    print(f"\n[INFO] Fetching RSS feeds at {datetime.now()}")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        source_title = feed.feed.get("title", "Unknown Source")

        for entry in feed.entries:
            try:
                cur.execute("""
                    INSERT INTO articles (title, link, published, source)
                    VALUES (?, ?, ?, ?)
                """, (
                    entry.get("title", "No Title"),
                    entry.get("link", ""),
                    entry.get("published", ""),
                    source_title
                ))
                conn.commit()
                print(f"[NEW] {entry.get('title', 'No Title')} from {source_title}")

            except sqlite3.IntegrityError:
                # Duplicate article (same link) - skip
                print(f"[DUPLICATE] Skipping {entry.get('title', 'No Title')}")

    conn.close()

# ========================
# SCHEDULER
# ========================
def start_scheduler():
    schedule.every(30).minutes.do(fetch_and_store)  # Runs every 30 mins
    print("[INFO] RSS Feed Collector Scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(1)

# ========================
# MAIN
# ========================
if _name_ == "_main_":
    init_db()
    fetch_and_store()  # First run
    start_scheduler()
