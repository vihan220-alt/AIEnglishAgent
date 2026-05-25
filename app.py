def init_db():
    conn = sqlite3.connect("coach_data.db")
    c = conn.cursor()
    # 1. Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (room_id TEXT PRIMARY KEY, history_json TEXT, is_pinned INTEGER DEFAULT 0)''')
    
    # 2. Check if 'is_pinned' column exists, if not, add it
    try:
        c.execute("ALTER TABLE conversations ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Column already exists, proceed normally
    
    conn.commit()
    conn.close()
