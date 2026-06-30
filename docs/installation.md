# Installation Guide: ActionSync AI

This guide walks you through setting up ActionSync AI on your local machine for development and testing.

## Prerequisites

1. **Python 3.11**: Make sure Python 3.11+ is installed.
2. **FFmpeg**: Required by `openai-whisper` for audio transcribing.
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`
   - **Windows**: Download binaries from [FFmpeg website](https://ffmpeg.org/) and add them to your system `PATH`.
3. **Git**: Required for cloning and resolving python dependencies.

---

## Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/saaket2006/ActionSync-AI.git
cd ActionSync-AI
```

### 2. Create a Virtual Environment
We recommend using Python's standard `venv`:
```bash
# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
Install all package requirements listed in `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```
Open `.env` and configure:
- **`GEMINI_API_KEY`**: Your Google Gemini API token (required for agent orchestration).
- **`DATABASE_URL`**: Change database location if needed. Defaults to a local SQLite database in the `storage/` directory.

---

## Running the Platform

To start the ActionSync AI platform locally:

1. **Start the FastAPI Backend**:
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *The Swagger API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

2. **Start the Streamlit Frontend**:
   ```bash
   streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
   ```
   *The Web UI will open automatically in your browser at [http://localhost:8501](http://localhost:8501).*
