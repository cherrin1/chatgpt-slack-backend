from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx
from models.token_store import (
    get_token_by_gpt_user,
    load_user_map,
    get_secret
)

router = APIRouter()

@router.get("/slack/status")
async def slack_status(
    user_id: str = Query(...),
    secret: str = Query(...)
):
    # ✅ Validate the user's secret
    stored_secret = get_secret(user_id)
    if not stored_secret or stored_secret != secret:
        return JSONResponse({
            "ok": False,
            "connected": False,
            "message": "Invalid or missing secret. Please verify your identity."
        })

    # ✅ Lookup Slack user ID
    user_map = load_user_map()
    slack_user_id = user_map.get(user_id)

    if not slack_user_id:
        return JSONResponse({
            "ok": False,
            "connected": False,
            "message": "GPT user is not linked to any Slack account.",
            "auth_url": f"/oauth/start?gpt_user_id={user_id}"
        })

    # ✅ Check token
    token = get_token_by_gpt_user(user_id)
    if not token:
        return JSONResponse({
            "ok": False,
            "connected": False,
            "slack_user_id": slack_user_id,
            "message": "Slack user found but token is missing or expired.",
            "auth_url": f"/oauth/start?gpt_user_id={user_id}"
        })

    # ✅ Optionally fetch Slack username
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
