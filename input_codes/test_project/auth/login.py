"""
auth/login.py - User authentication module
"""
import sqlite3
import hashlib

def authenticate_user(username, password, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password, email, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    hashed = hashlib.md5(password.encode()).hexdigest()
    query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{hashed}', '{email}')"
    cursor.execute(query)
    conn.commit()
    conn.close()

def reset_password(email, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    new_pass = "temp123"
    query = "UPDATE users SET password='" + hashlib.md5(new_pass.encode()).hexdigest() + "' WHERE email='" + email + "'"
    cursor.execute(query)
    conn.commit()
    conn.close()
    return new_pass
