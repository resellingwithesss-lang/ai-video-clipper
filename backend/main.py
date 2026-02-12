from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime
import subprocess
import os
import uuid
import logging

app = FastAPI()

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


class LoginData(BaseModel):
    email: EmailStr


@app.get("/")
def home():
    return {"status": "AI Clipper Running 🚀"}


@app.post("/login")
def login(data: LoginData):
    logger.info(f"Login attempt: {data.email}")
    return {"status": "logged_in"}


@app.post("/clip")
def clip(
    background_tasks: BackgroundTasks,
    url: str = Query(...),
    start: str = Query(...),
    end: str = Query(...)
):
    try:
        start_dt = datetime.strptime(start, "%H:%M:%S")
        end_dt = datetime.strptime(end, "%H:%M:%S")

        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="End must be after start")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format HH:MM:SS")

    job_id = str(uuid.uuid4())
    video_path = f"{job_id}.mp4"
    clip_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    def process():
        try:
            subprocess.run([
                "yt-dlp",
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", video_path,
                url
            ], check=True)

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

            if os.path.exists(video_path):
                os.remove(video_path)

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")

    background_tasks.add_task(process)

    return {
        "status": "processing",
        "job_id": job_id,
        "status_url": f"/status/{job_id}",
        "download_url": f"/download/{job_id}"
    }


@app.get("/status/{job_id}")
def status(job_id: str):
    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")
    return {"status": "done" if os.path.exists(file_path) else "processing"}


@app.get("/download/{job_id}")
def download(job_id: str):
    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(file_path, media_type="video/mp4", filename="clip.mp4")
