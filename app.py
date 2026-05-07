from flask import Flask, render_template_string, request, redirect
import json
import os
from utils.formatter import format_news_html_pro
from utils.ranker import rank_news
from utils.thought import generate_thought

# from utils.formatter import format_news_pro
from fetch.github import get_github_news
from fetch.arxiv import get_arxiv_news
from fetch.news import get_web_news
from utils.summarizer import summarize
from utils.emailer import send_email
from utils.db import init_db, save_news, get_news
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
init_db()

DATA_FILE = "data/news.json"
os.makedirs("data", exist_ok=True)


# 🔥 Generate News
def generate_news():
    results = []

    # GitHub
    for n in get_github_news():
        results.append({"text": n, "source": "GitHub"})

    # arXiv
    for n in get_arxiv_news():
        results.append({"text": n, "source": "arXiv"})

    # Web
    for n in get_web_news():
        results.append({"text": n, "source": "Web"})

    final = []

    category_map = {"GitHub": "Tools", "arXiv": "Research", "Web": "News"}

    for item in results[:15]:
        try:
            title = item["text"].get("title", "No Title")
            content_raw = item["text"].get("content", "")

            summary = summarize(content_raw)
            score = rank_news(content_raw)

            final.append(
                {
                    "title": title,
                    "content": str(summary),
                    "source": item["source"],
                    "link": item["text"].get("link", "#"),
                    "category": category_map[item["source"]],
                    "score": score,
                }
            )

        except Exception as e:
            print(e)

    final = sorted(final, key=lambda x: x["score"], reverse=True)

    save_news(final)
    return final


# 🌐 UI
@app.route("/", methods=["GET", "POST"])
def home():

    thought = generate_thought()

    if request.method == "POST":
        emails = request.form.get("emails")

        data = get_news()

        content = format_news_html_pro(data, thought)

        # ✅ emails list
        emails_list = [e.strip() for e in emails.split(",") if e.strip()]

        if not emails_list:
            print("No emails provided")
            return redirect("/")

        send_email(content, emails_list)

        return redirect("/")

    # ✅ GET request
    try:
        data = get_news()
    except:
        data = []

    html = """
    <html>
    <body style="font-family:Arial; background:#f4f6f8;">

    <div style="display:flex;">

    <!-- LEFT -->
    <div style="width:70%; padding:20px;">

        <h1>🧠 AI News Dashboard</h1>

        <a href="/generate">
            <button style="padding:10px; background:#2ecc71; color:white;">
                Generate News
            </button>
        </a>

        <div style="background:#fff3cd; padding:10px; border-radius:8px; margin:15px 0;">
            <h3>💡 Thought of the Day</h3>
            <p>{{thought}}</p>
        </div>

        {% for n in data %}
        <div style="background:white; padding:15px; margin:10px 0; border-radius:10px;">
            <h3>{{n.title}}</h3>

            <p><b>🏷️ {{n.category}}</b> | ⭐ {{n.score}}/10</p>
            <p>{{n.content}}</p>

            <small>
                🔗 <a href="{{n.link}}" target="_blank">
                    {{n.source}}
                </a>
            </small>
        </div>
        {% endfor %}

    </div>

    <!-- RIGHT -->
    <div style="width:30%; padding:20px; background:#ecf0f1;">

        <h3>📧 Send Email</h3>

        <form method="POST">
            <textarea name="emails" placeholder="Enter emails comma separated"
            style="width:100%; height:100px;"></textarea>

            <br><br>
            <button type="submit" style="padding:10px; background:#3498db; color:white;">
                Send Newsletter
            </button>
        </form>

    </div>

    </div>

    </body>
    </html>
    """

    return render_template_string(html, data=data, thought=thought)


# 🔄 Generate route
@app.route("/generate")
def generate():
    generate_news()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
