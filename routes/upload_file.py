from fastapi import APIRouter
from models.token_store import get_token_by_gpt_user
import httpx

router = APIRouter()

@router.post("/slack/upload-file")
async def upload_file(payload: dict):
    user_id = payload["user_id"]
    file_url = payload["file_url"]
    filename = payload["filename"]
    channel = payload["channel"]

    token = get_token_by_gpt_user(user_id)
    if not token:
        return {"ok": False, "error": "User not authorized"}

    async with httpx.AsyncClient() as client:
        # Step 1: Download file
        file_response = await client.get(file_url)
        if file_response.status_code != 200:
            return {"ok": False, "error": "File download failed"}

        file_bytes = file_response.content
        file_length = len(file_bytes)

        # Step 2: Request upload URL from Slack
        upload_url_resp = await client.post(
            "https://slack.com/api/files.getUploadURLExternal",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "filename": filename,
                "length": file_length,
                "channels": [channel]
            }
        )
        upload_data = upload_url_resp.json()
        if not upload_data.get("ok"):
            return {"ok": False, "error": upload_data.get("error")}

        upload_url = upload_data["upload_url"]
        file_id = upload_data["file_id"]

        # Step 3: Upload file bytes to Slack
        upload_response = await client.post(
            upload_url,
            files={"file": (filename, file_bytes)}
        )
        if upload_response.status_code != 200:
            return {"ok": False, "error": "Upload to Slack failed."}

        # Step 4: Complete upload
        complete_resp = await client.post(
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
        complete_data = complete_resp.json()
        if not complete_data.get("ok"):
            return {"ok": False, "error": complete_data.get("error")}

    return {"ok": True, "file_id": file_id}
