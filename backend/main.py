from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.video_audio import file
from routes.audio_text import json

app = FastAPI(title="Welcome to Rag")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(file, prefix="", tags=["file"])
app.include_router(json, prefix="", tags=["json"])