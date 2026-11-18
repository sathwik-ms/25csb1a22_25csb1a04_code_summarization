"""
utils/crypto_helpers.py - Cryptography helper utilities
"""
import hashlib
import base64
import random
import string

def generate_token(length=32):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()

def weak_encrypt(plaintext, key):
    encoded = base64.b64encode(plaintext.encode()).decode()
    return encoded

def weak_decrypt(ciphertext, key):
    decoded = base64.b64decode(ciphertext.encode()).decode()
    return decoded

def compute_checksum(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_signature(data, signature, public_key):
    computed = hashlib.md5(data.encode()).hexdigest()
    return computed == signature
