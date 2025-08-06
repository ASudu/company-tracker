# Company Tracker 🕵️

This GitHub Action tracks:

- Latest Google News mentions
- GitHub commits
- Company blog posts (via RSS)

## How it works

- Runs daily at 12 PM UTC
- Prints updates to the GitHub Actions logs

## Configuration

Edit `tracker.py` to change:
- `COMPANY_NAME`
- `GITHUB_REPO`
- `BLOG_RSS_FEED`
