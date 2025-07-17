from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx
import os
import json

from models.token_store import (
    get_token_by_gpt_user,
    load_user_map,
    load_all_tokens,
    save_all_tokens,
    save_user_map,
)

router = APIRouter()


@router.get("/slack/whoami")
async def slack_whoami(user_id: str = Query(...)):
    token = get_token_by_gpt_user(user_id)
    if not token:
        return {"ok": False, "error": "No token found for user"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {token}"}
        )
        return resp.json()


@router.get("/debug/token-map")
async def token_map():
    user_map = load_user_map()
    tokens = load_all_tokens()
    result = {}

    for gpt_id, slack_id in user_map.items():
        token = tokens.get(slack_id)
        result[gpt_id] = {
            "slack_user_id": slack_id,
            "token_starts_with": token[:12] + "..." if token else None
        }

    return JSONResponse(result)


@router.delete("/slack/logout")
async def logout(user_id: str = Query(...)):
    user_map = load_user_map()
    tokens = load_all_tokens()

    slack_user_id = user_map.pop(user_id, None)
    if slack_user_id:
        tokens.pop(slack_user_id, None)
        save_user_map(user_map)
        save_all_tokens(tokens)
        return {"ok": True, "message": f"Disconnected {user_id}"}

    return {"ok": False, "error": "User not found"}
