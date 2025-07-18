from fastapi import APIRouter
from models.token_store import get_token_by_gpt_user
import httpx

router = APIRouter()

@router.post("/slack/upload-file")
async def share_remote_file(payload: dict):
    user_id = payload["user_id"]
    channel = payload["channel"]
    file_url = payload["file_url"]
    title = payload.get("title", "Shared file")

    token = get_token_by_gpt_user(user_id)
    if not token:
        return {"ok": False, "error": "User not authorized"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://slack.com/api/files.remote.share",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "external_url": file_url,
                "title": title,
                "channels": channel
            }
        )

    return resp.json()
