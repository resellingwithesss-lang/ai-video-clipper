```python
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, AnyHttpUrl, constr, validator
import subprocess
import os
import uuid
import logging
from typing import Optional

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
class LoginRequest(BaseModel):
    email: constr(strip_whitespace=True, min_length=1)

class ClipRequest(BaseModel):
    url: AnyHttpUrl
    start: constr(regex=r"^\d{2}:\d{2}:\d{2}$")
    end: constr(regex=r"^\d{2}:\d{2}:\d{2}$")

    @validator("end")
    def check_start_end(cls, v, values):
        if "start" in values:
            def to_seconds(t: str) -> int:
                h, m, s = map(int, t.split(":"))
                return h * 3600 + m * 60 + s

            start_sec = to_seconds(values["start"])
            end_sec = to_seconds(v)
            if end_sec <= start_sec:
                raise ValueError("end must be after start")
        return v


# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"status": "AI Clipper Running 🚀"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: LoginRequest):
    # email validation is handled by Pydantic model
    logger.info(f"Login attempt for email: {data.email}")
    return {"status": "logged_in"}

# ---------------- CLIP ----------------
@app.post("/clip")
def clip(
    url: AnyHttpUrl = Query(..., description="Video URL"),
    start: constr(regex=r"^\d{2}:\d{2}:\d{2}$") = Query(..., description="Start time in HH:MM:SS"),
    end: constr(regex=r"^\d{2}:\d{2}:\d{2}$") = Query(..., description="End time in HH:MM:SS"),
    background_tasks: BackgroundTasks = None
):
    # Validate start < end
    def to_seconds(t: str) -> int:
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s

    start_sec = to_seconds(start)
    end_sec = to_seconds(end)
    if end_sec <= start_sec:
        raise HTTPException(status_code=400, detail="End time must be after start time")

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
    # Sanitize job_id input by allowing only UUID format check
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")

    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if os.path.exists(file_path):
        return {"status": "done"}

    return {"status": "processing"}

# ---------------- DOWNLOAD ----------------
@app.get("/download/{job_id}")
def download(job_id: str):
    # Sanitize job_id input by allowing only UUID format check
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")

    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename="clip.mp4"
    )
```