import os
import httpx
from fastapi import APIRouter
from models.token_store import save_token

router = APIRouter()

@router.get("/oauth/start")
async def start_oauth():
    return {
        "url": f"https://slack.com/oauth/v2/authorize?client_id={os.getenv('SLACK_CLIENT_ID')}&scope=chat:write,conversations.read&user_scope=users:read&redirect_uri={os.getenv('SLACK_REDIRECT_URI')}"
    }

@router.get("/oauth/callback")
async def oauth_callback(code: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://slack.com/api/oauth.v2.access", data={
            "client_id": os.getenv("SLACK_CLIENT_ID"),
            "client_secret": os.getenv("SLACK_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": os.getenv("SLACK_REDIRECT_URI")
        })

    data = resp.json()
    if data.get("ok"):
        user_id = data["authed_user"]["id"]
        token = data["access_token"]
        save_token(user_id, token)
        return {"message": "Slack connected!", "user_id": user_id}
    return {"error": data}
