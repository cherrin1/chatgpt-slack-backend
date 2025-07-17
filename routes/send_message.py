from fastapi import APIRouter
from models.token_store import get_token_by_gpt_user
from utils.slack_api import slack_post

router = APIRouter()

@router.post("/slack/send-message")
async def send_message(payload: dict):
    token = get_token_by_gpt_user(payload["user_id"])
    if not token:
        return {"error": "User not authorized"}
    response = await slack_post("chat.postMessage", token, {
        "channel": payload["channel"],
        "text": payload["text"]
    })
    return response
