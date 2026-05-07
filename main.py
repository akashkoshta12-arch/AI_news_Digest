from fetch.github import get_github_news
from fetch.arxiv import get_arxiv_news
from fetch.news import get_web_news

from utils.summarizer import summarize
from utils.formatter import format_news_html
from utils.emailer import send_email


def main():
    print("🚀 Fetching news...")

    news = []
    news += get_github_news()
    news += get_arxiv_news()
    news += get_web_news()

    print("✂️ Summarizing...")

    data = []

    for n in news[:10]:
        try:
            summary = summarize(n)

            data.append({
                "title": n.split(":")[0],
                "content": summary,
                "source": "AI News"
            })

        except Exception as e:
            print("❌ Error:", e)

    print("🧾 Formatting...")

    final_content = format_news_html(data)

    print("📧 Sending email...")
    send_email(final_content, ["your_email@gmail.com"])

    print("✅ Done!")


if __name__ == "__main__":
    main()