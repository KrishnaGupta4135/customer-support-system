import sqlite3
from pathlib import Path

DB_PATH = "db/chatbot.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    Path("db").mkdir(exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT
    )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.commit()
    seed_tools()
    conn.close()

def seed_tools():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tools")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    tools = [
        ("Search MCP", "Search the internet using MCP search server"),
        ("RAG Engine", "Query your documents using RAG"),
        ("YouTube MCP", "Ask questions about YouTube videos"),
        ("General LLM", "General conversational AI queries")
    ]

    cursor.executemany(
        "INSERT INTO tools (name, description) VALUES (?,?)", tools
    )

    conn.commit()
    conn.close()