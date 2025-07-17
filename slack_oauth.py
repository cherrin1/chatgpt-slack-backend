import os
import httpx
import urllib.parse
from uuid import uuid4
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from models.token_store import save_token

router = APIRouter()

@router.get("/oauth/start")
async def start_oauth(gpt_user_id: str = Query(...)):
    client_id = os.getenv("SLACK_CLIENT_ID")
    redirect_uri = os.getenv("SLACK_REDIRECT_URI")

    if not client_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="Missing Slack client ID or redirect URI in environment variables")

    scopes = [
        "channels:read", "chat:write", "users:read", "channels:history",
        "im:history", "mpim:history", "search:read", "groups:read",
        "mpim:read", "channels:write", "groups:write", "im:write"
    ]
    user_scope = urllib.parse.quote_plus(" ".join(scopes))

    url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={client_id}"
        f"&user_scope={user_scope}"
        f"&redirect_uri={urllib.parse.quote_plus(redirect_uri)}"
        f"&state={gpt_user_id}"
    )
    
    return {"url": url}


@router.get("/oauth/callback", response_class=HTMLResponse)
async def oauth_callback(code: str = Query(...), state: str = Query(...)):
    # We're replacing GPT's opaque user_id with Slack username later
    original_gpt_id = state

    client_id = os.getenv("SLACK_CLIENT_ID")
    client_secret = os.getenv("SLACK_CLIENT_SECRET")
    redirect_uri = os.getenv("SLACK_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        return HTMLResponse(
            "<h2>❌ Slack configuration error. Check environment variables.</h2>",
            status_code=500
        )

    async with httpx.AsyncClient() as client:
        # Step 1: Get token
        resp = await client.post("https://slack.com/api/oauth.v2.access", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        })

        data = resp.json()

        if not data.get("ok") or "authed_user" not in data:
            error_message = data.get("error", "Unknown error")
            return HTMLResponse(
                content=f"<h2>❌ Slack connection failed:</h2><pre>{error_message}</pre>",
                status_code=400
            )

        slack_user_id = data["authed_user"]["id"]
        access_token = data["authed_user"]["access_token"]

        # Step 2: Look up Slack username
        user_info_resp = await client.get(
            "https://slack.com/api/users.info",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"user": slack_user_id}
        )
        user_info = user_info_resp.json()
        slack_username = user_info.get("user", {}).get("name", slack_user_id)

        # Step 3: Save using slack_username as the GPT user ID
        save_token(slack_user_id, access_token, gpt_user_id=slack_username)

        return HTMLResponse(f"""
            <html>
                <head><title>Slack Connected</title></head>
                <body style="font-family:sans-serif">
                    <h2>✅ Slack Connected!</h2>
                    <p>You are now linked as:</p>
                    <ul>
                        <li><strong>Slack Username:</strong> <code>{slack_username}</code></li>
                        <li><strong>Slack User ID:</strong> <code>{slack_user_id}</code></li>
                    </ul>
                    <p>This username will now act as your GPT identity.</p>
                    <p>You can return to ChatGPT.</p>
                </body>
            </html>
        """)