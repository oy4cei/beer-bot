import sqlite3
import aiosqlite
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
            timestamp DATETIME,
            ai_comment TEXT
        )
    ''')

    try:
        cursor.execute('ALTER TABLE drinks ADD COLUMN ai_comment TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()

async def add_drink(user_id, username, ai_comment=None, drink_type="beer"):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO drinks (user_id, username, ai_comment, drink_type, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, ai_comment, drink_type, datetime.now()))
        await db.commit()

async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COUNT(*) FROM drinks WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_top_users(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT username, COUNT(*) as count 
            FROM drinks 
            GROUP BY user_id 
            ORDER BY count DESC 
            LIMIT ?
        ''', (limit,)) as cursor:
            return await cursor.fetchall()

async def get_todays_comments(limit=20):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT ai_comment FROM drinks 
            WHERE date(timestamp) = date('now', 'localtime')
            AND ai_comment IS NOT NULL 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
