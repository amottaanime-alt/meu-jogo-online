import sqlite3
import hashlib

DB_NAME = "game.db"


def get_conn():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        x REAL DEFAULT 100,
        y REAL DEFAULT 100
    )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register(username, password):
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login(username, password):
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "SELECT id, x, y FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    result = c.fetchone()
    conn.close()

    if result:
        return {
            "id": str(result[0]),
            "x": result[1],
            "y": result[2]
        }

    return None


def save_position(player_id, x, y):
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "UPDATE users SET x=?, y=? WHERE id=?",
        (x, y, player_id)
    )

    conn.commit()
    conn.close()
