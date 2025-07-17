import httpx

async def slack_post(endpoint, token, json):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://slack.com/api/{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            json=json
        )
        return resp.json()

async def slack_get(endpoint, token, params=None):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://slack.com/api/{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            params=params or {}
        )
        return resp.json()
