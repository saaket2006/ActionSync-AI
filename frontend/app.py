import streamlit as st
import requests
import os
import datetime
import time

# Set up page configurations
st.set_page_config(
    page_title="ActionSync AI - Meeting Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL config
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Initialize session state variables
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Custom CSS for Premium Design
st.markdown("""
<style>
    .main {
        background-color: #0f1116;
        color: #e2e8f0;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
    }
    .card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #60a5fa;
    }
    .tagline {
        color: #94a3b8;
        font-style: italic;
        margin-bottom: 30px;
    }
    .sidebar-header {
        font-size: 22px;
        font-weight: 800;
        color: #3b82f6;
        margin-bottom: 5px;
    }
    /* Fix file uploader overlap and pointer issues */
    div[data-testid="stFileUploaderErrorMessage"] {
        pointer-events: none !important; /* Click-through so it doesn't block the cursor */
        position: relative !important;
        z-index: 1 !important;
    }
    button[data-testid="stFileUploaderDeleteBtn"], 
    button[aria-label="Remove file"],
    .stFileUploader button {
        position: relative !important;
        z-index: 9999 !important;
        pointer-events: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get HTTP headers
def get_headers():
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers

# --- AUTHENTICATION INTERFACE ---
SECURITY_QUESTIONS_1 = [
    "Where were you born?",
    "What was the name of your first pet?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
]

SECURITY_QUESTIONS_2 = [
    "What is your favorite book/game?",
    "What is your favorite movie?",
    "What was your first car?",
]

# --- AUTHENTICATION INTERFACE ---
def show_login_page():
    st.markdown("<h1 style='text-align: center; color: #3b82f6;'>ActionSync AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;' class='tagline'>From Conversations to Accountability</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to your Account")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/auth/token",
                    data={"username": login_username, "password": login_password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.username = login_username
                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again.")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
                
        # Forgot Password Expander
        st.markdown("---")
        with st.expander("🔑 Forgot Password?"):
            st.write("Retrieve your security questions to reset your password.")
            reset_username = st.text_input("Username", key="reset_username")
            
            if "retrieved_username" not in st.session_state:
                st.session_state.retrieved_username = None
                st.session_state.q1 = None
                st.session_state.q2 = None
                
            if st.button("Retrieve Security Questions"):
                if not reset_username.strip():
                    st.warning("Please enter your username first.")
                else:
                    try:
                        res = requests.get(f"{BACKEND_URL}/api/auth/security-questions?username={reset_username}")
                        if res.status_code == 200:
                            questions = res.json()
                            st.session_state.retrieved_username = reset_username
                            st.session_state.q1 = questions["security_question_1"]
                            st.session_state.q2 = questions["security_question_2"]
                            st.success("Questions retrieved successfully!")
                        else:
                            st.error("Username not found.")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")
                        
            # If questions are loaded, show verification form
            if st.session_state.retrieved_username == reset_username and st.session_state.q1:
                st.markdown("---")
                st.markdown(f"**Question 1:** {st.session_state.q1}")
                ans1 = st.text_input("Answer 1", type="password", key="reset_ans_1")
                
                st.markdown(f"**Question 2:** {st.session_state.q2}")
                ans2 = st.text_input("Answer 2", type="password", key="reset_ans_2")
                
                new_pass = st.text_input("New Password", type="password", key="reset_new_pass")
                
                if st.button("Reset Password"):
                    if not ans1.strip() or not ans2.strip() or not new_pass.strip():
                        st.warning("Please fill in all fields.")
                    else:
                        try:
                            payload = {
                                "username": reset_username,
                                "security_answer_1": ans1,
                                "security_answer_2": ans2,
                                "new_password": new_pass
                            }
                            res = requests.post(f"{BACKEND_URL}/api/auth/reset-password", json=payload)
                            if res.status_code == 200:
                                st.success("Password reset successfully! You can now log in.")
                                # Clear state
                                st.session_state.retrieved_username = None
                                st.session_state.q1 = None
                                st.session_state.q2 = None
                            else:
                                err = res.json().get("detail", "Password reset failed. Check answers.")
                                st.error(err)
                        except Exception as e:
                            st.error(f"Error resetting password: {e}")
                            
    with tab2:
        st.subheader("Create a New Account")
        reg_username = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_role = st.selectbox("Role", ["member", "manager", "admin"])
        
        st.markdown("---")
        st.markdown("**Security Verification Questions**")
        st.markdown("*These will be used if you need to reset your password.*")
        
        q1 = st.selectbox("Security Question 1", SECURITY_QUESTIONS_1)
        a1 = st.text_input("Answer 1", type="password", key="reg_ans_1")
        
        q2 = st.selectbox("Security Question 2", SECURITY_QUESTIONS_2)
        a2 = st.text_input("Answer 2", type="password", key="reg_ans_2")
        
        if st.button("Create Account"):
            if not reg_username.strip() or not reg_email.strip() or not reg_password.strip():
                st.error("Please fill in username, email, and password.")
            elif not a1.strip() or not a2.strip():
                st.error("Please answer both security questions.")
            else:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/auth/register",
                        json={
                            "username": reg_username,
                            "email": reg_email,
                            "password": reg_password,
                            "role": reg_role,
                            "security_question_1": q1,
                            "security_answer_1": a1,
                            "security_question_2": q2,
                            "security_answer_2": a2
                        }
                    )
                    if response.status_code == 200:
                        st.success("Account created successfully! Please switch to the Login tab.")
                    else:
                        err_msg = response.json().get("detail", "Registration failed.")
                        st.error(err_msg)
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

# --- DASHBOARD PAGE ---
def show_dashboard():
    st.title("📊 Organizational Analytics")
    st.markdown("<p class='tagline'>Real-time dashboard of task completion, decision rates, and meeting metadata.</p>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/dashboard/metrics", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            summary = data["summary"]
            risk_dist = data["risk_distribution"]
            recent = data["recent_meetings"]
            
            # Metric Columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='card'><p>Total Meetings</p><p class='metric-value'>{summary['total_meetings']}</p></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='card'><p>Active Projects</p><p class='metric-value'>{summary['active_projects']}</p></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='card'><p>Pending Tasks</p><p class='metric-value'>{summary['pending_tasks']}</p></div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='card'><p>Total Decisions</p><p class='metric-value'>{summary['total_decisions']}</p></div>", unsafe_allow_html=True)
                
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("📈 Execution Progress")
                st.markdown(f"**Task Completion Rate:** {summary['task_completion_rate']}%")
                st.progress(summary['task_completion_rate'] / 100.0)
                
                st.subheader("⚠️ Active Risk Distribution")
                r_col1, r_col2, r_col3 = st.columns(3)
                r_col1.metric("High/Critical", risk_dist["high"])
                r_col2.metric("Medium", risk_dist["medium"])
                r_col3.metric("Low", risk_dist["low"])
                
            with col_right:
                st.subheader("📂 Recent Meetings")
                if recent:
                    for m in recent:
                        status_color = "🟢" if m["status"] == "Completed" else "🟡" if m["status"] == "Processing" else "🔴"
                        st.markdown(f"{status_color} **{m['title']}** - {m['date'][:10]} (*{m['status']}*)")
                else:
                    st.info("No meetings processed yet. Go to the Upload section to start.")
        else:
            st.error("Failed to load dashboard metrics. Verify backend health.")
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

# --- UPLOAD MEETING PAGE ---
def show_upload():
    st.title("📤 Upload Meeting Audio")
    st.markdown("<p class='tagline'>Upload audio files (mp3, wav, m4a) to transcribe and execute the multi-agent intelligence pipeline.</p>", unsafe_allow_html=True)
    
    meeting_title = st.text_input("Meeting Title", placeholder="e.g. Q3 Roadmap Kick-off")
    uploaded_file = st.file_uploader("Select Meeting Audio File", type=["mp3", "wav", "m4a", "mp4", "ogg"])
    
    if st.button("Upload & Process"):
        if not meeting_title.strip() or not uploaded_file:
            st.warning("Please fill in the title and select an audio file first.")
            return
            
        with st.spinner("Uploading audio file to backend..."):
            try:
                # 1. Upload file
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"title": meeting_title}
                
                upload_res = requests.post(
                    f"{BACKEND_URL}/api/meetings/upload",
                    data=data,
                    files=files,
                    headers=get_headers()
                )
                
                if upload_res.status_code == 201:
                    meeting = upload_res.json()
                    meeting_id = meeting["id"]
                    st.success(f"File uploaded successfully!")
                    
                    # 2. Trigger background processing
                    proc_res = requests.post(
                        f"{BACKEND_URL}/api/agents/process/{meeting_id}",
                        headers=get_headers()
                    )
                    
                    if proc_res.status_code == 202:
                        st.success("AI Agents have started transcribing and extracting meeting intelligence in the background. Redirecting...")
                        st.session_state.selected_meeting_id = meeting_id
                        st.session_state.page = "Meeting History"
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Failed to trigger agent analysis pipeline.")
                else:
                    st.error(f"Upload failed: {upload_res.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error communicating with backend: {e}")

# --- MEETING HISTORY PAGE ---
def show_history():
    st.title("📂 Meeting Archival History")
    st.markdown("<p class='tagline'>Search through all processed meetings, view executive reports, extracted decisions, and timeline milestones.</p>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/meetings", headers=get_headers())
        if response.status_code != 200:
            st.error("Failed to load meetings list.")
            return
            
        meetings = response.json()
        if not meetings:
            st.info("No meetings found in the archives. Please upload a meeting audio file.")
            return
            
        # Select meeting to inspect
        meeting_options = {m["title"]: m for m in meetings}
        meeting_titles = list(meeting_options.keys())
        
        default_index = 0
        target_meeting_id = st.session_state.get("selected_meeting_id")
        if target_meeting_id:
            for idx, m in enumerate(meetings):
                if m["id"] == target_meeting_id:
                    default_index = idx
                    break
                    
        selected_title = st.selectbox("Select a meeting to view details:", meeting_titles, index=default_index)
        selected_meeting = meeting_options[selected_title]
        st.session_state.selected_meeting_id = selected_meeting["id"]
        m_id = selected_meeting["id"]
        
        # Detail header
        st.markdown("---")
        
        # Meeting title and status layout
        status_emoji = "🟢" if selected_meeting["status"] == "Completed" else "🟡" if selected_meeting["status"] == "Processing" else "🔴"
        
        col_header, col_delete = st.columns([4, 1])
        with col_header:
            st.header(f"{status_emoji} {selected_meeting['title']}")
            st.write(f"**Date:** {selected_meeting['date'][:10]} | **Status:** {selected_meeting['status']}")
        
        with col_delete:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Delete", key=f"del_{m_id}"):
                st.session_state.confirm_delete = m_id
                
        # Handle deletion confirmation
        if st.session_state.get("confirm_delete") == m_id:
            st.warning("⚠️ Are you sure you want to permanently delete this meeting and all its extracted intelligence?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, Delete", key=f"confirm_yes_{m_id}"):
                    try:
                        res = requests.delete(f"{BACKEND_URL}/api/meetings/{m_id}", headers=get_headers())
                        if res.status_code in (200, 204):
                            st.success("Meeting deleted successfully!")
                            st.session_state.confirm_delete = None
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Failed to delete meeting."))
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")
            with col_no:
                if st.button("Cancel", key=f"confirm_no_{m_id}"):
                    st.session_state.confirm_delete = None
                    st.rerun()
                    
        # State-based early returns (after delete check)
        if selected_meeting["status"] == "Processing":
            st.warning("This meeting is currently being processed by the Whisper and Google ADK Agent pipeline. Waiting for completion...")
            try:
                # Perform a blocking wait call to the backend (long polling)
                wait_res = requests.get(
                    f"{BACKEND_URL}/api/meetings/wait/{m_id}",
                    headers=get_headers(),
                    timeout=600  # 10 minutes timeout
                )
                if wait_res.status_code == 200:
                    st.rerun()
            except Exception as e:
                st.error(f"Lost connection to backend: {e}")
                if st.button("Refresh Page", key=f"refresh_{m_id}"):
                    st.rerun()
            return
        elif selected_meeting["status"] == "Failed":
            err_msg = selected_meeting.get("error_message") or "Unknown error. Please check server logs."
            st.error(f"Processing failed for this meeting: {err_msg}")
            return

        # Action Buttons (Downloads)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Download PDF Report"):
                report_res = requests.get(f"{BACKEND_URL}/api/reports/download?meeting_id={m_id}&format=pdf", headers=get_headers())
                if report_res.status_code == 200:
                    st.download_button("Click here to download PDF", data=report_res.content, file_name=f"{selected_title}.pdf", mime="application/pdf")
                else:
                    st.error("Failed to download PDF.")
        with col2:
            if st.button("📥 Download Markdown Report"):
                report_res = requests.get(f"{BACKEND_URL}/api/reports/download?meeting_id={m_id}&format=markdown", headers=get_headers())
                if report_res.status_code == 200:
                    st.download_button("Click here to download Markdown", data=report_res.content, file_name=f"{selected_title}.md", mime="text/markdown")
                else:
                    st.error("Failed to download Markdown.")
                    
        # Tabs for details
        tab_sum, tab_dec, tab_tsk, tab_rsk, tab_timeline, tab_transcript = st.tabs([
            "📝 Executive Summary", 
            "⚖️ Decisions", 
            "✅ Action Items", 
            "⚠️ Risks", 
            "📅 Timeline", 
            "📜 Transcript"
        ])
        
        with tab_sum:
            st.subheader("Executive Summary")
            st.write(selected_meeting["executive_summary"] or "No summary generated.")
            st.subheader("Team & Cultural Impact")
            st.write(selected_meeting["community_impact"] or "No impact assessment generated.")
            
        with tab_dec:
            st.subheader("Extracted Decisions")
            # Fetch segments or entities
            dec_res = requests.get(f"{BACKEND_URL}/api/meetings/{m_id}", headers=get_headers())  # Fetching links if any
            # Query db details: for simplicity, we query backend router endpoints
            # We can request details of decisions from backend `/api/meetings` links
            # To fetch tasks, decisions, risks for a specific meeting, let's display them
            # Wait, let's call semantic search or fetch entities related to this meeting!
            # Since we have semantic search in backend `/api/memory/search` or `/api/meetings/{m_id}/segments`,
            # we can show the details. Let's do a request to the backend database via a custom fetch or display summaries
            # Wait, the summary and impact are already inside selected_meeting!
            # What about decisions? We can display them if we query the SQL database.
            # Let's see if we have an endpoint in `meetings.py` for segments, yes: `/meetings/{meeting_id}/segments`.
            # Let's show the raw segments if needed.
            # For decisions/tasks, we can search using Semantic Search or filter.
            # Let's show search results or retrieve lists of tasks.
            # Let's perform a query for decisions with meeting_id!
            # We can use our `/api/memory/search?query=Decision&scope=session` or similar,
            # but wait, let's search for decisions in this meeting!
            # Let's call `/api/memory/search?query=Decision&scope=session`
            dec_search = requests.get(f"{BACKEND_URL}/api/memory/search?query={m_id}&scope=session", headers=get_headers())
            if dec_search.status_code == 200:
                memories = dec_search.json()
                # Render keys and values from session memory
                decisions_found = False
                for item in memories:
                    if "decision" in item["key"].lower():
                        decisions_found = True
                        st.markdown(f"**{item['key'].replace(m_id + '_', '').capitalize()}**")
                        st.write(item["value"])
                if not decisions_found:
                    st.info("No structured decisions persisted in memory for this session.")
            else:
                st.info("No decisions stored in memory.")

        with tab_tsk:
            st.subheader("Action Items")
            dec_search = requests.get(f"{BACKEND_URL}/api/memory/search?query={m_id}&scope=session", headers=get_headers())
            if dec_search.status_code == 200:
                memories = dec_search.json()
                tasks_found = False
                for item in memories:
                    if "task" in item["key"].lower() or "action" in item["key"].lower():
                        tasks_found = True
                        st.markdown(f"**{item['key'].replace(m_id + '_', '').capitalize()}**")
                        st.write(item["value"])
                if not tasks_found:
                    st.info("No action items persisted in memory for this session.")

        with tab_rsk:
            st.subheader("Risks & Blockers")
            dec_search = requests.get(f"{BACKEND_URL}/api/memory/search?query={m_id}&scope=session", headers=get_headers())
            if dec_search.status_code == 200:
                memories = dec_search.json()
                risks_found = False
                for item in memories:
                    if "risk" in item["key"].lower():
                        risks_found = True
                        st.markdown(f"**{item['key'].replace(m_id + '_', '').capitalize()}**")
                        st.write(item["value"])
                if not risks_found:
                    st.info("No risks persisted in memory for this session.")

        with tab_timeline:
            st.subheader("Project Timelines & Dates")
            dec_search = requests.get(f"{BACKEND_URL}/api/memory/search?query={m_id}&scope=session", headers=get_headers())
            if dec_search.status_code == 200:
                memories = dec_search.json()
                timeline_found = False
                for item in memories:
                    if "timeline" in item["key"].lower():
                        timeline_found = True
                        st.markdown(f"**{item['key'].replace(m_id + '_', '').capitalize()}**")
                        st.write(item["value"])
                if not timeline_found:
                    st.info("No timeline milestones persisted in memory.")

        with tab_transcript:
            st.subheader("Transcribed Conversation")
            seg_res = requests.get(f"{BACKEND_URL}/api/meetings/{m_id}/segments", headers=get_headers())
            if seg_res.status_code == 200:
                segments = seg_res.json()
                for s in segments:
                    # Format time as mm:ss
                    start_min = int(s['start_time'] // 60)
                    start_sec = int(s['start_time'] % 60)
                    time_stamp = f"{start_min:02d}:{start_sec:02d}"
                    st.markdown(f"**[{time_stamp}] {s['speaker'] or 'Unknown'}:** {s['text']}")
            else:
                st.write(selected_meeting["transcript_raw"] or "No transcript generated.")

    except Exception as e:
        st.error(f"Error loading meeting archives: {e}")

# --- SEARCH & MEMORY PAGE ---
def show_search():
    st.title("🔍 Semantic Query & Org Memory")
    st.markdown("<p class='tagline'>Search across all transcripts, organizational memory, and vector embeddings using semantic search.</p>", unsafe_allow_html=True)
    
    query = st.text_input("Enter Search Phrase", placeholder="e.g. Who is responsible for the database schema?")
    search_type = st.radio("Search Category", ["segments", "decisions", "tasks"])
    
    if st.button("Query Database"):
        if not query.strip():
            st.warning("Please enter a search query first.")
            return
            
        with st.spinner("Searching semantic database..."):
            try:
                # Query semantic search tool via memory search API
                response = requests.get(
                    f"{BACKEND_URL}/api/memory/search?query={query}",
                    headers=get_headers()
                )
                
                if response.status_code == 200:
                    results = response.json()
                    st.subheader(f"Results for '{query}'")
                    if results:
                        for idx, res in enumerate(results, 1):
                            with st.expander(f"Match {idx} (Scope: {res['scope']}, Key: {res['key']})"):
                                st.write(res["value"])
                    else:
                        st.info("No semantically relevant results found.")
                else:
                    st.error("Failed to query semantic memory.")
            except Exception as e:
                st.error(f"Error querying backend: {e}")

# --- SETTINGS PAGE ---
def show_settings():
    st.title("⚙️ System Settings")
    st.markdown("<p class='tagline'>View and verify Google ADK Agent settings, database connection status, and directory layouts.</p>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/settings", headers=get_headers())
        h_response = requests.get(f"{BACKEND_URL}/api/health")
        
        if response.status_code == 200 and h_response.status_code == 200:
            config = response.json()
            health = h_response.json()
            
            st.subheader("🤖 AI Model Orchestrator")
            st.write(f"**Gemini Model:** `{config['GEMINI_MODEL']}`")
            st.write(f"**Whisper Model:** `{config['WHISPER_MODEL_NAME']}`")
            st.write(f"**Google Gemini API Status:** `{'🟢 Configured' if health['gemini_api'] == 'configured' else '🔴 Missing'}`")
            
            st.subheader("💾 Database & Paths")
            st.write(f"**Database Connection String:** `{config['DATABASE_URL']}`")
            st.write(f"**Storage Directory:** `{config['STORAGE_DIR']}`")
            st.write(f"**Database Status:** `{'🟢 Healthy' if 'healthy' in health['database'] else '🔴 Unhealthy'}`")
            st.write(f"**Storage Writable:** `{'🟢 Yes' if health['storage_writable'] else '🔴 No'}`")
        else:
            st.error("Failed to load settings. Verify backend is running.")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

# --- MAIN APP LAYOUT & ROUTING ---
def main():
    if not st.session_state.token:
        # Show login page if not authenticated
        show_login_page()
    else:
        # Sidebar Navigation
        with st.sidebar:
            st.markdown("<div class='sidebar-header'>ActionSync AI</div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:12px; color:#94a3b8; font-style:italic;'>From Conversations to Accountability</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Page routing buttons
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
            if st.button("📤 Upload Meeting", use_container_width=True):
                st.session_state.page = "Upload Meeting"
                st.rerun()
            if st.button("📂 Meeting History", use_container_width=True):
                st.session_state.page = "Meeting History"
                st.rerun()
            if st.button("🔍 Search & Memory", use_container_width=True):
                st.session_state.page = "Search & Memory"
                st.rerun()
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.page = "Settings"
                st.rerun()
                
            st.markdown("---")
            st.write(f"Logged in as: **{st.session_state.username}**")
            if st.button("🔒 Logout", use_container_width=True):
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.page = "Dashboard"
                st.rerun()
                
        # Main page routing
        if st.session_state.page == "Dashboard":
            show_dashboard()
        elif st.session_state.page == "Upload Meeting":
            show_upload()
        elif st.session_state.page == "Meeting History":
            show_history()
        elif st.session_state.page == "Search & Memory":
            show_search()
        elif st.session_state.page == "Settings":
            show_settings()

if __name__ == "__main__":
    main()
