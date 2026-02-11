from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess, os, uuid, logging

app = FastAPI()

# allow frontend
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

# in-memory job tracker
JOBS = {}

@app.get("/")
def home():
    return {"status": "AI Clipper running"}

# background worker
def process_clip(job_id, url, start, end):
    try:
        JOBS[job_id]["status"] = "downloading"

        video_path = f"{OUTPUT_DIR}/{job_id}.mp4"
        clip_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

        # download video
        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "-o", video_path,
            url
        ], check=True)

        JOBS[job_id]["status"] = "processing"

        # cut clip
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

        JOBS[job_id]["status"] = "complete"

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
        logger.error(e)

@app.post("/clip")
def create_clip(url: str, start: str, end: str, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued"}

    background_tasks.add_task(process_clip, job_id, url, start, end)

    return {"job_id": job_id}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(404, "Job not found")
    return JOBS[job_id]

@app.get("/download/{job_id}")
def download(job_id: str):
    path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"
    if not os.path.exists(path):
        raise HTTPException(404, "Clip not ready")
    return FileResponse(path, media_type="video/mp4")
