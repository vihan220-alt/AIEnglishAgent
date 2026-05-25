import sqlite3

def init_db():
    conn = sqlite3.connect("coach_data.db")
    c = conn.cursor()
    # Ensure the table exists
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (room_id TEXT PRIMARY KEY, is_pinned INTEGER DEFAULT 0)''')
    # SAFELY add the missing column without crashing
    try:
        c.execute("ALTER TABLE conversations ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Column already exists, no action needed
    conn.commit()
    conn.close()

init_db()
