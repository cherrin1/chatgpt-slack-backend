from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx

from models.token_store import get_token_by_gpt_user

router = APIRouter()

@router.get("/slack/search")
async def search_slack(
    user_id: str = Query(...),
    query: str = Query(...),
    page: int = Query(1)
):
    token = get_token_by_gpt_user(user_id)
    if not token:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://slack.com/api/search.all",
            headers={"Authorization": f"Bearer {token}"},
            params={"query": query, "page": page, "count": 100}
        )

    data = resp.json()
    if not data.get("ok"):
        return JSONResponse(data, status_code=400)

    return JSONResponse(data)
