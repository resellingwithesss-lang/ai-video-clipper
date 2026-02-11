from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess, os, uuid, json, threading, logging

app = FastAPI()

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-clipper")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- FILE STORAGE ----------------
OUTPUT_DIR = "outputs"
DB_FILE = "db.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# create DB if not exists
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"users": {}, "jobs": {}}, f)


def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------- HEALTH CHECK ----------------
@app.get("/")
def home():
    return {"status": "AI Clipper Running 🚀"}


# ---------------- LOGIN ----------------
@app.get("/login")
@app.post("/login")
def login(email: str):
    db = load_db()

    if email not in db["users"]:
        db["users"][email] = []
        save_db(db)

    return {"user": email}


# ---------------- VIDEO WORKER ----------------
def process_clip(job_id, url, start, end, email):
    db = load_db()
    db["jobs"][job_id]["status"] = "downloading"
    save_db(db)

    video_path = f"{OUTPUT_DIR}/{job_id}.mp4"
    clip_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

    try:
        # download video
        download_cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio",
            "--merge-output-format", "mp4",
            "-o", video_path,
            url
        ]
        subprocess.run(download_cmd, check=True)

        db["jobs"][job_id]["status"] = "clipping"
        save_db(db)

        # create clip
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

        db = load_db()
        db["jobs"][job_id]["status"] = "done"
        db["jobs"][job_id]["file"] = clip_path
        db["users"][email].append(job_id)
        save_db(db)

        logger.info(f"Job finished: {job_id}")

    except Exception as e:
        db = load_db()
        db["jobs"][job_id]["status"] = "error"
        db["jobs"][job_id]["error"] = str(e)
        save_db(db)
        logger.error(str(e))


# ---------------- CREATE CLIP ----------------
@app.post("/clip")
def create_clip(email: str, url: str, start: str, end: str):
    job_id = str(uuid.uuid4())

    db = load_db()
    db["jobs"][job_id] = {
        "status": "queued",
        "url": url,
        "start": start,
        "end": end
    }
    save_db(db)

    thread = threading.Thread(
        target=process_clip,
        args=(job_id, url.strip(), start, end, email)
    )
    thread.start()

    return {"job_id": job_id}


# ---------------- JOB STATUS ----------------
@app.get("/status/{job_id}")
def job_status(job_id: str):
    db = load_db()
    if job_id not in db["jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")
    return db["jobs"][job_id]


# ---------------- USER HISTORY ----------------
@app.get("/history")
def history(email: str):
    db = load_db()
    jobs = db["users"].get(email, [])
    return {"jobs": jobs}


# ---------------- DOWNLOAD FILE ----------------
@app.get("/download/{job_id}")
def download(job_id: str):
    db = load_db()

    if job_id not in db["jobs"]:
        raise HTTPException(status_code=404, detail="Job not found")

    file_path = db["jobs"][job_id].get("file")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not ready")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=f"clip_{job_id}.mp4"
    )
