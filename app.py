from flask import Flask, render_template, render_template_string, request, redirect
import os
from flask import session

from utils.formatter import format_news_html_pro
from utils.ranker import rank_news
from utils.thought import generate_thought
# from utils.formatter import format_news_pro
from fetch.github import get_github_news
from fetch.arxiv import get_arxiv_news
from fetch.news import get_web_news
from utils.summarizer import summarize
from utils.emailer import send_email
from utils.db import (init_db,save_news,get_news,get_archive_dates,get_news_by_date,clear_news)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "akki_ai_news_secret"

# Initialize database and clear existing news on startup
init_db()
# clear_news() # Optional: Remove this if you want to keep data across restarts

# Data storage configuration
DATA_FILE = "data/news.json"
os.makedirs("data", exist_ok=True)

# Function to aggregate and process news from multiple sources
def generate_news():
    results = []

    # Fetching from GitHub
    for n in get_github_news():
        results.append({"text": n, "source": "GitHub"})

    # Fetching from arXiv
    for n in get_arxiv_news():
        results.append({"text": n, "source": "arXiv"})

    # Fetching from Web
    for n in get_web_news():
        results.append({"text": n, "source": "Web"})

    final = []
    category_map = {"GitHub": "Tools", "arXiv": "Research", "Web": "News"}

    # Process first 15 items
    for item in results[:20]:
        try:
            title = item["text"].get("title", "No Title")
            content_raw = item["text"].get("content", "")

            # Summarize and Rank news content
            summary = summarize(content_raw)
            score = rank_news(content_raw)

            final.append({
                "title": title,
                "content": str(summary),
                "source": item["source"],
                "link": item["text"].get("link", "#"),
                "category": category_map[item["source"]],
                "score": score,
            })
        except Exception as e:
            print(f"Error processing news item: {e}")

    # Sort news by score in descending order
    final = sorted(final, key=lambda x: x["score"], reverse=True)

    # Persist processed news to database
    save_news(final)
    return final

