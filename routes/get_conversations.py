from fastapi import APIRouter, Request
from models.token_store import get_token
from utils.slack_api import slack_get

router = APIRouter()

@router.get("/slack/conversations")
async def get_conversations(user_id: str):
    token = get_token(user_id)
    if not token:
        return {"error": "User not authorized"}
    response = await slack_get("conversations.list", token)
    return response
