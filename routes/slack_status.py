from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx
from models.token_store import get_token_by_gpt_user, load_user_map

router = APIRouter()

@router.get("/slack/status")
async def slack_status(user_id: str = Query(...)):
    user_map = load_user_map()
    slack_user_id = user_map.get(user_id)

    if not slack_user_id:
        return JSONResponse({
            "ok": False,
            "connected": False,
            "message": "GPT user is not linked to any Slack account.",
            "auth_url": f"/oauth/start?gpt_user_id={user_id}"
        })

    token = get_token_by_gpt_user(user_id)
    if not token:
        return JSONResponse({
            "ok": False,
            "connected": False,
            "message": "Slack user found but token is missing or expired.",
            "slack_user_id": slack_user_id,
            "auth_url": f"/oauth/start?gpt_user_id={user_id}"
        })

    # ✅ Fetch Slack username from Slack API
    async with httpx.AsyncClient() as client:
        user_info = await client.get(
            "https://slack.com/api/users.info",
            headers={"Authorization": f"Bearer {token}"},
            params={"user": slack_user_id}
        )

    data = user_info.json()
    slack_username = data.get("user", {}).get("name", "unknown")

    return JSONResponse({
        "ok": True,
        "connected": True,
        "gpt_user_id": user_id,
        "slack_user_id": slack_user_id,
        "slack_username": slack_username,
        "message": f"User is connected to Slack as @{slack_username}."
    })
