from flask import Flask, render_template_string, request, redirect

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
from utils.db import init_db, save_news, get_news, clear_news
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
init_db()
clear_news()

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
<head>
<title>AI News Dashboard</title>

<style>

body{
    margin:0;
    padding:0;
    font-family:Arial;
    background:#f1f5f9;
}

/* HEADER */
.header{
    background:linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
    padding:25px;
    text-align:center;
    box-shadow:0 4px 15px rgba(0,0,0,0.2);
}

.header h1{
    margin:0;
    font-size:38px;
}

/* MAIN LAYOUT */
.container{
    display:flex;
    gap:20px;
    padding:20px;
}

/* LEFT SECTION */
.left{
    width:70%;
}

/* RIGHT SECTION */
.right{
    width:30%;
}

/* CARD */
.card{
position:relative;
overflow:hidden;


background:white;
padding:20px;
margin-bottom:20px;
border-radius:16px;

box-shadow:
    0 4px 12px rgba(0,0,0,0.08),
    inset 0 0 80px rgba(0,0,0,0.02);

transition:0.3s;

border:1px solid rgba(0,0,0,0.05);


}

/* Background watermark effect */
.card::before{
content:"";


position:absolute;
top:50%;
left:50%;

transform:translate(-50%,-50%) rotate(-20deg);

font-size:70px;
font-weight:bold;

color:rgba(0,0,0,0.03);

white-space:nowrap;

pointer-events:none;


}

/* Hover effect */
.card:hover{
transform:translateY(-6px);


box-shadow:
    0 10px 25px rgba(0,0,0,0.15),
    inset 0 0 100px rgba(0,0,0,0.03);


}
.watermark{
position:absolute;


top:50%;
left:50%;
bottom:30%;
transform:translate(-50%,-50%) rotate(-25deg);

font-size:80px;
font-weight:bold;

color:#24252714;

pointer-events:none;

white-space:nowrap;


}


/* BUTTONS */
.btn{
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    color:white;
    border:none;
    padding:12px 18px;
    border-radius:10px;
    cursor:pointer;
    font-size:15px;
    transition:0.3s;
    font-weight:bold;
}

.btn:hover{
    opacity:0.9;
    transform:scale(1.03);
}

/* GENERATE BUTTON */
.generate-btn{
    background:linear-gradient(135deg,#10b981,#059669);
}

/* THOUGHT BOX */
.thought{
    background:linear-gradient(135deg,#fef3c7,#fde68a);
    border-left:6px solid #f59e0b;
}

/* CATEGORY */
.badge{
    display:inline-block;
    background:#dbeafe;
    color:#1d4ed8;
    padding:5px 10px;
    border-radius:20px;
    font-size:12px;
    font-weight:bold;
}

/* SCORE */
.score{
    color:#f59e0b;
    font-weight:bold;
}

/* LINKS */
a{
    color:#2563eb;
    text-decoration:none;
    font-weight:bold;
}

a:hover{
    text-decoration:underline;
}

/* TEXTAREA */
textarea{
    width:100%;
    height:120px;
    padding:12px;
    border-radius:10px;
    border:1px solid #cbd5e1;
    font-size:14px;
    resize:none;
    outline:none;
}

textarea:focus{
    border:1px solid #2563eb;
    box-shadow:0 0 8px rgba(37,99,235,0.3);
}

/* RESPONSIVE */
@media(max-width:900px){

    .container{
        flex-direction:column;
    }

    .left,
    .right{
        width:100%;
    }
}

</style>

</head>

<body>

<div class="header">
    <h1>🧠 AI News Dashboard</h1>
    <p>Latest AI Research, Tools & Tech Updates</p>
</div>

<div class="container">


<!-- LEFT -->
<div class="left">

    <a href="/generate">
        <button class="btn generate-btn">
            🚀 Generate News
        </button>
    </a>

    <br><br>

    <!-- Thought -->
    <div class="card thought">
        <h3>💡 Thought of the Day</h3>
        <p>{{thought}}</p>
    </div>

    <!-- NEWS -->
    {% for n in data %}

    <div class="card">
    <div class="watermark"> {{n.source}} </div>

        <h2>{{n.title}}</h2>

        <p>
            <span class="badge">
                🏷️ {{n.category}}
            </span>

            &nbsp;

            <span class="score">
                ⭐ {{n.score}}/10
            </span>
        </p>

        <p style="line-height:1.7;">
            {{n.content}}
        </p>

        <p>
            🔗 
            <a href="{{n.link}}" target="_blank">
                {{n.source}}
            </a>
        </p>

    </div>

    {% endfor %}

</div>

<!-- RIGHT -->
<div class="right">

    <div class="card">

        <h2>📧 Send Newsletter</h2>

        <form method="POST">

            <textarea
                name="emails"
                placeholder="Enter emails separated by commas">
            </textarea>

            <br><br>

            <button type="submit" class="btn">
                📩 Send Newsletter
            </button>

        </form>

    </div>

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
