FROM python:3.11-slim

# Install system dependencies (ffmpeg is required by Whisper for audio extraction)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure storage directories exist inside the container
RUN mkdir -p storage/uploads storage/docs storage/logs

# Expose backend (8000) and frontend (8501) ports
EXPOSE 8000
EXPOSE 8501

# Start both FastAPI backend and Streamlit frontend in parallel
CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
