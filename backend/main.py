from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, constr
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
    url: constr(min_length=10) = Query(..., description="Valid video url"),
    start: constr(regex=r"^\d{2}:\d{2}:\d{2}$") = Query(..., description="Start time in HH:MM:SS"),
    end: constr(regex=r"^\d{2}:\d{2}:\d{2}$") = Query(..., description="End time in HH:MM:SS")
):
    try:
        start_dt = datetime.strptime(start, "%H:%M:%S")
        end_dt = datetime.strptime(end, "%H:%M:%S")

        if end_dt <= start_dt:
            logger.warning(f"clip failed: End time {end} must be after start time {start}")
            raise HTTPException(status_code=400, detail="End time must be after start time")

    except ValueError as e:
        logger.warning(f"clip failed: Invalid time format for start='{start}' or end='{end}' - {e}")
        raise HTTPException(status_code=400, detail="Invalid time format for start or end, expected HH:MM:SS")

    job_id = str(uuid.uuid4())
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    clip_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    def process():
        try:
            logger.info(f"Job {job_id} started: downloading {url}")
            subprocess.run([
                "yt-dlp",
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", video_path,
                url
            ], check=True)

            logger.info(f"Job {job_id}: clipping video from {start} to {end}")
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
                logger.info(f"Job {job_id}: temporary video file deleted")

            logger.info(f"Job {job_id} completed successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Job {job_id} failed subprocess: {e}")
        except Exception as e:
            logger.error(f"Job {job_id} unexpected failure: {e}")

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
    status_val = "done" if os.path.exists(file_path) else "processing"
    logger.debug(f"Status check for job {job_id}: {status_val}")
    return {"status": status_val}


@app.get("/download/{job_id}")
def download(job_id: str):
    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if not os.path.exists(file_path):
        logger.warning(f"Download requested for missing clip: {job_id}")
        raise HTTPException(status_code=404, detail="Clip not found")

    logger.info(f"Download served for job {job_id}")
    return FileResponse(file_path, media_type="video/mp4", filename="clip.mp4")