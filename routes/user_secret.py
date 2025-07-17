from fastapi import APIRouter, Query
from models.token_store import save_secret

router = APIRouter()

@router.post("/slack/save-secret")
async def save_user_secret(
    user_id: str = Query(..., description="Slack username or GPT user ID"),
    secret: str = Query(..., description="User-defined secret for verification")
):
    save_secret(user_id, secret)
    return {
        "ok": True,
        "message": f"Secret saved for user {user_id}"
    }
