import json, os

TOKENS_FILE = "tokens.json"
USER_MAP_FILE = "user_map.json"
SECRETS_FILE = "secrets.json"

def save_secret(user_id, secret):
    data = load_all_secrets()
    data[user_id] = secret
    with open(SECRETS_FILE, "w") as f:
        json.dump(data, f)

def get_secret(user_id):
    return load_all_secrets().get(user_id)

def load_all_secrets():
    if not os.path.exists(SECRETS_FILE):
        return {}
    with open(SECRETS_FILE, "r") as f:
        return json.load(f)
        
def save_token(slack_user_id, token, gpt_user_id):
    tokens = load_all_tokens()
    user_map = load_user_map()
    tokens[slack_user_id] = token
    user_map[gpt_user_id] = slack_user_id
    save_all_tokens(tokens)
    save_user_map(user_map)
    print(f"✅ Saved token for Slack user {slack_user_id}")
    print(f"🔗 Linked GPT user {gpt_user_id} → Slack user {slack_user_id}")

def get_token(slack_user_id):
    return load_all_tokens().get(slack_user_id)

def get_token_by_gpt_user(gpt_user_id):
    slack_id = load_user_map().get(gpt_user_id)
    if not slack_id:
        return None
    return get_token(slack_id)

def load_all_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)

def save_all_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f)

def load_user_map():
    if not os.path.exists(USER_MAP_FILE):
        return {}
    with open(USER_MAP_FILE, "r") as f:
        return json.load(f)

def save_user_map(data):
    with open(USER_MAP_FILE, "w") as f:
        json.dump(data, f)
