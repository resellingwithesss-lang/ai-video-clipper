from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

app = FastAPI()

# allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/")
def home():
    return {"status": "AI Clipper Running 🚀"}


# -------------------------
# SIMPLE LOGIN (MVP)
# -------------------------
@app.post("/login")
def login(data: dict):
    email = data.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    # For now any email works (MVP auth)
    return {"status": "logged_in", "email": email}


# -------------------------
# CREATE CLIP
# -------------------------
@app.post("/clip")
def clip(url: str, start: str, end: str):
    try:
        job_id = str(uuid.uuid4())
        video_path = f"{job_id}.mp4"
        clip_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

        # download youtube video
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "-o", video_path,
            url
        ], check=True)

        # cut clip
        subprocess.run([
            "ffmpeg",
            "-y",
            "-ss", start,
            "-to", end,
            "-i", video_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "copy",
            clip_path
        ], check=True)

        return {
            "status": "success",
            "download_url": f"https://ai-clipper-backend.onrender.com/download/{job_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# DOWNLOAD FILE
# -------------------------
@app.get("/download/{job_id}")
def download(job_id: str):
    file_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(file_path, media_type="video/mp4", filename="clip.mp4")
