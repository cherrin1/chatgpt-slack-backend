from fastapi import FastAPI
from slack_oauth import router as oauth_router
from routes.send_message import router as send_message_router
from routes.get_conversations import router as get_conversations_router

app = FastAPI()

app.include_router(oauth_router)
app.include_router(send_message_router)
app.include_router(get_conversations_router)
