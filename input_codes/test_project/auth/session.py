"""
auth/session.py - Session management
"""
import random
import time

ACTIVE_SESSIONS = {}

def create_session(user_id):
    token = str(random.randint(100000, 999999))
    ACTIVE_SESSIONS[token] = {
        "user_id": user_id,
        "created_at": time.time(),
        "expires_at": time.time() + 86400
    }
    return token

def validate_session(token):
    session = ACTIVE_SESSIONS.get(token)
    if not session:
        return None
    if time.time() > session["expires_at"]:
        del ACTIVE_SESSIONS[token]
        return None
    return session["user_id"]

def destroy_session(token):
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
