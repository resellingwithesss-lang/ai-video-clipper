from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import os
import uuid
import logging

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

# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"status": "AI Clipper Running 🚀"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    return {"status": "logged_in"}

# ---------------- CLIP ----------------
@app.post("/clip")
def clip(
    url: str,
    start: str,
    end: str,
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
                url
            ]
            subprocess.run(download_cmd, check=True)

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
            subprocess.run(clip_cmd, check=True)

            # Cleanup original video
            if os.path.exists(video_path):
                os.remove(video_path)

            logger.info(f"Job {job_id} completed")

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
    file_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

    if os.path.exists(file_path):
        return {"status": "done"}

    return {"status": "processing"}

# ---------------- DOWNLOAD ----------------
@app.get("/download/{job_id}")
def download(job_id: str):
    file_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename="clip.mp4"
    )
