from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess, os, uuid, threading

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

JOBS = {}

def process_job(job_id, url, start, end):
    try:
        video_path = f"{job_id}.mp4"
        clip_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"

        subprocess.run([
            "yt-dlp","-f","bestvideo+bestaudio",
            "--merge-output-format","mp4",
            "-o", video_path, url
        ], check=True)

        subprocess.run([
            "ffmpeg","-y",
            "-ss", start,"-to", end,
            "-i", video_path,
            "-c:v","libx264","-preset","fast","-crf","18",
            "-c:a","copy", clip_path
        ], check=True)

        JOBS[job_id]["status"] = "done"

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)

@app.post("/clip")
def create_job(url:str, start:str, end:str):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status":"processing"}

    threading.Thread(
        target=process_job,
        args=(job_id,url,start,end)
    ).start()

    return {"job_id": job_id}

@app.get("/status/{job_id}")
def job_status(job_id:str):
    return JOBS.get(job_id, {"status":"not_found"})

@app.get("/download/{job_id}")
def download(job_id:str):
    file_path = f"{OUTPUT_DIR}/{job_id}_clip.mp4"
    if not os.path.exists(file_path):
        raise HTTPException(404)
    return FileResponse(file_path, media_type="video/mp4", filename="clip.mp4")
