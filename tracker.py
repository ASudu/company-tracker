import feedparser, requests, json, datetime
from urllib.parse import quote_plus

def get_news_articles(company_name, limit=3):
    rss_url = f"https://news.google.com/rss/search?q={quote_plus(company_name)}"
    feed = feedparser.parse(rss_url)
    return [
        {"title": e.title, "link": e.link, "date": e.published}
        for e in feed.entries[:limit]
    ]

def get_blog_updates(blog_rss, limit=3):
    feed = feedparser.parse(blog_rss)
    return [
        {"title": e.title, "link": e.link, "date": e.published}
        for e in feed.entries[:limit]
    ]

def get_github_commits(repo, limit=3):
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {"Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return [{"title": f"❌ Failed to fetch: {r.status_code}", "link": "#", "date": ""}]
    commits = r.json()[:limit]
    return [
        {
            "title": c['commit']['message'].split('\n')[0][:80] + "...",
            "link": c['html_url'],
            "date": c['commit']['author']['date']
        }
        for c in commits
    ]

def format_entries(entries):
    return "<ul>" + "".join(
        f"<li><a href='{e['link']}' target='_blank'>{e['title']}</a> <em>({e['date']})</em></li>"
        for e in entries
    ) + "</ul>"

def track_company(c):
    output = [f"<details class='company-block'><summary><h2>📊 Updates for {c['name']}</h2></summary>"]

    output.append("<h3>🗞️ News</h3>")
    output.append(format_entries(get_news_articles(c['name'])))

    if c.get("blog_rss"):
        output.append("<h3>📝 Blog</h3>")
        output.append(format_entries(get_blog_updates(c['blog_rss'])))

    if c.get("github_repo"):
        output.append("<h3>💻 GitHub</h3>")
        output.append(format_entries(get_github_commits(c['github_repo'])))

    output.append("</details>")
    return "\n".join(output)

# ========== MAIN SCRIPT ==========
if __name__ == "__main__":
    with open("companies.json") as f:
        companies = json.load(f)

    date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"📅 Tracking started: {date}")

    html_header = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Company Tracker</title>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; margin: 2em; background: #f9f9f9; }}
            h1 {{ color: #333; }}
            h2 {{ color: #004aad; margin-top: 2em; }}
            h3 {{ color: #666; margin-bottom: 0.3em; }}
            a {{ color: #0077cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            ul {{ padding-left: 1.2em; }}
            .company-block {{ margin-bottom: 2em; padding-bottom: 1em; border-bottom: 1px solid #ccc; }}
            details summary {
                cursor: pointer;
            }

            details summary h2 {
                display: inline;
                font-size: 1.4em;
                color: #004aad;
            }

            details[open] summary::after {
                content: " 🔽";
            }

            details summary::after {
                content: " ▶";
            }
        </style>
    </head>
    <body>
    <h1>📈 Company Tracker</h1>
    <p><strong>Last updated:</strong> {date}</p>
    """
    html_header = html_header.replace("{date}", date)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_header)

        for company in companies:
            html_block = track_company(company)
            f.write(f"<div class='company-block'>{html_block}</div>")

        f.write("</body></html>")

    print("✅ Tracking completed. Output saved to index.html")