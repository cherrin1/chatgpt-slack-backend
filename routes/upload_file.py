from fastapi import APIRouter
from models.token_store import get_token_by_gpt_user
import httpx

router = APIRouter()

@router.post("/slack/upload-file")
async def upload_file(payload: dict):
    user_id = payload["user_id"]
    secret = payload["secret"]
    file_url = payload["file_url"]
    filename = payload["filename"]
    channel = payload["channel"]

    token = get_token_by_gpt_user(user_id, secret)
    if not token:
        return {"ok": False, "error": "User not authorized"}

    # Step 1: Request upload URL
    async with httpx.AsyncClient() as client:
        slack_response = await client.post(
            "https://slack.com/api/files.getUploadURLExternal",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "filename": filename,
                "length": 10000000,  # Optional size estimate
                "channels": [channel]
            }
        )
    upload_data = slack_response.json()
    if not upload_data.get("ok"):
        return {"ok": False, "error": upload_data.get("error")}

    upload_url = upload_data["upload_url"]
    file_id = upload_data["file_id"]

    # Step 2: Download file from external URL
    async with httpx.AsyncClient() as client:
        file_response = await client.get(file_url)
        file_bytes = file_response.content

    # Step 3: Upload to Slack
    async with httpx.AsyncClient() as client:
        upload_response = await client.post(
            upload_url,
            files={"file": (filename, file_bytes)}
        )
    if upload_response.status_code != 200:
        return {"ok": False, "error": "Upload to Slack failed."}

    # Step 4: Complete upload
    async with httpx.AsyncClient() as client:
        complete = await client.post(
            "https://slack.com/api/files.completeUploadExternal",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "files": [
                    {
                        "id": file_id,
                        "title": filename
                    }
                ]
            }
        )
    complete_data = complete.json()
    if not complete_data.get("ok"):
        return {"ok": False, "error": complete_data.get("error")}

    return {"ok": True, "file_id": file_id}
