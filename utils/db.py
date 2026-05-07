import sqlite3

DB_NAME = "news.db"


# ✅ Create DB + Table
def init_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        source TEXT,
        link TEXT,
        category TEXT,
        score INTEGER
    )
    """)

    conn.commit()
    conn.close()


# ✅ Save news
def save_news(news_list):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    # old news delete
    cursor.execute("DELETE FROM news")

    for news in news_list:

        cursor.execute("""
        INSERT INTO news
        (title, content, source, link, category, score)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            news["title"],
            news["content"],
            news["source"],
            news["link"],
            news["category"],
            news["score"]
        ))

    conn.commit()
    conn.close()


# ✅ Load news
def get_news():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT title, content, source, link, category, score
    FROM news
    ORDER BY score DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append({
            "title": row[0],
            "content": row[1],
            "source": row[2],
            "link": row[3],
            "category": row[4],
            "score": row[5]
        })

    return data