# Main UI Route
@app.route("/", methods=["GET", "POST"])
def home():
    # Fetch archive dates for the sidebar
    archive_dates = get_archive_dates()
    thought = generate_thought()
    selected_date = request.args.get("date")
    
    # --- HANDLE POST REQUEST (Email Sending) ---
    if request.method == "POST":
        emails = request.form.get("emails")
        
        # Get current news data for the email
        current_news_data = get_news()
        email_content = format_news_html_pro(current_news_data, thought)

        # Create list of emails from comma-separated input
        emails_list = [e.strip() for e in emails.split(",") if e.strip()]

        if not emails_list:
            print("No emails provided")
            return redirect("/")

        # Send email via utility function
        send_email(email_content, emails_list)
        return redirect("/")

    # --- HANDLE GET REQUEST (Display News) ---
    data = []

    # CASE 1: Display Archive based on selected date (Always works if date is clicked)
    if selected_date:
        data = get_news_by_date(selected_date)
    
    # CASE 2: Display latest generated feed ONLY if user just clicked "Generate"
    elif session.get("generated"):
        try:
            data = get_news()
            # Clear the flag after showing so it doesn't show on next fresh visit
            session.pop("generated", None) 
        except Exception as e:
            print(f"Error fetching news: {e}")
            data = []
            
    # NOTE: If neither case is met (fresh visit), data remains an empty list []

    # Default thought if generation fails
    current_thought = thought if thought else "Innovation distinguishes between a leader and a follower."

    html = """
    <html>
    <head>
        <title>AI News Dashboard</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: #f1f5f9;
            }

            /* HEADER */
            .header {
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: white;
                padding: 25px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }

            .container {
                display: flex;
                gap: 20px;
                padding: 20px;
            }

            .left { width: 70%; }
            .right { width: 30%; }

            /* MODERN GLASSY CARD SECTION */
            .card, .mini-card {
                position: relative;
                overflow: hidden;
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }

            .card::after, .mini-card::after {
                content: "";
                position: absolute;
                top: 0;
                left: -150%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    120deg, 
                    transparent, 
                    rgba(255, 255, 255, 0.6), 
                    transparent
                );
                transition: 0.6s;
            }

            .card:hover, .mini-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                background: rgba(255, 255, 255, 0.95);
            }

            .card:hover::after, .mini-card:hover::after {
                left: 150%;
            }

            .watermark {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-25deg);
                font-size: 80px;
                font-weight: bold;
                color: rgba(0, 0, 0, 0.03);
                pointer-events: none;
                white-space: nowrap;
            }

            .btn {
                background: linear-gradient(135deg, #2563eb, #1d4ed8);
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 10px;
                cursor: pointer;
                font-weight: bold;
                transition: 0.3s;
            }

            .btn:hover { transform: scale(1.05); }
            .generate-btn { background: linear-gradient(135deg, #10b981, #059669); }

            .thought {
                background: linear-gradient(135deg, #fef3c7, #fde68a);
                border-left: 6px solid #f59e0b;
            }

            .badge {
                background: #dbeafe;
                color: #1d4ed8;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }

            .mini-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 16px;
            }

            textarea {
                width: 100%; height: 120px; padding: 12px; border-radius: 10px;
                border: 1px solid #cbd5e1; outline: none;
            }

            .archive-item {
                background: white;
                padding: 14px;
                border-radius: 14px;
                margin-bottom: 12px;
                display: flex;
                justify-content: space-between;
                transition: 0.3s;
            }
            .archive-item:hover { background: #eff6ff; transform: translateX(5px); }

            @media(max-width:900px){ .container { flex-direction: column; } .left, .right { width: 100%; } }
        </style>
    </head>
    <body>

    <div class="header">
        <h1>🧠 AI News Dashboard</h1>
        <p>Latest AI Research, Tools & Tech Updates</p>
    </div>

    <div class="container">
        <div class="left">
            <a href="/generate"><button class="btn generate-btn">🚀 Generate News</button></a>
            <br><br>

            <div class="card thought">
                <h3>💡 Thought of the Day</h3>
                <p>{{thought}}</p>
            </div>

            {% if data %}
                {% if selected_date %}
                <div class="mini-grid">
                    {% for n in data %}
                    <div class="mini-card">
                        <div class="badge">{{n.source}}</div>
                        <h4 style="margin-top:10px;">{{n.title[:80]}}...</h4>
                        <p>⭐ {{n.score}}/10</p>
                        <a href="{{n.link}}" target="_blank" style="color:#2563eb; font-weight:bold; text-decoration:none;">Read →</a>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                    {% for n in data %}
                    <div class="card">
                        <div class="watermark">{{n.source}}</div>
                        <h2 style="position:relative; z-index:1;">{{n.title}}</h2>
                        <p style="position:relative; z-index:1;">
                            <span class="badge">🏷️ {{n.category}}</span>
                            <span style="color:#f59e0b; font-weight:bold; margin-left:10px;">⭐ {{n.score}}/10</span>
                        </p>
                        <p style="position:relative; z-index:1; color:#475569;">{{n.content}}</p>
                        <p style="position:relative; z-index:1;">
                            🔗 <a href="{{n.link}}" target="_blank" style="color:#2563eb; font-weight:bold; text-decoration:none;">{{n.source}}</a>
                        </p>
                    </div>
                    {% endfor %}
                {% endif %}
            {% else %}
                <div class="card">
                    <p style="text-align:center; color:#64748b;">No news to display. Click <b>Generate News</b> to fetch latest updates or select a date from the <b>Archive</b>.</p>
                </div>
            {% endif %}
        </div>

        <div class="right">
            <div class="card">
                <h2>📧 Send Newsletter</h2>
                <form method="POST">
                    <textarea name="emails" placeholder="Enter emails separated by commas"></textarea>
                    <br><br>
                    <button type="submit" class="btn" style="width:100%;">📩 Send Newsletter</button>
                </form>
            </div>

            <div class="card">
                <h2>📅 News Archive</h2>
                {% if archive_dates %}
                    {% for d in archive_dates %}
                    <a href="/?date={{d}}" style="text-decoration:none; color:inherit;">
                        <div class="archive-item">
                            <strong>{{d}}</strong>
                            <span style="color:#2563eb;">View →</span>
                        </div>
                    </a>
                    {% endfor %}
                {% else %}
                    <p style="color:#64748b; font-size:14px;">No archive available yet.</p>
                {% endif %}
            </div>
        </div>
    </div>

    </body>
    </html>
    """
    return render_template_string(html, data=data, thought=current_thought,
                                  archive_dates=archive_dates,
                                  selected_date=selected_date)

#  Generate route
@app.route("/generate")
def generate():
    latest_news = generate_news()
    if latest_news:
        save_news(latest_news)
    
    session["generated"] = True
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)