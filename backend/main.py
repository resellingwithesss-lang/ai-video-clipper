from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path
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

TIME_FORMAT = "%H:%M:%S"


class LoginData(BaseModel):
    email: EmailStr


class ClipQueryParams(BaseModel):
    url: constr(strip_whitespace=True, min_length=8)  # minimum length to avoid empty or invalid urls
    start: constr(regex=r"^\d{2}:\d{2}:\d{2}$")
    end: constr(regex=r"^\d{2}:\d{2}:\d{2}$")


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
    url: str = Query(..., description="Video URL to download and clip"),
    start: str = Query(..., description="Start time in HH:MM:SS format"),
    end: str = Query(..., description="End time in HH:MM:SS format")
):
    try:
        # Validate and parse times
        start_dt = datetime.strptime(start, TIME_FORMAT)
        end_dt = datetime.strptime(end, TIME_FORMAT)

        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="End time must be after start time")

        # Basic URL validation (could be extended)
        if not (url.startswith("http://") or url.startswith("https://")):
            raise HTTPException(status_code=400, detail="Invalid URL format")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Invalid time format, expected HH:MM:SS") from ve

    job_id = str(uuid.uuid4())
    safe_video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    clip_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    def process():
        try:
            logger.info(f"Job {job_id} started: downloading video from {url}")
            subprocess.run([
                "yt-dlp",
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", safe_video_path,
                url
            ], check=True)

            logger.info(f"Job {job_id}: video downloaded, starting clip from {start} to {end}")
            subprocess.run([
                "ffmpeg",
                "-y",
                "-ss", start,
                "-to", end,
                "-i", safe_video_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-c:a", "copy",
                clip_path
            ], check=True)

            if os.path.exists(safe_video_path):
                os.remove(safe_video_path)
                logger.info(f"Job {job_id}: temporary video file removed")

            logger.info(f"Job {job_id} completed successfully")

        except subprocess.CalledProcessError as cpe:
            logger.error(f"Job {job_id} subprocess failed: {cpe}")
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
def status(job_id: str = Path(..., description="Job ID UUID string")):
    if not job_id or len(job_id) != 36:
        raise HTTPException(status_code=400, detail="Invalid job_id format")

    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")
    clip_exists = os.path.exists(file_path)
    logger.info(f"Status check for job {job_id}: {'done' if clip_exists else 'processing'}")
    return {"status": "done" if clip_exists else "processing"}


@app.get("/download/{job_id}")
def download(job_id: str = Path(..., description="Job ID UUID string")):
    if not job_id or len(job_id) != 36:
        raise HTTPException(status_code=400, detail="Invalid job_id format")

    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if not os.path.exists(file_path):
        logger.warning(f"Download attempt for missing clip job {job_id}")
        raise HTTPException(status_code=404, detail="Clip not found")

    logger.info(f"Download started for job {job_id}")
    return FileResponse(file_path, media_type="video/mp4", filename=f"{job_id}_clip.mp4")