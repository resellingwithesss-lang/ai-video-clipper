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


@app.get("/")
def home():
    logger.debug("Health check endpoint called")
    return {"status": "AI Clipper Running 🚀"}


@app.post("/login")
def login(data: LoginData):
    logger.info(f"Login attempt: {data.email}")
    return {"status": "logged_in"}


def validate_time_format(time_str: str) -> datetime:
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S")
        return dt
    except ValueError:
        logger.warning(f"Invalid time format received: {time_str}")
        raise HTTPException(status_code=400, detail="Invalid time format HH:MM:SS")


@app.post("/clip")
def clip(
    background_tasks: BackgroundTasks,
    url: constr(min_length=10, max_length=2048) = Query(..., description="Video URL to download and clip"),
    start: str = Query(..., description="Start time in HH:MM:SS format"),
    end: str = Query(..., description="End time in HH:MM:SS format")
):
    start_dt = validate_time_format(start)
    end_dt = validate_time_format(end)

    if end_dt <= start_dt:
        logger.warning(f"End time {end} is not after start time {start}")
        raise HTTPException(status_code=400, detail="End must be after start")

    job_id = str(uuid.uuid4())
    video_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    clip_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    def process():
        try:
            logger.info(f"Job {job_id} started processing. Downloading video from {url}")
            subprocess.run([
                "yt-dlp",
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", video_path,
                url
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            logger.info(f"Job {job_id} video downloaded, starting clip from {start} to {end}")
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
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if os.path.exists(video_path):
                os.remove(video_path)
                logger.debug(f"Job {job_id} temporary video file removed")

            logger.info(f"Job {job_id} completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Job {job_id} failed during subprocess call: {e.stderr.decode()}")
        except Exception as e:
            logger.error(f"Job {job_id} unexpected error: {e}")

    background_tasks.add_task(process)

    logger.info(f"Job {job_id} submitted for processing")

    return {
        "status": "processing",
        "job_id": job_id,
        "status_url": f"/status/{job_id}",
        "download_url": f"/download/{job_id}"
    }


@app.get("/status/{job_id}")
def status(job_id: constr(min_length=36, max_length=36) = Path(..., description="UUID of the clip job")):
    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")
    done = os.path.exists(file_path)
    logger.debug(f"Status check for job {job_id}: {'done' if done else 'processing'}")
    return {"status": "done" if done else "processing"}


@app.get("/download/{job_id}")
def download(job_id: constr(min_length=36, max_length=36) = Path(..., description="UUID of the clip job")):
    file_path = os.path.join(OUTPUT_DIR, f"{job_id}_clip.mp4")

    if not os.path.exists(file_path):
        logger.warning(f"Download requested for job {job_id} but clip not found")
        raise HTTPException(status_code=404, detail="Clip not found")

    logger.info(f"Clip {job_id} downloaded")
    return FileResponse(file_path, media_type="video/mp4", filename="clip.mp4")