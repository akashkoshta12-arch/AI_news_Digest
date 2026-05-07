import feedparser

def get_arxiv_news():
    feed = feedparser.parse("http://export.arxiv.org/rss/cs.AI")

    data = []
    for entry in feed.entries[:5]:
        data.append({
            "title": entry.title,
            "content": entry.summary,
            "link": entry.link
        })

    return data