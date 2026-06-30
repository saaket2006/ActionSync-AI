# ActionSync AI

> **Tagline:** From Conversations to Accountability  
> **Overview:** ActionSync AI is a production-ready, agentic Meeting Intelligence Platform that converts raw organizational conversations into structured, validated execution blueprints (decisions, tasks, risks, and timelines) using a multi-agent workflow coordinated by Google ADK.

Unlike standard summary chatbots, ActionSync AI operates as a unified multi-agent pipeline executing parallel analysis, validation, and team alignment assessments.

---

## 🛠️ Technology Stack

- **Orchestration**: Google ADK (Agent Development Kit)
- **AI Model**: Gemini 2.5 Flash
- **Backend API**: FastAPI
- **Frontend Dashboard**: Streamlit
- **Transcription**: Faster Whisper
- **Translation**: Bhashini API
- **Entities & Relations**: NetworkX (MVP) & SQLAlchemy
- **Databases**: SQLite (Development) / PostgreSQL (Production)

---

## 📂 Project Structure & Guides

For details on configuration, code organization, and execution, refer to our comprehensive documentation:

1. **[Installation Guide](docs/installation.md)**: System requirements (FFmpeg), environment files, and local run configurations.
2. **[Architecture Guide](docs/architecture.md)**: Agent coordination flow charts, pipeline transformations, and memory designs.
3. **[Folder Structure Guide](docs/folders.md)**: Responsibilities of each directory in the modular layout.
4. **[API Router Reference](docs/api.md)**: REST endpoints for authentication, uploads, agents, and report downloads.
5. **[ADK Agents Manual](docs/agents.md)**: Directives and schemas for the nine configured agents.
6. **[Developer Customization Manual](docs/developer.md)**: Guide for running pytest suites, writing new tools, and creating agents.
7. **[Docker & Production Deployment Guide](docs/deployment.md)**: Running inside containers and configuring production PostgreSQL.

---

## 🚀 Quick Start

### 1. Configure Credentials
Copy `.env.example` to `.env` and insert your `GEMINI_API_KEY`:
```bash
cp .env.example .env
```

### 2. Run with Docker Compose or Docker
```bash
docker build -t actionsync-ai .
docker run -d -p 8000:8000 -p 8501:8501 --env-file .env actionsync-ai
```

Access the **API Swagger Docs** at [http://localhost:8000/docs](http://localhost:8000/docs) and the **Streamlit Web UI** at [http://localhost:8501](http://localhost:8501).

---

## 🔒 License

Proprietary License. All rights reserved. Developed by Senior STAFF Engineering Team.