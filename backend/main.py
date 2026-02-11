from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess, os, uuid, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "outputs"
DB_FILE = "db.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- DATABASE ----------
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "jobs": {}}
    return json.load(open(DB_FILE))

def save_db(db):
    json.dump(db, open(DB_FILE, "w"))

# ---------- AUTH ----------
@app.post("/login")
def login(email: str):
    db = load_db()
    if email not in db["users"]:
        db["users"][email] = []
        save_db(db)
    return {"user": email}

# ---------- JOB WORKER ----------
def process_clip(job_id, url, start, end, user):
    db = load_db()

    video_path = f"{OUTPUT_DIR}/{job_id}.mp4"
    clip_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

    try:
        db["jobs"][job_id]["status"] = "downloading"
        save_db(db)

        subprocess.run([
            "yt-dlp","-f","bestvideo+bestaudio",
            "--merge-output-format","mp4","-o",video_path,url
        ], check=True)

        db["jobs"][job_id]["status"] = "processing"
        save_db(db)

        subprocess.run([
            "ffmpeg","-y","-ss",start,"-to",end,"-i",video_path,
            "-c:v","libx264","-preset","fast","-crf","18",
            "-c:a","copy",clip_path
        ], check=True)

        db["jobs"][job_id]["status"] = "complete"
        db["users"][user].append(job_id)
        save_db(db)

    except Exception as e:
        db["jobs"][job_id]["status"] = "error"
        save_db(db)

# ---------- CREATE CLIP ----------
@app.post("/clip")
def create_clip(url:str,start:str,end:str,user:str,background_tasks:BackgroundTasks):
    db = load_db()

    job_id = str(uuid.uuid4())
    db["jobs"][job_id] = {"status":"queued"}
    save_db(db)

    background_tasks.add_task(process_clip,job_id,url,start,end,user)
    return {"job_id":job_id}

# ---------- JOB STATUS ----------
@app.get("/status/{job_id}")
def status(job_id:str):
    db = load_db()
    return db["jobs"].get(job_id,{})

# ---------- USER HISTORY ----------
@app.get("/history/{user}")
def history(user:str):
    db = load_db()
    jobs = db["users"].get(user,[])
    return {"jobs":jobs}

# ---------- DOWNLOAD ----------
@app.get("/download/{job_id}")
def download(job_id:str):
    path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"
    if not os.path.exists(path):
        raise HTTPException(404,"Not ready")
    return FileResponse(path,media_type="video/mp4")
