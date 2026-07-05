import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.connection import Base, engine, get_db
from database.models import Meeting
from sqlalchemy.orm import Session
import uuid
import datetime

client = TestClient(app)

def test_wait_route():
    # Initialize schema
    Base.metadata.create_all(bind=engine)
    
    # Get db session
    db = next(get_db())
    
    # Create a meeting
    meeting_id = str(uuid.uuid4())
    db_meeting = Meeting(
        id=meeting_id,
        title="Test wait meeting",
        date=datetime.datetime.utcnow(),
        status="Completed"
    )
    db.add(db_meeting)
    db.commit()
    
    # Query wait route
    # First, let's log in to get access token (wait route depends on get_current_user)
    # We can mock current_user or create a user. Let's register and login:
    reg_data = {
        "username": "wait_test_user",
        "email": "wait_test@example.com",
        "password": "secretpassword",
        "role": "admin",
        "security_question_1": "Q1",
        "security_answer_1": "A1",
        "security_question_2": "Q2",
        "security_answer_2": "A2"
    }
    client.post("/api/auth/register", json=reg_data)
    login_res = client.post("/api/auth/token", data={"username": "wait_test_user", "password": "secretpassword"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Query wait route
    url = f"/api/meetings/wait/{meeting_id}"
    print(f"Requesting wait route: {url}")
    response = client.get(url, headers=headers)
    print("Response status code:", response.status_code)
    print("Response body:", response.json())
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    test_wait_route()
