import json, os

TOKENS_FILE = "tokens.json"

def save_token(user_id, token):
    data = load_all_tokens()
    data[user_id] = token
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f)

def get_token(user_id):
    return load_all_tokens().get(user_id)

def load_all_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)
