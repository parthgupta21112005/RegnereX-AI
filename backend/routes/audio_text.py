import os
import zipfile
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from services.audio_text import audio_text
from fastapi.responses import FileResponse

json = APIRouter()

EXTRACT_DIR = "extracted_audio"
JSON_DIR = "jsons"

@json.post("/upload-audio-zip/")
async def upload_audio_zip(file: UploadFile = File(...)):
    # ✅ Check extension
    filename = file.filename
    if not filename or not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    # ✅ Ensure extract folder exists
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    # ✅ Save uploaded zip temporarily
    try:
        with zipfile.ZipFile(file.file) as zip_ref:
            # सिर्फ audio files extract करो
            for member in zip_ref.namelist():
                if member.lower().endswith(".mp3"):
                    zip_ref.extract(member, EXTRACT_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting zip: {str(e)}")

    audio_text(EXTRACT_DIR)

    return {"message": "Zip extracted successfully", "folder": EXTRACT_DIR}

import shutil
@json.get("/download-text/")
async def download_text(background_tasks: BackgroundTasks):
    zip_path = shutil.make_archive("text_zip", "zip", JSON_DIR)

    def cleanup():
        for folder in [JSON_DIR, EXTRACT_DIR]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    background_tasks.add_task(cleanup)
    return FileResponse(zip_path, filename="converted_text.zip")
