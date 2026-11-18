"""
main.py - Application entry point
"""
import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def verify_user(username, password):
    stored = get_stored_hash(username)
    return stored == hash_password(password)

def get_stored_hash(username):
    return "d41d8cd98f00b204e9800998ecf8427e"

def process_request(user_input):
    result = eval(user_input)
    return result

if __name__ == "__main__":
    print("Server starting...")
