# Architecture Guide: ActionSync AI

This document details the architectural layout, pipeline processing flow, and multi-agent design of ActionSync AI.

## Pipeline Architecture

The platform processes meeting audio uploads through a structured sequence of transformations:

```
User
  ↓
[Audio Upload] ─────────► Save to uploads/
  ↓
[Speech Recognition] ───► WhisperTool transcribes audio
  ↓
[Transcript Clean] ─────► Segment insertion in SQLite/PostgreSQL
  ↓
[Google ADK Orchestrator]
  ├─► Parallel Execution Phase:
  │     ├── Summarizer Agent (Context extraction)
  │     ├── Decision Agent (Agreement extraction)
  │     ├── Action Item Agent (Task assignment)
  │     ├── Timeline Agent (Milestone mapping)
  │     └── Risk Agent (Blocker detection)
  │
  ├─► Validation Phase:
  │     └── Validator Agent (Cross-checks parallel outputs)
  │
  └─► Contextual Phase:
        ├── Community Impact Agent (Team workload evaluation)
        ├── Accountability Agent (Ownership & Check-in schedule)
        └── Clarification Agent (Identifies unresolved gaps)
  ↓
[Knowledge Graph] ──────► NetworkX updates nodes and relationships
  ↓
[Org Memory] ──────────► Sync Session & Organizational Memory items
  ↓
[FastAPI / Dashboard] ──► Query metrics and view in Streamlit UI
```

---

## Component Details

### 1. Database Layer (SQLAlchemy)
The database layer holds persistent states.
- **Relational Tables**: Map meetings, segments, people, projects, tasks, decisions, risks, timeline events, and memories.
- **Direct SQL Prevention**: Agents are prohibited from performing raw SQL queries. They rely exclusively on repositories and the memory manager context.

### 2. Memory Hierarchy
The `MemoryManager` abstracts storage from agent actions.
- **Working Memory**: In-memory dict holding transient details during single-turn workflow runs.
- **Session Memory**: Meeting-specific facts stored in SQL.
- **Organizational Memory**: Global key-value knowledge base linking cross-meeting outcomes, projects, and task histories.

### 3. Tool Registry
Tools encapsulate external connections.
- **WhisperTool**: Invokes local speech-to-text.
- **BhashiniTool**: Handles translation for multilingual support.
- **KnowledgeGraphBuilder**: Translates pipeline results into database inserts and graph nodes.
- **DocumentGenerator**: Builds executive MD/PDF report archives.
- **SemanticSearch**: Computes vector similarities using local SentenceTransformer embeddings.

### 4. Google ADK Orchestrator
The orchestrator in `orchestrator/workflow.py` inherits from `BaseNode` and overrides `_run_impl`. It controls task coordination:
- Uses `asyncio.gather` for simultaneous execution of the first 5 agents.
- Ensures strict dependency mapping by validating parallel outputs before invoking community impact, accountability, and clarification agents.
