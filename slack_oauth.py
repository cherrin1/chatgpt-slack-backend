import os
import httpx
import urllib.parse
import uuid
from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from models.token_store import save_token  # assumes you implemented this

router = APIRouter()

@router.get("/oauth/start")
async def start_oauth():
    client_id = os.getenv("SLACK_CLIENT_ID")
    redirect_uri = os.getenv("SLACK_REDIRECT_URI")
    state = str(uuid.uuid4())  # optional: save to DB for CSRF protection

    scopes = [
        "channels:read",
        "chat:write",
        "users:read",
        "channels:history",
        "im:history",
        "mpim:history",
        "search:read",
        "groups:read",
        "mpim:read",
        "channels:write",
        "groups:write",
        "im:write"
    ]

    user_scope = urllib.parse.quote_plus(" ".join(scopes))

    url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={client_id}"
        f"&user_scope={user_scope}"
        f"&redirect_uri={urllib.parse.quote_plus(redirect_uri)}"
        f"&state={state}"
    )
    
    return {"url": url}

@router.get("/oauth/callback", response_class=HTMLResponse)
async def oauth_callback(code: str = Query(...), state: str = Query(None)):
    client_id = os.getenv("SLACK_CLIENT_ID")
    client_secret = os.getenv("SLACK_CLIENT_SECRET")
    redirect_uri = os.getenv("SLACK_REDIRECT_URI")

    async with httpx.AsyncClient() as client:
        resp = await client.post("https://slack.com/api/oauth.v2.access", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        })

    data = resp.json()

    if data.get("ok") and "authed_user" in data:
        user_id = data["authed_user"]["id"]
        access_token = data["authed_user"]["access_token"]

        save_token(user_id, access_token)

        html = f"""
        <html>
        <head><title>Slack Connected</title></head>
        <body style="font-family:sans-serif">
            <h2>✅ Slack Connected!</h2>
            <p>You can now return to ChatGPT and use Slack actions as <code>{user_id}</code>.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=200)

    error_message = data.get("error", "Unknown error")
    return HTMLResponse(
        content=f"<h2>❌ Slack connection failed:</h2><pre>{error_message}</pre>",
        status_code=400
    )
