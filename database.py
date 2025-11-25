import sqlite3
from datetime import datetime

DB_NAME = "beer_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            drink_type TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def add_drink(user_id, username, drink_type="beer"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO drinks (user_id, username, drink_type, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, drink_type, datetime.now()))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM drinks WHERE user_id = ?
    ''', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count
