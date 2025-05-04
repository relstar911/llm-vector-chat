from fastapi import FastAPI
from app.api import chat, query, chats, sessions, factcheck

app = FastAPI()

app.include_router(chat.router)
app.include_router(query.router)
app.include_router(chats.router)
app.include_router(sessions.router)
app.include_router(factcheck.router)
app.include_router(factcheck.router)

@app.get("/")
def read_root():
    return {"message": "LLM Chat Vector App läuft!"}
