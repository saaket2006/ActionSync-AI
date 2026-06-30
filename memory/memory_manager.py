import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from repositories.meeting_repository import MeetingRepository
from config.settings import settings

logger = logging.getLogger("actionsync.memory")

class MemoryManager:
    """Manages the memory hierarchy (Working, Session, Organizational).
    
    Provides standardized read, write, update, delete, search, and summarize operations.
    Agents interact only with this service, never directly querying SQL or files.
    """
    def __init__(self, db: Session):
        self.db = db
        # Working memory is ephemeral and stored in memory during the execution lifecycle.
        self._working_memory: Dict[str, str] = {}

    def read(self, scope: str, key: str) -> Optional[str]:
        """Reads a key from the specified memory scope (working, session, organizational)."""
        scope = scope.lower()
        if scope == "working":
            val = self._working_memory.get(key)
            logger.debug(f"Working Memory Read: {key} -> {val is not None}")
            return val
        elif scope in ("session", "organizational"):
            item = MeetingRepository.get_memory_item(self.db, scope=scope, key=key)
            logger.debug(f"{scope.capitalize()} Memory Read: {key} -> {item is not None}")
            return item.value if item else None
        else:
            raise ValueError(f"Invalid memory scope: {scope}. Must be working, session, or organizational.")

    def write(self, scope: str, key: str, value: str) -> None:
        """Writes or overwrites a key-value pair in the specified memory scope."""
        scope = scope.lower()
        if scope == "working":
            self._working_memory[key] = value
            logger.debug(f"Working Memory Write: {key}")
        elif scope in ("session", "organizational"):
            MeetingRepository.save_memory_item(self.db, scope=scope, key=key, value=value)
            logger.debug(f"{scope.capitalize()} Memory Write: {key}")
        else:
            raise ValueError(f"Invalid memory scope: {scope}")

    def update(self, scope: str, key: str, value: str) -> None:
        """Updates an existing key-value pair in memory (same as write)."""
        self.write(scope, key, value)

    def delete(self, scope: str, key: str) -> None:
        """Deletes a key from the specified memory scope."""
        scope = scope.lower()
        if scope == "working":
            if key in self._working_memory:
                del self._working_memory[key]
                logger.debug(f"Working Memory Delete: {key}")
        elif scope in ("session", "organizational"):
            deleted = MeetingRepository.delete_memory_item(self.db, scope=scope, key=key)
            logger.debug(f"{scope.capitalize()} Memory Delete: {key} -> {deleted}")
        else:
            raise ValueError(f"Invalid memory scope: {scope}")

    def search(self, query: str, scope: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches for keys or values matching the query in one or all scopes."""
        results = []
        target_scopes = [scope.lower()] if scope else ["working", "session", "organizational"]
        
        for tgt in target_scopes:
            if tgt == "working":
                for k, v in self._working_memory.items():
                    if query.lower() in k.lower() or query.lower() in v.lower():
                        results.append({"scope": "working", "key": k, "value": v})
            elif tgt in ("session", "organizational"):
                db_items = MeetingRepository.search_memory_items(self.db, query, scope=tgt)
                for item in db_items:
                    results.append({"scope": item.scope, "key": item.key, "value": item.value})
                    
        logger.info(f"Memory search for '{query}' in scopes {target_scopes} returned {len(results)} matches.")
        return results

    def summarize(self, scope: str) -> str:
        """Summarizes all content inside the specified scope.
        
        If a Gemini API key is configured, uses the LLM to generate a concise summary.
        Otherwise, returns a formatted list of all keys and values in the scope.
        """
        scope = scope.lower()
        contents = {}
        
        if scope == "working":
            contents = self._working_memory
        elif scope in ("session", "organizational"):
            items = MeetingRepository.search_memory_items(self.db, "", scope=scope)
            contents = {item.key: item.value for item in items}
            
        if not contents:
            return f"The {scope} memory is currently empty."

        text_block = "\n".join([f"- {k}: {v}" for k, v in contents.items()])
        
        # Check if we can summarize using Gemini
        if settings.GEMINI_API_KEY:
            try:
                from google.genai import Client
                client = Client(api_key=settings.GEMINI_API_KEY)
                prompt = (
                    f"You are the memory manager for ActionSync AI. Summarize the following "
                    f"key-value memory data from the '{scope}' scope. Consolidate and extract "
                    f"the key facts, decisions, and task history into a readable report:\n\n{text_block}"
                )
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt
                )
                if response.text:
                    return response.text
            except Exception as e:
                logger.error(f"Failed to summarize memory using LLM: {e}")
                
        # Fallback to structured text block
        return f"Consolidated {scope.capitalize()} Memory:\n\n{text_block}"

    def clear_working_memory(self) -> None:
        self._working_memory.clear()
        logger.info("Cleared working memory.")
