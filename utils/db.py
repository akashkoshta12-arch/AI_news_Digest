import sqlite3
from datetime import datetime
import uuid

DB_NAME = "news.db"

# CREATE DATABASE & TABLE
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
        score INTEGER,
        created_at TEXT,
        batch_id TEXT
    )
    """)
    conn.commit()
    conn.close()

# SAVE NEWS
def save_news(news_list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    batch_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for news in news_list:
        # Duplicate check: prevents saving the same title twice
        cursor.execute(
            "SELECT id FROM news WHERE title = ?", 
            (news["title"],)
        )
        
        existing_news = cursor.fetchone()
        
        if existing_news:
            continue  # Skip if title already exists
            
        cursor.execute("""
        INSERT INTO news 
        (
            title, 
            content, 
            source, 
            link, 
            category, 
            score, 
            created_at, 
            batch_id
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            news["title"], 
            news["content"], 
            news["source"], 
            news["link"], 
            news["category"], 
            news["score"], 
            created_at, 
            batch_id
        ))
    
    conn.commit()
    conn.close()

# LOAD LATEST NEWS (Updated to show last 20 items)
def get_news():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Added LIMIT 20 to ensure you see a consistent number of latest news
    cursor.execute("""
    SELECT 
        title, 
        content, 
        source, 
        link, 
        category, 
        score 
    FROM news 
    ORDER BY created_at DESC, score DESC
    LIMIT 20
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

# CLEAR NEWS
def clear_news():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news")
    conn.commit()
    conn.close()

# GET ARCHIVE DATES
def get_archive_dates():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT DISTINCT DATE(created_at) 
    FROM news 
    ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    dates = []
    for row in rows:
        dates.append(row[0])
    return dates

# GET NEWS BY DATE (Fetches all news for the selected date)
def get_news_by_date(selected_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        title, 
        content, 
        source, 
        link, 
        category, 
        score 
    FROM news 
    WHERE DATE(created_at) = ? 
    ORDER BY score DESC
    """, (selected_date,))
    
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

# INITIALIZE DB
init_db()