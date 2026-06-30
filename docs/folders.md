# Directory Folder Guide: ActionSync AI

This document outlines the folder layout and the architectural responsibilities of each directory in ActionSync AI.

## Directory Structure

```
actionsync-ai/
├── config/             # Global configurations and .env loading
├── database/           # Connection wrappers and SQLAlchemy models
├── schemas/            # Pydantic schemas for database objects and agent I/O
├── repositories/       # Database CRUD operations (Prevents direct SQL in agents)
├── knowledge_graph/    # Graph interfaces and NetworkX implementation
├── memory/             # Multi-tier Memory Manager (Working, Session, Org)
├── tools/              # Central Tool Registry and tool definitions
├── agents/             # Google ADK Agents configurations
├── orchestrator/       # Pipeline coordinators (Concurrently and sequentially)
├── backend/            # FastAPI app server and router endpoints
├── frontend/           # Streamlit Web UI application
├── utils/              # Logging formatters and helpers
├── tests/              # Pytest unit and integration test suite
├── docs/               # Technical manuals and guides
└── storage/            # Local data directories (created automatically)
    ├── uploads/        # Uploaded meeting audio files (.mp3, .wav)
    ├── docs/           # Generated PDF and Markdown reports
    └── logs/           # System log files
```

---

## Folder Responsibilities

### `config/`
Houses global configuration. `settings.py` reads `.env` variables and registers paths.

### `database/` and `repositories/`
Encapsulates relational persistence. Repositories abstract SQL operations, protecting database sessions.

### `schemas/`
Defines serialization boundaries. Used by FastAPI request validators, SQL models, and ADK agent outputs.

### `knowledge_graph/` and `memory/`
Manages organizational intelligence and graph state. NetworkX models people, projects, and tasks. The Memory Manager handles the 3-tiered memory scopes.

### `tools/`
Declares external APIs and utility executions. Each tool inherits from `BaseActionSyncTool` and registers with the central tool manager.

### `agents/` and `orchestrator/`
Constructs the cognitive layers. `agents/` contains individual agent profiles with specific prompt instructions. `orchestrator/` coordinates the agent pipeline flow.

### `backend/` and `frontend/`
Exposes system endpoints and interfaces. Frontend communicates with Backend via REST API with JWT authorization.
