from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from models.token_store import get_token_by_gpt_user
import httpx

router = APIRouter()

@router.get("/slack/users")
async def get_users(user_id: str = Query(...)):
    token = get_token_by_gpt_user(user_id)
    if not token:
        return JSONResponse({"ok": False, "error": "User not connected"}, status_code=401)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://slack.com/api/users.list",
            headers={"Authorization": f"Bearer {token}"}
        )

    data = resp.json()
    if not data.get("ok"):
        return JSONResponse({"ok": False, "error": data.get("error", "Unknown error")}, status_code=500)

    simplified_users = [
        {
            "id": user["id"],
            "name": user["name"],
            "real_name": user.get("real_name"),
            "display_name": user.get("profile", {}).get("display_name"),
            "is_bot": user.get("is_bot", False),
        }
        for user in data.get("members", [])
        if not user.get("deleted", False)
    ]

    return {"ok": True, "users": simplified_users}
