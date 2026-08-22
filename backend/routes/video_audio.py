from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import os
import shutil
from services.video_audio import video_audio

file = APIRouter()

# Directory to store uploaded videos
UPLOAD_DIR = "uploaded_videos"
AUDIO_DIR = "audio"

# Allowed video extensions
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

# Max file size in bytes (e.g., 100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


def validate_video(file: UploadFile):
    """Validate file extension and size."""
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

    # Check file size (streaming read)
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large: {file.filename}")


@file.post("/upload-videos/")
async def upload_videos(files: List[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_files = []

    for file in files:
        try:
            validate_video(file)

            filename = file.filename
            if filename is None:
                raise HTTPException(status_code=400, detail="Filename is required")

            # Save file to disk
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_files.append(file.filename)
            video_audio(UPLOAD_DIR)

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"error": e.detail})
        finally:
            file.file.close()

    return {"message": "Videos uploaded successfully", "files": saved_files}

# ✅ Route to download all converted audio files as zip

@file.get("/download-audio/")
async def download_audio(background_tasks: BackgroundTasks):
    zip_path = shutil.make_archive("audio_zip", "zip", AUDIO_DIR)

    def cleanup():
            for folder in [AUDIO_DIR, UPLOAD_DIR]:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
            if os.path.exists(zip_path):
                os.remove(zip_path)

    background_tasks.add_task(cleanup)
    return FileResponse(zip_path, filename="converted_audio.zip")
