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


class LoginData(BaseModel):
    email: EmailStr


def is_valid_url(url: str) -> bool:
    # Basic validation for URL scheme presence
    from urllib.parse import urlparse
    result = urlparse(url)
    return result.scheme in ("http", "https") and result.netloc != ""


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
    url: str = Query(..., min_length=10, max_length=2048),
    start: constr(regex=r"^\d{2}:\d{2}:\d{2}$") = Query(...),
    end: constr(regex=r"^\d{2}:\d{2}:\d{2}$") = Query(...)
):
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    try:
        start_dt = datetime.strptime(start, "%H:%M:%S")
        end_dt = datetime.strptime(end, "%H:%M:%S")

        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="End time must be after start time")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format, expected HH:MM:SS")

    job_id = str(uuid.uuid4())
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    clip_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    def process():
        try:
            logger.info(f"Job {job_id} started for URL: {url}")
            subprocess.run([
                "yt-dlp",
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", video_path,
                url
            ], check=True, capture_output=True)

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
            ], check=True, capture_output=True)

            if os.path.exists(video_path):
                os.remove(video_path)

            logger.info(f"Job {job_id} completed successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Job {job_id} failed: {e.stderr.decode().strip() if e.stderr else e}")
        except Exception as e:
            logger.error(f"Job {job_id} unexpected error: {e}")

    background_tasks.add_task(process)

    return {
        "status": "processing",
        "job_id": job_id,
        "status_url": f"/status/{job_id}",
        "download_url": f"/download/{job_id}"
    }


@app.get("/status/{job_id}")
def status(job_id: str = Path(..., min_length=36, max_length=36)):
    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")
    if os.path.exists(file_path):
        logger.info(f"Job {job_id} status checked: done")
        return {"status": "done"}
    else:
        logger.info(f"Job {job_id} status checked: processing")
        return {"status": "processing"}


@app.get("/download/{job_id}")
def download(job_id: str = Path(..., min_length=36, max_length=36)):
    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if not os.path.exists(file_path):
        logger.warning(f"Download requested for missing clip: {job_id}")
        raise HTTPException(status_code=404, detail="Clip not found")

    logger.info(f"Serving clip {job_id} for download")
    return FileResponse(file_path, media_type="video/mp4", filename="clip.mp4")