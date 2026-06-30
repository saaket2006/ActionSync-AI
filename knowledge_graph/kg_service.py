import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import networkx as nx
from config.settings import settings

logger = logging.getLogger("actionsync.knowledge_graph")

class BaseKnowledgeGraphService(ABC):
    """Abstract Base Class for the Knowledge Graph Service.
    
    Allows swapping the backend implementation (e.g. from NetworkX to Neo4j) 
    without changing agent or repository code.
    """
    @abstractmethod
    def add_node(self, node_id: str, node_type: str, name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def add_edge(self, source_id: str, target_id: str, relation_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def remove_node(self, node_id: str) -> None:
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_relationships(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def search_graph(self, query: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def persist(self) -> None:
        pass

    @abstractmethod
    def load(self) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class NetworkXKnowledgeGraphService(BaseKnowledgeGraphService):
    """NetworkX implementation of the Knowledge Graph Service for development and testing.
    
    Persists the graph to a JSON file specified in the settings.
    """
    def __init__(self, file_path: str = settings.KNOWLEDGE_GRAPH_PATH):
        self.file_path = file_path
        self.graph = nx.DiGraph()
        self.load()

    def add_node(self, node_id: str, node_type: str, name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        props = properties or {}
        self.graph.add_node(
            node_id, 
            type=node_type, 
            name=name, 
            **props
        )
        logger.debug(f"Added node: {node_id} ({node_type})")

    def add_edge(self, source_id: str, target_id: str, relation_type: str, properties: Optional[Dict[str, Any]] = None) -> None:
        props = properties or {}
        # Ensure source and target nodes exist (create with defaults if missing)
        if not self.graph.has_node(source_id):
            self.graph.add_node(source_id, type="Unknown", name=source_id)
        if not self.graph.has_node(target_id):
            self.graph.add_node(target_id, type="Unknown", name=target_id)
            
        self.graph.add_edge(
            source_id, 
            target_id, 
            relation=relation_type, 
            **props
        )
        logger.debug(f"Added edge: {source_id} -> {target_id} ({relation_type})")

    def remove_node(self, node_id: str) -> None:
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            logger.debug(f"Removed node: {node_id}")

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self.graph.has_node(node_id):
            node_data = self.graph.nodes[node_id]
            return {"id": node_id, **node_data}
        return None

    def get_relationships(self) -> List[Dict[str, Any]]:
        relationships = []
        for u, v, data in self.graph.edges(data=True):
            relationships.append({
                "source": u,
                "target": v,
                "relation_type": data.get("relation", "RELATES_TO"),
                "properties": {k: val for k, val in data.items() if k != "relation"}
            })
        return relationships

    def search_graph(self, query: str) -> Dict[str, Any]:
        """Search the graph for nodes matching the query and return a subgraph."""
        query_lower = query.lower()
        matching_nodes = []
        
        for node_id, data in self.graph.nodes(data=True):
            name = data.get("name", "").lower()
            node_type = data.get("type", "").lower()
            
            if query_lower in node_id.lower() or query_lower in name or query_lower in node_type:
                matching_nodes.append(node_id)
                
        # Include direct neighbors
        neighbors = set()
        for node in matching_nodes:
            neighbors.update(self.graph.successors(node))
            neighbors.update(self.graph.predecessors(node))
            
        all_nodes = set(matching_nodes).union(neighbors)
        subgraph = self.graph.subgraph(all_nodes)
        
        return self._to_dict(subgraph)

    def persist(self) -> None:
        """Saves the NetworkX graph to a JSON file."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            data = nx.readwrite.json_graph.node_link_data(self.graph)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Persisted knowledge graph to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to persist knowledge graph: {e}")

    def load(self) -> None:
        """Loads the NetworkX graph from a JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.graph = nx.readwrite.json_graph.node_link_graph(data)
                logger.info(f"Loaded knowledge graph from {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load knowledge graph from {self.file_path}, starting fresh: {e}")
                self.graph = nx.DiGraph()
        else:
            logger.info("No knowledge graph file found, initializing empty graph.")
            self.graph = nx.DiGraph()

    def clear(self) -> None:
        self.graph.clear()
        self.persist()

    def _to_dict(self, graph_obj: nx.DiGraph) -> Dict[str, Any]:
        """Convert a NetworkX graph into a serialized dictionary format."""
        nodes = []
        for n, data in graph_obj.nodes(data=True):
            nodes.append({
                "id": n,
                "name": data.get("name", n),
                "type": data.get("type", "Unknown"),
                "properties": {k: v for k, v in data.items() if k not in ("name", "type")}
            })
            
        edges = []
        for u, v, data in graph_obj.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relation_type": data.get("relation", "RELATES_TO"),
                "properties": {k: val for k, val in data.items() if k != "relation"}
            })
            
        return {"nodes": nodes, "edges": edges}

    def export_graph_data(self) -> Dict[str, Any]:
        """Export the entire graph for frontend visualization."""
        return self._to_dict(self.graph)
