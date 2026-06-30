import logging
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from tools.registry import BaseActionSyncTool, tool_registry
from repositories.entity_repository import EntityRepository
from repositories.meeting_repository import MeetingRepository
from knowledge_graph.kg_service import NetworkXKnowledgeGraphService, BaseKnowledgeGraphService

logger = logging.getLogger("actionsync.tools.kg_builder")

class KnowledgeGraphBuilder(BaseActionSyncTool):
    def __init__(self, kg_service: Optional[BaseKnowledgeGraphService] = None):
        super().__init__(
            name="KnowledgeGraphBuilder",
            description="Updates the SQL database and NetworkX knowledge graph with extracted meeting intelligence."
        )
        self.kg_service = kg_service or NetworkXKnowledgeGraphService()

    def initialize(self) -> None:
        self.kg_service.load()
        self.initialized = True
        logger.info("Knowledge Graph Builder Tool initialized.")

    def execute(self, db: Session, meeting_id: str, pipeline_output: Dict[str, Any]) -> bool:
        """Parses parallel agent outputs and inserts them into SQL DB and NetworkX Graph.
        
        Args:
            db: SQLAlchemy Session.
            meeting_id: The ID of the meeting being processed.
            pipeline_output: A dictionary containing outputs from the agents:
              - summarizer: SummarizerOutput
              - decision: DecisionOutput
              - action_item: ActionItemOutput
              - timeline: TimelineOutput
              - risk: RiskOutput
        """
        logger.info(f"Building knowledge graph for meeting ID: {meeting_id}")
        
        meeting = MeetingRepository.get_meeting(db, meeting_id)
        if not meeting:
            raise ValueError(f"Meeting with ID {meeting_id} not found.")

        # Extract agent data blocks
        summarizer_data = pipeline_output.get("summarizer", {})
        decision_data = pipeline_output.get("decision", {})
        action_item_data = pipeline_output.get("action_item", {})
        timeline_data = pipeline_output.get("timeline", {})
        risk_data = pipeline_output.get("risk", {})

        # --- 1. Add Meeting Node to Graph ---
        self.kg_service.add_node(
            node_id=meeting.id,
            node_type="Meeting",
            name=meeting.title,
            properties={"date": meeting.date.isoformat(), "status": meeting.status}
        )

        # --- 2. Process Decisions ---
        for dec_item in decision_data.get("decisions", []):
            title = dec_item.get("title")
            desc = dec_item.get("description", "")
            decider_name = dec_item.get("decider_name", "Unknown")
            status = dec_item.get("status", "Approved")

            # DB insertion
            decider_person = EntityRepository.get_or_create_person(db, name=decider_name)
            db_decision = EntityRepository.create_decision(
                db, 
                meeting_id=meeting.id, 
                title=title, 
                description=desc, 
                decider_id=decider_person.id,
                status=status
            )

            # Graph Nodes & Edges
            self.kg_service.add_node(
                node_id=db_decision.id,
                node_type="Decision",
                name=title,
                properties={"status": status}
            )
            self.kg_service.add_node(
                node_id=decider_person.id,
                node_type="Person",
                name=decider_person.name,
                properties={"role": decider_person.role}
            )
            
            # Relations
            self.kg_service.add_edge(meeting.id, db_decision.id, "DECIDED_IN")
            self.kg_service.add_edge(db_decision.id, decider_person.id, "DECIDED_BY")

        # --- 3. Process Action Items (Tasks) ---
        for task_item in action_item_data.get("tasks", []):
            title = task_item.get("title")
            desc = task_item.get("description", "")
            assignee_name = task_item.get("assignee_name", "Unknown")
            status = task_item.get("status", "Pending")
            deadline_str = task_item.get("deadline")
            
            deadline = None
            if deadline_str:
                try:
                    # Parse YYYY-MM-DD
                    deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d")
                except ValueError:
                    pass

            # DB insertion
            assignee_person = EntityRepository.get_or_create_person(db, name=assignee_name)
            db_task = EntityRepository.create_task(
                db, 
                meeting_id=meeting.id, 
                title=title, 
                description=desc, 
                assignee_id=assignee_person.id,
                deadline=deadline,
                status=status
            )

            # Graph Nodes & Edges
            self.kg_service.add_node(
                node_id=db_task.id,
                node_type="Task",
                name=title,
                properties={"status": status, "deadline": deadline_str or ""}
            )
            self.kg_service.add_node(
                node_id=assignee_person.id,
                node_type="Person",
                name=assignee_person.name,
                properties={"role": assignee_person.role}
            )
            
            # Relations
            self.kg_service.add_edge(meeting.id, db_task.id, "ASSIGNED_IN")
            self.kg_service.add_edge(db_task.id, assignee_person.id, "ASSIGNED_TO")

        # --- 4. Process Risks ---
        for risk_item in risk_data.get("risks", []):
            desc = risk_item.get("description")
            impact = risk_item.get("impact_level", "Medium")
            mitigation = risk_item.get("mitigation_strategy", "")

            # DB insertion
            db_risk = EntityRepository.create_risk(
                db, 
                meeting_id=meeting.id, 
                description=desc, 
                impact_level=impact, 
                mitigation_strategy=mitigation,
                status="Active"
            )

            # Graph Nodes & Edges
            self.kg_service.add_node(
                node_id=db_risk.id,
                node_type="Risk",
                name=desc[:30] + "..." if len(desc) > 30 else desc,
                properties={"description": desc, "impact": impact, "mitigation": mitigation}
            )
            
            # Relations
            self.kg_service.add_edge(meeting.id, db_risk.id, "RISK_IDENTIFIED")

        # --- 5. Process Timeline Events & Projects ---
        for event_item in timeline_data.get("events", []):
            date_str = event_item.get("event_date")
            desc = event_item.get("description")
            project_name = event_item.get("project_name", "General")

            event_date = None
            if date_str:
                try:
                    event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    # Default to meeting date if unparseable
                    event_date = meeting.date
            else:
                event_date = meeting.date

            # DB Project & Event
            db_project = EntityRepository.get_or_create_project(db, name=project_name)
            db_event = EntityRepository.create_timeline_event(
                db, 
                meeting_id=meeting.id, 
                event_date=event_date, 
                description=desc, 
                project_id=db_project.id
            )

            # Graph Nodes & Edges
            self.kg_service.add_node(
                node_id=db_project.id,
                node_type="Project",
                name=db_project.name,
                properties={"status": db_project.status}
            )
            self.kg_service.add_node(
                node_id=db_event.id,
                node_type="Timeline",
                name=desc[:30] + "..." if len(desc) > 30 else desc,
                properties={"date": event_date.isoformat()}
            )
            
            # Relations
            self.kg_service.add_edge(meeting.id, db_event.id, "EVENT_OCCURRED")
            self.kg_service.add_edge(db_event.id, db_project.id, "PART_OF_PROJECT")

        # Persist graph state
        self.kg_service.persist()
        return True

    def validate(self, output: Any) -> bool:
        return isinstance(output, bool) and output is True

# Register tool
tool_registry.register(KnowledgeGraphBuilder())
