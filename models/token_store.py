import json
import os
import threading

TOKENS_FILE = os.getenv("TOKENS_FILE", "tokens.json")
USER_MAP_FILE = os.getenv("USER_MAP_FILE", "user_map.json")
_lock = threading.Lock()

def save_token(slack_user_id: str, token: str, gpt_user_id: str = None):
    with _lock:
        # Save token
        tokens = load_all_tokens()
        tokens[slack_user_id] = token
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f)

        # Map GPT user to Slack user
        if gpt_user_id:
            user_map = load_user_map()
            user_map[gpt_user_id] = slack_user_id
            with open(USER_MAP_FILE, "w") as f:
                json.dump(user_map, f)

        print(f"✅ Saved token for Slack user {slack_user_id}")
        if gpt_user_id:
            print(f"🔗 Linked GPT user {gpt_user_id} → Slack user {slack_user_id}")

def get_token_by_gpt_user(gpt_user_id: str):
    user_map = load_user_map()
    slack_user_id = user_map.get(gpt_user_id)
    if not slack_user_id:
        print(f"⚠️ No Slack user mapped for GPT user {gpt_user_id}")
        return None
    return get_token(slack_user_id)

def get_token(slack_user_id: str):
    return load_all_tokens().get(slack_user_id)

def load_all_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)

def load_user_map():
    if not os.path.exists(USER_MAP_FILE):
        return {}
    with open(USER_MAP_FILE, "r") as f:
        return json.load(f)
