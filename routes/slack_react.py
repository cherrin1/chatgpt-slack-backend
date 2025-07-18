from fastapi import APIRouter
from models.token_store import get_token_by_gpt_user
import httpx

router = APIRouter()

@router.post("/slack/react")
async def add_reaction(payload: dict):
    user_id = payload["user_id"]
    channel = payload["channel"]
    timestamp = payload["timestamp"]
    emoji = payload["emoji"]

    token = get_token_by_gpt_user(user_id)
    if not token:
        return {"ok": False, "error": "Unauthorized"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://slack.com/api/reactions.add",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "channel": channel,
                "timestamp": timestamp,
                "name": emoji
            }
        )

    return resp.json()
