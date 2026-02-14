from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import subprocess
import os
import uuid
import json
import logging
import re
import zipfile
import io
import time

app = FastAPI(title="AI Video Clipper")

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

# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------
jobs: dict = {}
CLEANUP_AGE_SECONDS = 3600  # remove job files older than 1 hour


class ProcessRequest(BaseModel):
    url: str
    clip_duration: int = 30  # 30, 60 or 90 seconds


class JobStatus:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = "downloading"  # downloading | processing | done | error
        self.total_clips = 0
        self.completed_clips = 0
        self.clips: list[dict] = []
        self.error: str | None = None
        self.video_title = ""
        self.created_at = time.time()

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status,
            "total_clips": self.total_clips,
            "completed_clips": self.completed_clips,
            "clips": self.clips,
            "error": self.error,
            "video_title": self.video_title,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cleanup_old_jobs():
    """Delete job directories older than CLEANUP_AGE_SECONDS."""
    now = time.time()
    stale = [jid for jid, j in jobs.items()
             if now - j.created_at > CLEANUP_AGE_SECONDS and j.status in ("done", "error")]
    for jid in stale:
        job_dir = os.path.join(OUTPUT_DIR, jid)
        if os.path.isdir(job_dir):
            try:
                for f in os.listdir(job_dir):
                    os.remove(os.path.join(job_dir, f))
                os.rmdir(job_dir)
            except OSError:
                pass
        jobs.pop(jid, None)


def get_video_info(video_path: str):
    """Return (duration_seconds, width, height) via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    info = json.loads(result.stdout)

    duration = float(info["format"]["duration"])

    width, height = 1920, 1080
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            width = int(stream["width"])
            height = int(stream["height"])
            break

    return duration, width, height


def process_video(job_id: str, url: str, clip_duration: int):
    """Download a YouTube video and split it into 9:16 vertical clips."""
    job = jobs[job_id]
    job_dir = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    video_path = os.path.join(job_dir, "source.mp4")

    try:
        # -- Download ----------------------------------------------------------
        job.status = "downloading"
        logger.info("Job %s: downloading %s", job_id, url)

        # Grab the title first (best-effort)
        try:
            title_result = subprocess.run(
                ["yt-dlp", "--get-title", url],
                capture_output=True, text=True, timeout=30,
            )
            if title_result.returncode == 0:
                job.video_title = title_result.stdout.strip()
        except Exception:
            pass

        subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "--merge-output-format", "mp4",
            "-o", video_path,
            url,
        ], check=True, timeout=600)

        # -- Probe -------------------------------------------------------------
        duration, width, height = get_video_info(video_path)
        logger.info("Job %s: video %.1fs, %dx%d", job_id, duration, width, height)

        # -- Calculate clips ---------------------------------------------------
        total_clips = max(1, int(duration // clip_duration))
        total_clips = min(total_clips, 20)  # cap
        job.total_clips = total_clips
        job.status = "processing"

        # -- Generate clips ----------------------------------------------------
        for i in range(total_clips):
            start_time = i * clip_duration
            actual_duration = min(clip_duration, duration - start_time)
            if actual_duration < 5:
                job.total_clips = i
                break

            clip_path = os.path.join(job_dir, f"clip_{i}.mp4")

            # 9:16 center-crop then scale to 1080×1920
            vf = "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,setsar=1"

            subprocess.run([
                "ffmpeg", "-y",
                "-ss", str(start_time),
                "-t", str(actual_duration),
                "-i", video_path,
                "-vf", vf,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                clip_path,
            ], check=True, timeout=300)

            job.completed_clips = i + 1
            job.clips.append({
                "index": i,
                "start": start_time,
                "duration": round(actual_duration, 1),
                "filename": f"clip_{i}.mp4",
            })
            logger.info("Job %s: clip %d/%d done", job_id, i + 1, total_clips)

        # -- Cleanup source ----------------------------------------------------
        if os.path.exists(video_path):
            os.remove(video_path)

        job.status = "done"
        logger.info("Job %s: finished", job_id)

    except Exception as e:
        logger.error("Job %s failed: %s", job_id, e)
        job.status = "error"
        job.error = str(e)
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    return {"status": "AI Video Clipper API Running"}


@app.post("/process")
def start_processing(req: ProcessRequest, background_tasks: BackgroundTasks):
    youtube_re = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)\S+"
    if not re.match(youtube_re, req.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    if req.clip_duration not in (30, 60, 90):
        raise HTTPException(status_code=400, detail="Clip duration must be 30, 60, or 90 seconds")

    # Housekeeping
    cleanup_old_jobs()

    job_id = str(uuid.uuid4())
    jobs[job_id] = JobStatus(job_id)

    background_tasks.add_task(process_video, job_id, req.url, req.clip_duration)

    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id].to_dict()


# NOTE: the "download-all" route MUST be defined before the parameterised
# {clip_index} route so FastAPI matches the literal path first.
@app.get("/clips/{job_id}/download-all")
def download_all(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job.status != "done":
        raise HTTPException(status_code=400, detail="Job not finished yet")

    job_dir = os.path.join(OUTPUT_DIR, job_id)
    title = job.video_title or "clips"
    safe_title = re.sub(r"[^\w\s-]", "", title)[:50].strip() or "clips"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for clip in job.clips:
            clip_path = os.path.join(job_dir, clip["filename"])
            if os.path.exists(clip_path):
                zf.write(clip_path, f"{safe_title}_clip{clip['index'] + 1}.mp4")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}_clips.zip"'},
    )


@app.get("/clips/{job_id}/{clip_index}")
def download_clip(job_id: str, clip_index: int):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    clip_path = os.path.join(OUTPUT_DIR, job_id, f"clip_{clip_index}.mp4")
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail="Clip not found")

    title = jobs[job_id].video_title or "clip"
    safe_title = re.sub(r"[^\w\s-]", "", title)[:50].strip() or "clip"
    filename = f"{safe_title}_clip{clip_index + 1}.mp4"

    return FileResponse(clip_path, media_type="video/mp4", filename=filename)
