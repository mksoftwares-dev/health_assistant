import sqlite3
import bcrypt
import streamlit as st

DB = "history.db"

# ── Create users table ────────────────────────────────────
def init_users_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            created_at TEXT
        )
    ''')

    # Add user_id column to history if not exists
    try:
        c.execute("ALTER TABLE history ADD COLUMN user_id INTEGER")
    except:
        pass

    conn.commit()
    conn.close()

# ── Register ──────────────────────────────────────────────
def register_user(username, email, password, age, gender):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        from datetime import datetime
        c.execute('''
            INSERT INTO users (username, email, password, age, gender, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            username.strip(),
            email.strip(),
            hashed.decode("utf-8"),
            age,
            gender,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return True, "✅ Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "❌ Username already taken!"
        elif "email" in str(e):
            return False, "❌ Email already registered!"
        return False, "❌ Registration failed!"
    finally:
        conn.close()

# ── Login ─────────────────────────────────────────────────
def login_user(username, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    user = c.fetchone()
    conn.close()

    if user is None:
        return False, None, "❌ Username not found!"

    stored_password = user[3]
    if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
        return True, {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "age": user[4],
            "gender": user[5],
            "created_at": user[6]
        }, "✅ Login successful!"
    else:
        return False, None, "❌ Incorrect password!"

# ── Get user by id ────────────────────────────────────────
def get_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "age": user[4],
            "gender": user[5],
            "created_at": user[6]
        }
    return None

# ── Update profile ────────────────────────────────────────
def update_profile(user_id, age, gender):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        UPDATE users SET age = ?, gender = ? WHERE id = ?
    ''', (age, gender, user_id))
    conn.commit()
    conn.close()

# ── Session helpers ───────────────────────────────────────
def is_logged_in():
    return "user" in st.session_state and st.session_state.user is not None

def logout():
    st.session_state.user = None
    st.session_state.page = "login"
    for key in ["chat_step", "chat_answers", "chat_messages", "chat_done"]:
        if key in st.session_state:
            del st.session_state[key]
# ── Delete user ───────────────────────────────────────────
def delete_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    c.execute("DELETE FROM history WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()