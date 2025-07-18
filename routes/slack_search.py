from fastapi import APIRouter
from models.token_store import get_token_by_gpt_user
from utils.slack_api import slack_post

router = APIRouter()

@router.get("/slack/search")
async def search_slack(user_id: str = Query(...), secret: str = Query(...), query: str = Query(...), page: int = 1):
    token = get_token_by_gpt_user(user_id, secret)
    if not token:
        return {"ok": False, "error": "Unauthorized"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://slack.com/api/search.all",
            headers={"Authorization": f"Bearer {token}"},
            params={"query": query, "page": page, "count": 100}
        )

    return resp.json()
