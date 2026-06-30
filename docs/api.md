# API Router Guide: ActionSync AI

This document provides a reference for the REST API endpoints exposed by the ActionSync AI FastAPI backend.

All endpoints are prefixed with `/api`. All endpoints except `/api/health`, `/api/auth/register`, and `/api/auth/token` require a valid JWT token passed in the `Authorization: Bearer <token>` header.

---

## Authentication Router (`/api/auth`)

### 1. Register User
- **Method**: `POST`
- **Path**: `/api/auth/register`
- **Request Body**: `UserCreate` (username, email, password, role)
- **Response**: `UserResponse`

### 2. Retrieve Login Token
- **Method**: `POST`
- **Path**: `/api/auth/token`
- **Request Body**: `OAuth2PasswordRequestForm` (form data: username, password)
- **Response**: `Token` (access_token, token_type)

### 3. Retrieve Current User Profile
- **Method**: `GET`
- **Path**: `/api/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `UserResponse`

---

## Meetings Router (`/api/meetings`)

### 1. Upload Audio File
- **Method**: `POST`
- **Path**: `/api/meetings/upload`
- **Request Body**: `Multipart Form` (title: string, file: UploadFile)
- **Response**: `MeetingResponse`

### 2. List Meetings
- **Method**: `GET`
- **Path**: `/api/meetings`
- **Parameters**: `skip` (default 0), `limit` (default 100)
- **Response**: `List[MeetingResponse]`

### 3. Retrieve Meeting Details
- **Method**: `GET`
- **Path**: `/api/meetings/{meeting_id}`
- **Response**: `MeetingResponse`

### 4. Retrieve Meeting Transcripts
- **Method**: `GET`
- **Path**: `/api/meetings/{meeting_id}/segments`
- **Response**: `List[SegmentResponse]`

### 5. Delete Meeting
- **Method**: `DELETE`
- **Path**: `/api/meetings/{meeting_id}`
- **Response**: Status Code 204

---

## Agent Router (`/api/agents`)

### 1. Process Meeting
- **Method**: `POST`
- **Path**: `/api/agents/process/{meeting_id}`
- **Response**: `{"status": "processing", "message": "..."}`
- **Note**: Triggers Whisper transcription and Google ADK Multi-Agent Orchestrator pipeline in the background.

---

## Memory Router (`/api/memory`)

### 1. Search Memory
- **Method**: `GET`
- **Path**: `/api/memory/search`
- **Parameters**: `query` (string), `scope` (optional: working, session, organizational)
- **Response**: `List[MemoryItemResponse]`

### 2. Summarize Memory Scope
- **Method**: `GET`
- **Path**: `/api/memory/summarize`
- **Parameters**: `scope` (working, session, organizational)
- **Response**: `{"scope": "...", "summary": "..."}`

### 3. Write Memory Item
- **Method**: `POST`
- **Path**: `/api/memory/write`
- **Parameters**: `scope`, `key`, `value`
- **Response**: `{"status": "success", ...}`

---

## Reports Router (`/api/reports`)

### 1. Download Meeting Report
- **Method**: `GET`
- **Path**: `/api/reports/download`
- **Parameters**: `meeting_id` (string), `format` (pdf or markdown)
- **Response**: File stream (application/pdf or text/markdown)

---

## Dashboard Router (`/api/dashboard`)

### 1. Retrieve Dashboard Metrics
- **Method**: `GET`
- **Path**: `/api/dashboard/metrics`
- **Response**: Contains summaries, task completion rates, risk distributions, and recent meetings.

---

## Health Router (`/api/health`)

### 1. Verify Server Health
- **Method**: `GET`
- **Path**: `/api/health`
- **Response**: `{"status": "healthy", "database": "...", "gemini_api": "...", "storage_writable": true}`
- **Note**: Does not require authentication.
