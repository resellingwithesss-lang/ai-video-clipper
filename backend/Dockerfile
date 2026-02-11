FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp globally
RUN pip install --no-cache-dir yt-dlp

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

# Copy backend code
COPY . .

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
