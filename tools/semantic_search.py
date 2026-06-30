import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from tools.registry import BaseActionSyncTool, tool_registry
from database.models import Segment, Decision, Task
from config.settings import settings

logger = logging.getLogger("actionsync.tools.semantic_search")

class SemanticSearch(BaseActionSyncTool):
    def __init__(self):
        super().__init__(
            name="SemanticSearch",
            description="Performs semantic vector search on transcript segments, decisions, or tasks using SentenceTransformers."
        )
        self.model = None

    def initialize(self) -> None:
        """Loads the SentenceTransformer embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer embedding model 'all-MiniLM-L6-v2'...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.initialized = True
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}. Semantic search will run in keyword fallback mode.")
            self.initialized = True  # Proceed in keyword-matching fallback mode

    def execute(self, db: Session, query: str, meeting_id: Optional[str] = None, search_type: str = "segments", limit: int = 5) -> List[Dict[str, Any]]:
        """Searches database entities (segments, decisions, tasks) using semantic embeddings or keyword fallbacks.
        
        Args:
            db: SQLAlchemy Session.
            query: The search query.
            meeting_id: Optional filter for a specific meeting.
            search_type: "segments", "decisions", or "tasks".
            limit: Maximum results to return.
        """
        logger.info(f"Performing semantic search for: '{query}' (type={search_type})")
        
        if not query.strip():
            return []

        # 1. Fetch search candidates from DB
        candidates = []
        if search_type == "segments":
            q = db.query(Segment)
            if meeting_id:
                q = q.filter(Segment.meeting_id == meeting_id)
            records = q.all()
            candidates = [{"id": r.id, "text": f"{r.speaker or 'Unknown'}: {r.text}", "ref": r} for r in records]
        elif search_type == "decisions":
            q = db.query(Decision)
            if meeting_id:
                q = q.filter(Decision.meeting_id == meeting_id)
            records = q.all()
            candidates = [{"id": r.id, "text": f"{r.title}. {r.description or ''}", "ref": r} for r in records]
        elif search_type == "tasks":
            q = db.query(Task)
            if meeting_id:
                q = q.filter(Task.meeting_id == meeting_id)
            records = q.all()
            candidates = [{"id": r.id, "text": f"{r.title}. {r.description or ''}", "ref": r} for r in records]
        else:
            raise ValueError(f"Invalid search_type: {search_type}")

        if not candidates:
            return []

        # 2. Perform search
        if self.model is not None:
            try:
                from sentence_transformers import util
                # Extract candidate texts
                texts = [c["text"] for c in candidates]
                
                # Compute embeddings
                candidate_embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
                query_embedding = self.model.encode(query, convert_to_tensor=True)
                
                # Calculate cosine similarities
                cos_scores = util.cos_sim(query_embedding, candidate_embeddings)[0]
                
                # Sort candidates by similarity score
                results = []
                for idx, score in enumerate(cos_scores):
                    results.append({
                        "score": float(score),
                        "candidate": candidates[idx]
                    })
                
                results = sorted(results, key=lambda x: x["score"], reverse=True)[:limit]
                
                # Format matches
                formatted_results = []
                for r in results:
                    ref = r["candidate"]["ref"]
                    formatted_results.append({
                        "id": r["candidate"]["id"],
                        "text": r["candidate"]["text"],
                        "score": r["score"],
                        "meeting_id": getattr(ref, "meeting_id", None)
                    })
                return formatted_results
            except Exception as e:
                logger.error(f"Semantic encoding failed: {e}. Falling back to keyword match.")
                
        # 3. Keyword matching fallback
        results = []
        for c in candidates:
            if query.lower() in c["text"].lower():
                results.append({
                    "id": c["id"],
                    "text": c["text"],
                    "score": 1.0,
                    "meeting_id": getattr(c["ref"], "meeting_id", None)
                })
        return results[:limit]

    def validate(self, output: Any) -> bool:
        return isinstance(output, list)

# Register tool
tool_registry.register(SemanticSearch())
