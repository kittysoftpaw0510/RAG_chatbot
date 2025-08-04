import sqlite3
from typing import Optional, List, Tuple
import os
from datetime import datetime

# DB_PATH = os.path.join(os.path.dirname(__file__), 'user_data.db')

PERSIST_DIR = os.getenv("PERSIST_DIR", ".\\sqlite")
# Ensure the directory exists
os.makedirs(PERSIST_DIR, exist_ok=True)
DB_PATH = os.path.join(PERSIST_DIR, "sqlite.db")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userid TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            is_public INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ingest_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            ingested_by TEXT NOT NULL,
            is_public INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()

######################################
# users
######################################

def add_user(userid: str, password: str, is_admin: int = 0) -> bool:
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (userid, password) VALUES (?, ?)', (userid, password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def delete_user(userid: str) -> bool:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE userid = ?', (userid,))
        conn.commit()
        return c.rowcount > 0

def authenticate_user(userid: str, password: str) -> bool:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE userid = ? AND password = ?', (userid, password))
        return c.fetchone() is not None

def update_user_password(userid: str, new_password: str) -> bool:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET password = ? WHERE userid = ?', (new_password, userid))
        conn.commit()
        return c.rowcount > 0

def get_all_users() -> list:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, userid, password FROM users')
        rows = c.fetchall()
        return [dict(id=row[0], userid=row[1], password=row[2]) for row in rows]

######################################
# pdfs
######################################

def add_pdf(filename: str, uploaded_by: str, is_global: int = 0, filepath: Optional[str] = None) -> int:
    if filepath is None:
        filepath = filename
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO pdfs (filename, filepath, uploaded_by, is_public, created_at) VALUES (?, ?, ?, ?, ?)',
                  (filename, filepath, uploaded_by, is_global, datetime.utcnow().isoformat()))
        conn.commit()
        return c.lastrowid

def get_pdfs_by_user(uploaded_by: str) -> list:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, filename, filepath, uploaded_by, is_public, created_at FROM pdfs WHERE uploaded_by = ?', (uploaded_by,))
        rows = c.fetchall()
        return [dict(id=row[0], filename=row[1], filepath=row[2], uploaded_by=row[3], is_public=row[4], created_at=row[5]) for row in rows]

def get_all_pdfs() -> list:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, filename, filepath, uploaded_by, is_public, created_at FROM pdfs')
        rows = c.fetchall()
        return [dict(id=row[0], filename=row[1], filepath=row[2], uploaded_by=row[3], is_public=row[4], created_at=row[5]) for row in rows]

def delete_pdf_by_filename(filename: str):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM pdfs WHERE filename = ?', (filename,))
        conn.commit()
        return c.rowcount > 0

def delete_pdf_by_id(id: str):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM pdfs WHERE id = ?', (id,))
        conn.commit()
        return c.rowcount > 0

def get_pdf_filepath_by_filename(filename: str) -> Optional[str]:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT filepath FROM pdfs WHERE filename = ?', (filename,))
        row = c.fetchone()
        return row[0] if row else None

######################################
# ingest_state
######################################

def ingest(pdf_filename: str, ingested_by: str, is_public: int):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO ingest_state (filename, ingested_by, is_public, created_at) VALUES (?, ?, ?, ?)',
                  (pdf_filename, ingested_by, is_public, datetime.utcnow().isoformat()))
        conn.commit()
        return c.lastrowid

def get_ingested_pdfs_by_user(ingested_by: str):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, filename, ingested_by, is_public, created_at FROM ingest_state WHERE ingested_by = ?', (ingested_by,))
        rows = c.fetchall()
        return [dict(id=row[0], filename=row[1], ingested_by=row[2], is_public=row[3], created_at=row[4]) for row in rows]

def get_all_ingested_pdfs():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, filename, ingested_by, is_public, created_at FROM ingest_state')
        rows = c.fetchall()
        return [dict(id=row[0], filename=row[1], ingested_by=row[2], is_public=row[3], created_at=row[4]) for row in rows]

def delete_ingested_pdf_by_filename(pdf_filename: str):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM ingest_state WHERE filename = ?', (pdf_filename,))
        conn.commit()
        return c.rowcount > 0

def delete_ingested_pdf_by_id(id: str):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM ingest_state WHERE id = ?', (id,))
        conn.commit()
        return c.rowcount > 0

######################################

if __name__ == "__main__":
    init_db() 