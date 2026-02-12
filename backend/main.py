```python
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
import subprocess
import os
import uuid
import logging
from datetime import datetime

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-clipper")

# ---------------- OUTPUT DIRECTORY ----------------
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- MODELS ----------------

class LoginData(BaseModel):
    email: EmailStr

# ISO 8601 duration or HH:MM:SS string validation improved using regex and custom validator
class ClipQueryParams(BaseModel):
    url: constr(strip_whitespace=True, min_length=1)
    start: constr(strip_whitespace=True, min_length=1)
    end: constr(strip_whitespace=True, min_length=1)

    @validator('start')
    def validate_start(cls, v):
        try:
            datetime.strptime(v, '%H:%M:%S')
        except ValueError:
            raise ValueError('start must be a time string in HH:MM:SS format')
        return v

    @validator('end')
    def validate_end(cls, v):
        try:
            datetime.strptime(v, '%H:%M:%S')
        except ValueError:
            raise ValueError('end must be a time string in HH:MM:SS format')
        return v

    @validator('end')
    def end_after_start(cls, v, values):
        if 'start' in values:
            start_dt = datetime.strptime(values['start'], '%H:%M:%S')
            end_dt = datetime.strptime(v, '%H:%M:%S')
            if end_dt <= start_dt:
                raise ValueError('end time must be after start time')
        return v

# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"status": "AI Clipper Running 🚀"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: LoginData):
    # Email is validated by LoginData
    logger.info(f"Login attempt for email: {data.email}")
    return {"status": "logged_in"}

# ---------------- CLIP ----------------
@app.post("/clip")
def clip(
    url: str = Query(..., min_length=1, description="Video URL"),
    start: str = Query(..., regex=r"^\d{2}:\d{2}:\d{2}$", description="Start time HH:MM:SS"),
    end: str = Query(..., regex=r"^\d{2}:\d{2}:\d{2}$", description="End time HH:MM:SS"),
    background_tasks: BackgroundTasks = None
):
    # Validate start and end time order
    try:
        start_dt = datetime.strptime(start, '%H:%M:%S')
        end_dt = datetime.strptime(end, '%H:%M:%S')
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="End time must be after start time")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")

    job_id = str(uuid.uuid4())
    video_path = f"{job_id}.mp4"
    clip_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    def process_clip():
        try:
            logger.info(f"Starting job {job_id}")

            # Download video
            download_cmd = [
                "yt-dlp",
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", video_path,
                url
            ]
            subprocess.run(download_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Cut clip
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
            subprocess.run(clip_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Cleanup original video
            if os.path.exists(video_path):
                os.remove(video_path)

            logger.info(f"Job {job_id} completed")

        except subprocess.CalledProcessError as e:
            logger.error(f"Job {job_id} failed: {e.stderr.decode().strip()}")
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")

    background_tasks.add_task(process_clip)

    return {
        "status": "processing",
        "job_id": job_id,
        "status_url": f"/status/{job_id}",
        "download_url": f"/download/{job_id}"
    }

# ---------------- STATUS ----------------
@app.get("/status/{job_id}")
def status(job_id: str):
    if not job_id or len(job_id) > 64:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if os.path.exists(file_path):
        return {"status": "done"}

    return {"status": "processing"}

# ---------------- DOWNLOAD ----------------
@app.get("/download/{job_id}")
def download(job_id: str):
    if not job_id or len(job_id) > 64:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    # Return file with safer filename to prevent exploitation
    safe_filename = f"{job_id}_clip.mp4"
    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=safe_filename
    )
```