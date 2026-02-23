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
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

async def add_drink(user_id, username, drink_type="beer"):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO drinks (user_id, username, drink_type, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, drink_type, datetime.now()))
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
