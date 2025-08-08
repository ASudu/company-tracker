#!/usr/bin/env python3
"""
fetch_data.py
- Run from GitHub Actions daily.
- Writes JSON files into ./data/
"""
import os
import json
import time
import feedparser
import yfinance as yf
from datetime import datetime, timezone
from urllib.parse import quote_plus
from dateutil import parser as dateparser
from pathlib import Path

# --- Config: Edit company list & tickers as desired ---
COMPANIES = [
    {"name": "Apple", "ticker": "AAPL"},
    {"name": "Microsoft", "ticker": "MSFT"},
    {"name": "Alphabet", "ticker": "GOOGL"},
    {"name": "Amazon", "ticker": "AMZN"},
    {"name": "Meta", "ticker": "META"},
    {"name": "NVIDIA", "ticker": "NVDA"},
    {"name": "Johnson & Johnson", "ticker": "JNJ"},
    {"name": "Vertex Pharmaceuticals", "ticker": "VRTX"},
    {"name": "Insilico Medicine", "ticker": None},
    {"name": "Amgen", "ticker": "AMGN"},
    {"name": "Alcon", "ticker": "ALC"},
    {"name": "TCS", "ticker": "TCS.NS"},
    {"name": "SBI", "ticker": "SBIN.NS"},
    {"name": "Infosys", "ticker": "INFY"},
    {"name": "IDFC First Bank", "ticker": "IDFCFIRSTB.NS"},
    {"name": "Yes Bank", "ticker": "YESBANK.NS"},
    {"name": "Torrent Pharamceuticals", "ticker": "TORNTPHARM.NS"},
    {"name": "Mahindra & Mahindra", "ticker": "M&M.NS"}
]

DATA_DIR = Path("frontend/public/data")
DATA_DIR.mkdir(exist_ok=True)

# --- Helpers ---
def slugify(name: str) -> str:
    s = name.lower().replace("&", "and").replace(" ", "-")
    return "".join(ch for ch in s if (ch.isalnum() or ch == "-"))

def now_iso():
    return datetime.now(timezone.utc).isoformat()

# Google News RSS search helper
def google_news_rss_query(q: str, max_items=8):
    # Google News RSS search endpoint
    url = f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"
    # feedparser will fetch and parse
    d = feedparser.parse(url)
    items = []
    for entry in d.entries[:max_items]:
        published = None
        if hasattr(entry, "published"):
            try:
                published = dateparser.parse(entry.published).isoformat()
            except Exception:
                published = None
        items.append({
            "title": entry.get("title"),
            "link": entry.get("link"),
            "summary": entry.get("summary", None),
            "published": published,
            "source": entry.get("source", {}).get("title", None)
        })
    return items

# Stock data helper via yfinance
def fetch_stock(ticker: str):
    if not ticker:
        return None
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="7d", interval="1d", actions=False)
        # compress to simple list of {date, close}
        prices = []
        for idx, row in hist.iterrows():
            prices.append({"date": idx.strftime("%Y-%m-%d"), "close": float(row['Close'])})
        info = t.info if hasattr(t, "info") else {}
        latest = prices[-1] if prices else None
        return {
            "ticker": ticker,
            "currency": info.get("currency"),
            "latest": latest,
            "history": prices,
            "name": info.get("shortName") or info.get("longName"),
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

# Product-launch heuristic: search Google News for "company product launch"
def fetch_product_launches(company_name: str, max_items=5):
    query = f'{company_name} product launch OR launches OR "new product" OR "launches"'
    return google_news_rss_query(query, max_items=max_items)

# Main loop
def build_company_payload(company):
    name = company["name"]
    ticker = company.get("ticker")
    print(f"[{now_iso()}] Fetching: {name}")
    # 1) Top news for company
    news = google_news_rss_query(name, max_items=8)
    time.sleep(0.5)
    # 2) Product-related items
    products = fetch_product_launches(name, max_items=5)
    time.sleep(0.5)
    # 3) Stock
    stock = fetch_stock(ticker) if ticker else None
    payload = {
        "name": name,
        "slug": slugify(name),
        "ticker": ticker,
        "fetched_at": now_iso(),
        "news": news,
        "product_launches": products,
        "stock": stock
    }
    return payload

def main():
    companies_out = []
    for c in COMPANIES:
        try:
            payload = build_company_payload(c)
            companies_out.append({
                "name": payload["name"],
                "slug": payload["slug"],
                "ticker": payload["ticker"],
                "last_updated": payload["fetched_at"]
            })
            # write per-company file
            fpath = DATA_DIR / f"{payload['slug']}.json"
            with open(fpath, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
            print(f"  wrote {fpath}")
        except Exception as e:
            print("ERROR for", c.get("name"), e)
    # write master companies.json
    meta = {"generated_at": now_iso(), "companies": companies_out}
    with open(DATA_DIR / "companies.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    print("All done.")

if __name__ == "__main__":
    main()