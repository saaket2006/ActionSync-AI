# ADK Agent Guide: ActionSync AI

This document describes the roles, prompt instructions, and output schemas of the nine Google ADK agents configured in the ActionSync AI platform.

---

## 1. Summarizer Agent (`agents/summarizer.py`)
- **Role**: Executive Assistant
- **Instruction**: Synthesizes the meeting transcript to extract the key topics, background context, and a comprehensive high-level summary.
- **Output Schema**: `SummarizerOutput`
  - `executive_summary`: string
  - `key_topics`: list[str]
  - `meeting_context`: string

## 2. Decision Agent (`agents/decision.py`)
- **Role**: Organizational Archivist
- **Instruction**: Analyzes meeting transcripts to identify decisions, consensus points, and agreements.
- **Output Schema**: `DecisionOutput` (list of `DecisionItem`)
  - `title`: string
  - `description`: string
  - `decider_name`: string (person making/leading decision)
  - `status`: string (Approved, Proposed)

## 3. Action Item Agent (`agents/action_item.py`)
- **Role**: Agile Project Manager
- **Instruction**: Extracts tasks, deliverables, assignees, and deadlines.
- **Output Schema**: `ActionItemOutput` (list of `TaskItem`)
  - `title`: string
  - `description`: string
  - `assignee_name`: string (must be person's name)
  - `status`: string (Pending, In Progress)
  - `deadline`: string (YYYY-MM-DD format if mentioned)

## 4. Timeline Agent (`agents/timeline.py`)
- **Role**: Master Scheduler
- **Instruction**: Reconstructs project timelines, milestones, and dates.
- **Output Schema**: `TimelineOutput` (list of `TimelineEventItem`)
  - `event_date`: string (standardized to YYYY-MM-DD)
  - `description`: string
  - `project_name`: string (project context)

## 5. Risk Agent (`agents/risk.py`)
- **Role**: Risk Officer
- **Instruction**: Identifies potential risks, delays, technical blockers, and mitgation strategies.
- **Output Schema**: `RiskOutput` (list of `RiskItem`)
  - `description`: string
  - `impact_level`: string (Low, Medium, High, Critical)
  - `mitigation_strategy`: string

## 6. Validator Agent (`agents/validator.py`)
- **Role**: Quality Assurance Auditor
- **Instruction**: Synthesizes outputs from the 5 parallel extraction agents, identifying gaps, spelling discrepancies, or inconsistencies.
- **Output Schema**: `ValidatorOutput`
  - `is_valid`: boolean
  - `errors`: list[str]
  - `reasons`: string

## 7. Community Impact Agent (`agents/community_impact.py`)
- **Role**: Organizational Psychologist
- **Instruction**: Evaluates the cultural and team impact, assessing workloads, potential burnout, and value alignment.
- **Output Schema**: `CommunityImpactOutput`
  - `impact_summary`: string
  - `team_dynamics`: string (collaboration vs. friction assessment)
  - `cultural_alignment`: string

## 8. Accountability Agent (`agents/accountability.py`)
- **Role**: Execution Lead
- **Instruction**: Confirms deliverable ownership, assignments, and check-in intervals.
- **Output Schema**: `AccountabilityOutput`
  - `accountability_summary`: string
  - `assignments_confirmed`: list[str]
  - `follow_up_schedule`: string

## 9. Clarification Agent (`agents/clarification.py`)
- **Role**: Critical Inquiry Specialist
- **Instruction**: Formulates follow-up questions to resolve critical gaps or ambiguities in transcripts.
- **Output Schema**: `ClarificationOutput`
  - `is_clarification_needed`: boolean
  - `questions`: list[str]
