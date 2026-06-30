from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============================================================================
# Auth & User Schemas
# ============================================================================

class UserBase(BaseModel):
    username: str
    email: str
    role: str = "member"
    security_question_1: str
    security_question_2: str

class UserCreate(UserBase):
    password: str
    security_answer_1: str
    security_answer_2: str

class ResetPasswordRequest(BaseModel):
    username: str
    security_answer_1: str
    security_answer_2: str
    new_password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# ============================================================================
# Segment Schemas
# ============================================================================

class SegmentBase(BaseModel):
    speaker: Optional[str] = None
    text: str
    start_time: float
    end_time: float

class SegmentCreate(SegmentBase):
    pass

class SegmentResponse(SegmentBase):
    id: str
    meeting_id: str

    class Config:
        from_attributes = True

# ============================================================================
# Meeting Schemas
# ============================================================================

class MeetingBase(BaseModel):
    title: str
    date: datetime
    duration: float = 0.0

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    transcript_clean: Optional[str] = None
    executive_summary: Optional[str] = None
    community_impact: Optional[str] = None
    clarification_notes: Optional[str] = None

class MeetingResponse(MeetingBase):
    id: str
    status: str
    transcript_raw: Optional[str] = None
    transcript_clean: Optional[str] = None
    audio_path: Optional[str] = None
    executive_summary: Optional[str] = None
    community_impact: Optional[str] = None
    clarification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# Entity Schemas (Person, Project)
# ============================================================================

class PersonBase(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonResponse(PersonBase):
    id: str

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "Active"

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str

    class Config:
        from_attributes = True

# ============================================================================
# Extracted Intelligence Schemas (Task, Decision, Risk, TimelineEvent)
# ============================================================================

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Pending"
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    assignee_id: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    meeting_id: str
    assignee: Optional[PersonResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DecisionBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Approved"

class DecisionCreate(DecisionBase):
    decider_id: Optional[str] = None

class DecisionResponse(DecisionBase):
    id: str
    meeting_id: str
    decider: Optional[PersonResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RiskBase(BaseModel):
    description: str
    impact_level: str = "Medium"
    mitigation_strategy: Optional[str] = None
    status: str = "Active"

class RiskCreate(RiskBase):
    pass

class RiskResponse(RiskBase):
    id: str
    meeting_id: str

    class Config:
        from_attributes = True

class TimelineEventBase(BaseModel):
    event_date: datetime
    description: str

class TimelineEventCreate(TimelineEventBase):
    project_id: Optional[str] = None

class TimelineEventResponse(TimelineEventBase):
    id: str
    meeting_id: str
    project: Optional[ProjectResponse] = None

    class Config:
        from_attributes = True

class RelationshipBase(BaseModel):
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relation_type: str

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipResponse(RelationshipBase):
    id: str

    class Config:
        from_attributes = True

# ============================================================================
# Memory Schemas
# ============================================================================

class MemoryItemBase(BaseModel):
    scope: str
    key: str
    value: str

class MemoryItemCreate(MemoryItemBase):
    pass

class MemoryItemResponse(MemoryItemBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================================================
# AI Agent Output Schemas (Validated by ADK Output Schemas)
# ============================================================================

class SummarizerOutput(BaseModel):
    executive_summary: str = Field(description="High-level summary of the meeting context and outcomes.")
    key_topics: List[str] = Field(description="Key subject matters discussed during the meeting.")
    meeting_context: str = Field(description="Background and contextual details of the meeting.")

class DecisionItem(BaseModel):
    title: str = Field(description="Title of the decision.")
    description: str = Field(description="Details and context of the decision.")
    decider_name: str = Field(description="Name of the person who made or led the decision. Must be a person's name.")
    status: str = Field(default="Approved", description="Status (Approved, Proposed).")

class DecisionOutput(BaseModel):
    decisions: List[DecisionItem] = Field(default_factory=list, description="List of decisions extracted.")

class TaskItem(BaseModel):
    title: str = Field(description="Short description of the action item.")
    description: str = Field(description="Detailed instructions or specifications for the task.")
    assignee_name: str = Field(description="Name of the person responsible. Must be a specific person's name.")
    status: str = Field(default="Pending", description="Status (Pending, In Progress).")
    deadline: Optional[str] = Field(None, description="Deadline or due date (YYYY-MM-DD format if mentioned).")

class ActionItemOutput(BaseModel):
    tasks: List[TaskItem] = Field(default_factory=list, description="List of action items extracted.")

class TimelineEventItem(BaseModel):
    event_date: str = Field(description="Date or timestamp of the milestone/event (YYYY-MM-DD or relative).")
    description: str = Field(description="Milestone, deadline, or roadmap event details.")
    project_name: str = Field(description="Name of the project this event relates to.")

class TimelineOutput(BaseModel):
    events: List[TimelineEventItem] = Field(default_factory=list, description="Chronological timeline milestones.")

class RiskItem(BaseModel):
    description: str = Field(description="Identified risk, blocker, or delay factor.")
    impact_level: str = Field(description="Severity (Low, Medium, High, Critical).")
    mitigation_strategy: str = Field(description="Proposed mitigation action or solution.")

class RiskOutput(BaseModel):
    risks: List[RiskItem] = Field(default_factory=list, description="List of risks identified.")

class ValidatorOutput(BaseModel):
    is_valid: bool = Field(description="True if all inputs are consistent, complete, and high-quality.")
    errors: List[str] = Field(default_factory=list, description="List of errors or discrepancies detected.")
    reasons: str = Field(description="Rationale for the validation decision.")

class CommunityImpactOutput(BaseModel):
    impact_summary: str = Field(description="Summary of how decisions/actions affect team workload and culture.")
    team_dynamics: str = Field(description="Evaluation of team alignment, collaboration, or potential friction.")
    cultural_alignment: str = Field(description="How decisions match organizational values.")

class AccountabilityOutput(BaseModel):
    accountability_summary: str = Field(description="Overall health check on responsibilities and ownership.")
    assignments_confirmed: List[str] = Field(description="Summary list of who is accountable for what.")
    follow_up_schedule: str = Field(description="Suggested check-in intervals and follow-up timeline.")

class ClarificationOutput(BaseModel):
    is_clarification_needed: bool = Field(description="True if the transcript has unresolved ambiguities.")
    questions: List[str] = Field(default_factory=list, description="Specific follow-up questions to resolve gaps.")

# Consolidated pipeline output
class PipelineOutput(BaseModel):
    summarizer: SummarizerOutput
    decision: DecisionOutput
    action_item: ActionItemOutput
    timeline: TimelineOutput
    risk: RiskOutput
    validator: ValidatorOutput
    community_impact: CommunityImpactOutput
    accountability: AccountabilityOutput
    clarification: ClarificationOutput
