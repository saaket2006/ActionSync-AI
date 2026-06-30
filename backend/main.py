import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import init_db
import utils.logging

# Import tools to ensure they are registered with the central Tool Registry on startup
import tools.whisper_tool
import tools.bhashini_tool
import tools.kg_builder
import tools.doc_generator
import tools.semantic_search

from backend.routers import health, auth, settings, memory, reports, meetings, agents, dashboard

app = FastAPI(
    title="ActionSync AI - Meeting Intelligence Platform API",
    description="Backend API powering ActionSync AI multi-agent meeting analysis pipelines.",
    version="1.0.0"
)

# CORS configuration for local development and frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database Schema on Startup
@app.on_event("startup")
def startup_event():
    init_db()

# Include Sub-Routers
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(meetings.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
