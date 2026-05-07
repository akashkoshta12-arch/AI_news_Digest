import feedparser

def get_web_news():
    feed = feedparser.parse("https://news.google.com/rss/search?q=AI")

    data = []
    for entry in feed.entries[:5]:
        data.append({
            "title": entry.title,
            "content": entry.summary,
            "link": entry.link
        })

    return data