import os
import zipfile
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from services.read_chunks import ai_assistant
from services.process_incoming import response

from pydantic import BaseModel, field_validator

class chatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        if not value.strip():
            raise ValueError("Message cannot be empty")

        return value

rag_ai = APIRouter()

EXTRACT_DIR = "jsons"

@rag_ai.post("/upload-json-zip/")
async def upload_json_zip(file: UploadFile = File(...)):
    filename = file.filename
    if not filename or not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    os.makedirs(EXTRACT_DIR, exist_ok=True)

    try:
        with zipfile.ZipFile(file.file) as zip_ref:

            for member in zip_ref.namelist():
                if member.lower().endswith(".json"):
                    zip_ref.extract(member, EXTRACT_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting zip: {str(e)}")
    ai_assistant(EXTRACT_DIR)

    return {"message": "Zip extracted successfully", "folder": EXTRACT_DIR}


@rag_ai.post("/ai-chat")
async def create_item(user_inputs: chatRequest):
    try:
        prompt = response(user_inputs.message)
        return {"prompt": prompt}
    except Exception as e:
        print("LLM Error:", e)
        raise HTTPException(
            status_code=500,
            detail="AI services is currently unavailaible"
        )