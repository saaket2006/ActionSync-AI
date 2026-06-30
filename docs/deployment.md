# Deployment Guide: ActionSync AI

This document provides instructions for deploying ActionSync AI to production using Docker and PostgreSQL.

---

## Docker Deployment

The platform is fully containerized. The `Dockerfile` in the root directory compiles Python 3.11 with ffmpeg and runs both the FastAPI backend and Streamlit frontend in parallel.

### 1. Build the Docker Image
```bash
docker build -t actionsync-ai .
```

### 2. Run the Container
Run the container, mapping port 8000 (API) and port 8501 (Web UI), and passing the environment configuration file:
```bash
docker run -d \
  --name actionsync-platform \
  --env-file .env \
  -p 8000:8000 \
  -p 8501:8501 \
  -v actionsync-storage:/app/storage \
  actionsync-ai
```
*Using volume mount `-v actionsync-storage:/app/storage` ensures uploaded audio and generated documents are persisted across container restarts.*

---

## Production PostgreSQL Setup

For production deployments, migrate from SQLite to PostgreSQL.

1. **Provision PostgreSQL Database**: Set up a PostgreSQL instance (e.g. AWS RDS, GCP Cloud SQL, or a local Docker container).
2. **Update Connection String**: Modify the `.env` file to point to your PostgreSQL instance:
   ```env
   DATABASE_URL=postgresql://db_user:db_password@db_host:5432/db_name
   ```
   *FastAPI automatically establishes connection pools and creates required tables on startup.*

---

## Production Security Recommendations

1. **Disable Swagger in Production**: In `backend/main.py`, disable docs by setting `docs_url=None` if exposing directly to the internet.
2. **Secret Keys**: Ensure `SECRET_KEY` in `.env` is a cryptographically strong string:
   ```bash
   openssl rand -hex 32
   ```
3. **SSL/TLS Configuration**: Always route frontend and backend traffic through an HTTPS proxy (such as Nginx, Traefik, or Cloudflare ALBs) to secure audio transfers and JWT authorization headers.
