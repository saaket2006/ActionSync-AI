import datetime
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from database.connection import Base

# Association Table for Person to Project (many-to-many)
person_project_association = Table(
    "person_project",
    Base.metadata,
    Column("person_id", String(36), ForeignKey("people.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", String(36), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), default="member")  # admin, manager, member
    security_question_1 = Column(String(255), nullable=False)
    hashed_security_answer_1 = Column(String(255), nullable=False)
    security_question_2 = Column(String(255), nullable=False)
    hashed_security_answer_2 = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    duration = Column(Float, default=0.0)  # in seconds
    transcript_raw = Column(Text, nullable=True)
    transcript_clean = Column(Text, nullable=True)
    audio_path = Column(String(255), nullable=True)
    status = Column(String(50), default="Pending")  # Pending, Processing, Completed, Failed
    executive_summary = Column(Text, nullable=True)
    community_impact = Column(Text, nullable=True)
    clarification_notes = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    segments = relationship("Segment", back_populates="meeting", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="meeting", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="meeting", cascade="all, delete-orphan")

class Segment(Base):
    __tablename__ = "segments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker = Column(String(100), nullable=True)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)  # seconds from start
    end_time = Column(Float, nullable=False)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="segments")

class Person(Base):
    __tablename__ = "people"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)  # job title / organizational role
    
    # Relationships
    tasks = relationship("Task", back_populates="assignee")
    decisions = relationship("Decision", back_populates="decider")
    projects = relationship("Project", secondary=person_project_association, back_populates="members")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="Active")  # Active, Completed, On Hold
    
    # Relationships
    members = relationship("Person", secondary=person_project_association, back_populates="projects")
    timeline_events = relationship("TimelineEvent", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(String(36), ForeignKey("people.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="Pending")  # Pending, In Progress, Completed, Delayed
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="tasks")
    assignee = relationship("Person", back_populates="tasks")

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    decider_id = Column(String(36), ForeignKey("people.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="Approved")  # Proposed, Approved, Superseded
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="decisions")
    decider = relationship("Person", back_populates="decisions")

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    impact_level = Column(String(20), default="Medium")  # Low, Medium, High, Critical
    mitigation_strategy = Column(Text, nullable=True)
    status = Column(String(50), default="Active")  # Active, Mitigated, Ignored
    
    # Relationships
    meeting = relationship("Meeting", back_populates="risks")

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    event_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="timeline_events")
    project = relationship("Project", back_populates="timeline_events")

class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_type = Column(String(50), nullable=False)  # Person, Project, Meeting, Task, Decision, Risk
    source_id = Column(String(36), nullable=False)
    target_type = Column(String(50), nullable=False)  # Person, Project, Meeting, Task, Decision, Risk
    target_id = Column(String(36), nullable=False)
    relation_type = Column(String(100), nullable=False)  # ASSIGNED_TO, DECIDED_BY, MITIGATES, RELATES_TO, PART_OF

class MemoryItem(Base):
    __tablename__ = "memory_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope = Column(String(50), nullable=False, index=True)  # session, organizational
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)  # JSON or raw text
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
