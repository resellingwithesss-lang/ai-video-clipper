```python
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl, constr, validator
from typing import Optional
import subprocess
import os
import uuid
import logging
import re

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

# ---------------- HELPER FUNCTIONS ----------------
def validate_time_format(time_str: str) -> bool:
    # Accepts HH:MM:SS or MM:SS or SS formats with optional decimals for seconds
    pattern = r"^(?:[0-9]{1,2}:){0,2}[0-9]+(?:\.[0-9]+)?$"
    return re.match(pattern, time_str) is not None

# ---------------- REQUEST MODELS ----------------
class LoginRequest(BaseModel):
    email: constr(strip_whitespace=True, min_length=5, max_length=256)

class ClipRequest(BaseModel):
    url: HttpUrl
    start: constr(strip_whitespace=True)
    end: constr(strip_whitespace=True)

    @validator("start")
    def start_must_be_valid_time(cls, v):
        if not validate_time_format(v):
            raise ValueError("start must be a valid time string like HH:MM:SS")
        return v

    @validator("end")
    def end_must_be_valid_time(cls, v):
        if not validate_time_format(v):
            raise ValueError("end must be a valid time string like HH:MM:SS")
        return v

    @validator("end")
    def end_must_be_after_start(cls, v, values):
        start = values.get("start")
        if start and v <= start:
            raise ValueError("end time must be after start time")
        return v

# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"status": "AI Clipper Running 🚀"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: LoginRequest):
    email = data.email
    # Potential place for authentication logic, currently stub
    logger.info(f"Login attempt for email: {email}")
    return {"status": "logged_in"}

# ---------------- CLIP ----------------
@app.post("/clip")
def clip(
    data: ClipRequest,
    background_tasks: BackgroundTasks
):
    job_id = str(uuid.uuid4())
    video_path = f"{job_id}.mp4"
    clip_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

    def process_clip():
        try:
            logger.info(f"Starting job {job_id}")

            # Download video
            download_cmd = [
                "yt-dlp",
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", video_path,
                str(data.url)
            ]
            result = subprocess.run(download_cmd, check=True, capture_output=True, text=True)
            logger.debug(f"yt-dlp output: {result.stdout}")

            # Cut clip
            clip_cmd = [
                "ffmpeg",
                "-y",
                "-ss", data.start,
                "-to", data.end,
                "-i", video_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-c:a", "copy",
                clip_path
            ]
            result = subprocess.run(clip_cmd, check=True, capture_output=True, text=True)
            logger.debug(f"ffmpeg output: {result.stdout}")

            # Cleanup original video
            if os.path.exists(video_path):
                os.remove(video_path)

            logger.info(f"Job {job_id} completed")

        except subprocess.CalledProcessError as e:
            logger.error(f"Job {job_id} failed subprocess error: {e.stderr}")
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
    safe_job_id = re.sub(r"[^a-f0-9\-]", "", job_id.lower())
    file_path = f"{OUTPUT_DIR}/{safe_job_id}_clip.mp4"

    if os.path.exists(file_path):
        return {"status": "done"}

    return {"status": "processing"}

# ---------------- DOWNLOAD ----------------
@app.get("/download/{job_id}")
def download(job_id: str):
    safe_job_id = re.sub(r"[^a-f0-9\-]", "", job_id.lower())
    file_path = f"{OUTPUT_DIR}/{safe_job_id}_clip.mp4"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename="clip.mp4"
    )
```