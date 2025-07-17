import json
import os
import threading

# Allow token file path override via env
TOKENS_FILE = os.getenv("TOKENS_FILE", "tokens.json")

# Lock to prevent race conditions
_lock = threading.Lock()

def save_token(user_id: str, token: str):
    with _lock:
        data = load_all_tokens()
        data[user_id] = token
        with open(TOKENS_FILE, "w") as f:
            json.dump(data, f)
        print(f"✅ Token saved for {user_id}")

def get_token(user_id: str):
    data = load_all_tokens()
    token = data.get(user_id)
    if token:
        print(f"✅ Token retrieved for {user_id}")
    else:
        print(f"⚠️ No token found for {user_id}")
    return token

def load_all_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    try:
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Warning: tokens.json is malformed. Reinitializing.")
        return {}
