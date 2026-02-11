from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import os
import uuid
import logging

app = FastAPI()

# allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-clipper")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"status": "AI Clipper Running"}


@app.post("/clip")
def clip(url: str, start: str, end: str):
    try:
        url = url.strip()
        job_id = str(uuid.uuid4())

        video_path = f"{job_id}.mp4"
        clip_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

        # 1️⃣ Download video
        download_cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "-o", video_path,
            url
        ]

        logger.info("Downloading video...")
        subprocess.run(download_cmd, check=True)

        # 2️⃣ Cut clip
        clip_cmd = [
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
        ]

        logger.info("Creating clip...")
        subprocess.run(clip_cmd, check=True)

        return {
            "status": "success",
            "download_url": f"http://localhost:8000/download/{job_id}"
        }

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ⭐ THIS FIXES THE BLOCKED DOWNLOAD
@app.get("/download/{job_id}")
def download(job_id: str):
    file_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4"
    )
