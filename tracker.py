import feedparser, requests, json, datetime
from urllib.parse import quote_plus

def get_news_articles(company_name, limit=3):
    rss_url = f"https://news.google.com/rss/search?q={quote_plus(company_name)}"
    feed = feedparser.parse(rss_url)
    return [f"- {e.title} ({e.published})\n  {e.link}" for e in feed.entries[:limit]]

def get_blog_updates(blog_rss, limit=3):
    feed = feedparser.parse(blog_rss)
    return [f"- {e.title} ({e.published})\n  {e.link}" for e in feed.entries[:limit]]

def get_github_commits(repo, limit=3):
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {"Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return [f"❌ Failed to fetch: {r.status_code}"]
    commits = r.json()[:limit]
    return [f"- {c['commit']['message'][:80]}... ({c['commit']['author']['date']})\n  {c['html_url']}" for c in commits]

def track_company(c):
    output = [f"\n📊 Updates for {c['name']}"]
    output.append("\n🗞️ News:")
    output += get_news_articles(c['name'])
    if c.get("blog_rss"):
        output.append("\n📝 Blog:")
        output += get_blog_updates(c['blog_rss'])
    if c.get("github_repo"):
        output.append("\n💻 GitHub:")
        output += get_github_commits(c['github_repo'])
    return "\n".join(output)

if __name__ == "__main__":
    with open("companies.json") as f:
        companies = json.load(f)

    date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"📅 Tracking started: {date}")

    with open("index.html", "w", encoding="utf-8") as f:
        output = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Company Tracker</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    margin: 2em;
                    background-color: #f7f9fc;
                    color: #111;
                }
                h1 {
                    color: #004080;
                }
                .company-block {
                    background: #fff;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    padding: 1em;
                    margin-bottom: 2em;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
                }
                .company-block pre {
                    white-space: pre-wrap;
                }
            </style>
        </head>
        <body>
        <h1>📈 Company Tracker</h1>
        <p><strong>Last updated:</strong> {}</p>
        """
        output = output.replace("{}", date)
        f.write(output)

        for company in companies:
            result = track_company(company)
            html_block = result.replace("\n", "<br>")
            f.write(f"<div class='company-block'><pre>{html_block}</pre></div>")

        f.write("</body></html>")

    print("✅ Tracking completed. Output saved to index.html")