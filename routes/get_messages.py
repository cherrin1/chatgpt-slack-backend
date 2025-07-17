from fastapi import APIRouter, Query
from models.token_store import get_token_by_gpt_user
from utils.slack_api import slack_get

router = APIRouter()

@router.get("/slack/messages")
async def get_messages(user_id: str = Query(...), channel: str = Query(...), limit: int = 20):
    token = get_token_by_gpt_user(user_id)  # ✅ correct mapping via GPT user ID
    if not token:
        return {"error": "User not authorized"}

    response = await slack_get("conversations.history", token, {
        "channel": channel,
        "limit": limit
    })
    return response
