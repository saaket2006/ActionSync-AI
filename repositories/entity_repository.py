from sqlalchemy.orm import Session
from database.models import Person, Project, Task, Decision, Risk, TimelineEvent, Relationship
from typing import List, Optional, Any
import datetime

class EntityRepository:
    # --- Person ---
    @staticmethod
    def get_person_by_name(db: Session, name: str) -> Optional[Person]:
        return db.query(Person).filter(Person.name == name).first()

    @staticmethod
    def get_or_create_person(db: Session, name: str, email: Optional[str] = None, role: Optional[str] = None) -> Person:
        person = EntityRepository.get_person_by_name(db, name)
        if not person:
            person = Person(name=name, email=email, role=role)
            db.add(person)
            db.commit()
            db.refresh(person)
        else:
            # Update email/role if provided and not set
            updated = False
            if email and not person.email:
                person.email = email
                updated = True
            if role and not person.role:
                person.role = role
                updated = True
            if updated:
                db.commit()
                db.refresh(person)
        return person

    @staticmethod
    def get_people(db: Session) -> List[Person]:
        return db.query(Person).all()

    # --- Project ---
    @staticmethod
    def get_project_by_name(db: Session, name: str) -> Optional[Project]:
        return db.query(Project).filter(Project.name == name).first()

    @staticmethod
    def get_or_create_project(db: Session, name: str, description: Optional[str] = None, status: str = "Active") -> Project:
        project = EntityRepository.get_project_by_name(db, name)
        if not project:
            project = Project(name=name, description=description, status=status)
            db.add(project)
            db.commit()
            db.refresh(project)
        else:
            if description and not project.description:
                project.description = description
                db.commit()
                db.refresh(project)
        return project

    @staticmethod
    def get_projects(db: Session) -> List[Project]:
        return db.query(Project).all()

    # --- Task ---
    @staticmethod
    def create_task(
        db: Session, 
        meeting_id: str, 
        title: str, 
        description: Optional[str] = None, 
        assignee_id: Optional[str] = None, 
        deadline: Optional[datetime.datetime] = None, 
        status: str = "Pending"
    ) -> Task:
        task = Task(
            meeting_id=meeting_id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            deadline=deadline,
            status=status
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_tasks(db: Session) -> List[Task]:
        return db.query(Task).all()

    @staticmethod
    def get_tasks_for_meeting(db: Session, meeting_id: str) -> List[Task]:
        return db.query(Task).filter(Task.meeting_id == meeting_id).all()

    @staticmethod
    def update_task_status(db: Session, task_id: str, status: str) -> Optional[Task]:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            task.updated_at = datetime.datetime.utcnow()
            db.commit()
            db.refresh(task)
        return task

    # --- Decision ---
    @staticmethod
    def create_decision(
        db: Session, 
        meeting_id: str, 
        title: str, 
        description: Optional[str] = None, 
        decider_id: Optional[str] = None, 
        status: str = "Approved"
    ) -> Decision:
        decision = Decision(
            meeting_id=meeting_id,
            title=title,
            description=description,
            decider_id=decider_id,
            status=status
        )
        db.add(decision)
        db.commit()
        db.refresh(decision)
        return decision

    @staticmethod
    def get_decisions_for_meeting(db: Session, meeting_id: str) -> List[Decision]:
        return db.query(Decision).filter(Decision.meeting_id == meeting_id).all()

    # --- Risk ---
    @staticmethod
    def create_risk(
        db: Session, 
        meeting_id: str, 
        description: str, 
        impact_level: str = "Medium", 
        mitigation_strategy: Optional[str] = None, 
        status: str = "Active"
    ) -> Risk:
        risk = Risk(
            meeting_id=meeting_id,
            description=description,
            impact_level=impact_level,
            mitigation_strategy=mitigation_strategy,
            status=status
        )
        db.add(risk)
        db.commit()
        db.refresh(risk)
        return risk

    @staticmethod
    def get_risks_for_meeting(db: Session, meeting_id: str) -> List[Risk]:
        return db.query(Risk).filter(Risk.meeting_id == meeting_id).all()

    # --- Timeline Event ---
    @staticmethod
    def create_timeline_event(
        db: Session, 
        meeting_id: str, 
        event_date: datetime.datetime, 
        description: str, 
        project_id: Optional[str] = None
    ) -> TimelineEvent:
        event = TimelineEvent(
            meeting_id=meeting_id,
            event_date=event_date,
            description=description,
            project_id=project_id
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_timeline_for_meeting(db: Session, meeting_id: str) -> List[TimelineEvent]:
        return db.query(TimelineEvent).filter(TimelineEvent.meeting_id == meeting_id).order_by(TimelineEvent.event_date.asc()).all()

    # --- Relationship ---
    @staticmethod
    def create_relationship(
        db: Session, 
        source_type: str, 
        source_id: str, 
        target_type: str, 
        target_id: str, 
        relation_type: str
    ) -> Relationship:
        # Check if identical relationship already exists
        rel = db.query(Relationship).filter(
            Relationship.source_type == source_type,
            Relationship.source_id == source_id,
            Relationship.target_type == target_type,
            Relationship.target_id == target_id,
            Relationship.relation_type == relation_type
        ).first()
        if not rel:
            rel = Relationship(
                source_type=source_type,
                source_id=source_id,
                target_type=target_type,
                target_id=target_id,
                relation_type=relation_type
            )
            db.add(rel)
            db.commit()
            db.refresh(rel)
        return rel

    @staticmethod
    def get_relationships(db: Session) -> List[Relationship]:
        return db.query(Relationship).all()
