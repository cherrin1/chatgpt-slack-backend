from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
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

    return JSONResponse({
        "ok": True,
        "connected": True,
        "gpt_user_id": user_id,
        "slack_user_id": slack_user_id,
        "message": "User is connected to Slack."
    })
