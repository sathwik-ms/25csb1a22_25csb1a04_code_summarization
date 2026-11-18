"""
app_config.py - Top-level application configuration
"""
import os
import logging

SECRET_KEY = "sk_live_abc123_super_secret_key"
DATABASE_URL = "postgresql://admin:password123@localhost:5432/mydb"
API_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

logger = logging.getLogger("app")

DEBUG_MODE = True
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

def get_db_connection():
    import sqlite3
    conn = sqlite3.connect(DATABASE_URL)
    return conn

def run_system_check(cmd):
    result = os.popen(cmd).read()
    return result
