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


# =========================
# REGISTER
# =========================
def register(username, password):
    print("🧾 REGISTER RAW:", username, password)

    if not username or not password:
        print("❌ EMPTY DATA")
        return False

    conn = get_conn()
    c = conn.cursor()

    try:
        username = username.strip()
        password = password.strip()

        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )

        conn.commit()
        print("✔ REGISTER OK")
        return True

    except Exception as e:
        print("❌ REGISTER ERROR:", repr(e))
        return False

    finally:
        conn.close()


# =========================
# LOGIN
# =========================
def login(username, password):
    print("🔍 LOGIN TRY:", username, password)

    if not username or not password:
        print("❌ EMPTY LOGIN DATA")
        return None

    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "SELECT id, x, y FROM users WHERE username=? AND password=?",
        (username.strip(), hash_password(password.strip()))
    )

    result = c.fetchone()
    conn.close()

    print("📦 LOGIN RESULT:", result)

    if result:
        return {
            "id": str(result[0]),
            "x": result[1],
            "y": result[2]
        }

    return None


# =========================
# SAVE POSITION
# =========================
def save_position(player_id, x, y):
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "UPDATE users SET x=?, y=? WHERE id=?",
        (x, y, player_id)
    )

    conn.commit()
    conn.close()
