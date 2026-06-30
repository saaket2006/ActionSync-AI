from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from memory.memory_manager import MemoryManager
from .auth import get_current_user
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/memory", tags=["Memory"])

@router.get("/search")
def search_memory(
    query: str = Query(..., description="The query string to search for in memory keys/values"),
    scope: Optional[str] = Query(None, description="Optional scope: working, session, or organizational"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Searches memory items by keyword matching or vector fallback."""
    mem_mgr = MemoryManager(db)
    return mem_mgr.search(query, scope)

@router.get("/summarize")
def summarize_memory(
    scope: str = Query(..., description="Scope to summarize: working, session, or organizational"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Generates a text summary of all keys and values in the specified scope."""
    mem_mgr = MemoryManager(db)
    try:
        summary = mem_mgr.summarize(scope)
        return {"scope": scope, "summary": summary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/write")
def write_memory(
    scope: str = Query(..., description="Scope to write: working, session, or organizational"),
    key: str = Query(..., description="The memory key"),
    value: str = Query(..., description="The memory value"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Writes a new key-value pair to memory."""
    mem_mgr = MemoryManager(db)
    try:
        mem_mgr.write(scope, key, value)
        return {"status": "success", "message": f"Wrote '{key}' to '{scope}' memory."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete")
def delete_memory(
    scope: str = Query(..., description="Scope to delete: working, session, or organizational"),
    key: str = Query(..., description="The key to delete"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Deletes a key from the specified memory scope."""
    mem_mgr = MemoryManager(db)
    try:
        mem_mgr.delete(scope, key)
        return {"status": "success", "message": f"Deleted '{key}' from '{scope}' memory."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
