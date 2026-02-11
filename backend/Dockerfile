FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg curl

COPY . .

RUN pip install fastapi uvicorn yt-dlp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
