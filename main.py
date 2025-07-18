from fastapi import FastAPI
from slack_oauth import router as oauth_router
from routes.send_message import router as send_message_router
from routes.get_conversations import router as get_conversations_router
from routes.get_messages import router as get_messages_router
from routes.slack_status import router as status_router
from slack_admin import router as admin_router
from routes.slack_users import router as users_router
from routes.user_secret import router as secret_router
from routes.slack_react import router as react_router       # <-- ✅ NEW
from routes.slack_search import router as search_router     # <-- ✅ NEW
from routes.upload_file import router as file_router     # <-- ✅ NEW



app = FastAPI()

app.include_router(oauth_router)
app.include_router(send_message_router)
app.include_router(get_conversations_router)
app.include_router(get_messages_router)
app.include_router(status_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(secret_router)
app.include_router(react_router)     # <-- ✅ NEW
app.include_router(search_router)    # <-- ✅ NEW
app.include_router(file_router)    # <-- ✅ NEW