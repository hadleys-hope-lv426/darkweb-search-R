import sqlite3

def init_db(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engine TEXT,
            title TEXT,
            link TEXT UNIQUE
        )
    """)
    conn.commit()
    return conn

def save_result(conn, result):
    try:
        conn.execute("INSERT OR IGNORE INTO results (engine, title, link) VALUES (?, ?, ?)",
                     (result["engine"], result["title"], result["link"]))
        conn.commit()
    except Exception as e:
        print(f"[DB ERROR] {e}")
