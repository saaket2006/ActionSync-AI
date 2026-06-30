import os
# Force a separate test database URL before importing app/engine to isolate testing from development data
os.environ["DATABASE_URL"] = "sqlite:///./storage/actionsync_test.db"

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from database.connection import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    # Initialize test schema
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup test database tables
    Base.metadata.drop_all(bind=engine)
    # Remove test database file if possible
    try:
        db_file = "storage/actionsync_test.db"
        if os.path.exists(db_file):
            os.remove(db_file)
    except Exception:
        pass

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "gemini_api" in data

def test_user_registration_and_login():
    # 1. Register test user with security questions
    reg_data = {
        "username": "api_test_user",
        "email": "api_test@example.com",
        "password": "secretpassword",
        "role": "admin",
        "security_question_1": "Where were you born?",
        "security_answer_1": "Boston",
        "security_question_2": "What is your favorite book?",
        "security_answer_2": "1984"
    }
    reg_response = client.post("/api/auth/register", json=reg_data)
    assert reg_response.status_code == 200
    assert reg_response.json()["username"] == "api_test_user"

    # 2. Login to retrieve token
    login_data = {
        "username": "api_test_user",
        "password": "secretpassword"
    }
    login_response = client.post("/api/auth/token", data=login_data)
    assert login_response.status_code == 200
    token_json = login_response.json()
    assert "access_token" in token_json
    assert token_json["token_type"] == "bearer"

    # 3. Retrieve current user profile
    headers = {"Authorization": f"Bearer {token_json['access_token']}"}
    profile_response = client.get("/api/auth/me", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "api_test@example.com"

def test_forgot_password_reset_and_login():
    # 1. Register user
    reg_data = {
        "username": "reset_user",
        "email": "reset@example.com",
        "password": "oldpassword",
        "role": "member",
        "security_question_1": "Where were you born?",
        "security_answer_1": "Paris",
        "security_question_2": "What is your favorite book?",
        "security_answer_2": "Dune"
    }
    reg_res = client.post("/api/auth/register", json=reg_data)
    assert reg_res.status_code == 200

    # 2. Retrieve security questions
    questions_res = client.get("/api/auth/security-questions?username=reset_user")
    assert questions_res.status_code == 200
    questions = questions_res.json()
    assert questions["security_question_1"] == "Where were you born?"
    assert questions["security_question_2"] == "What is your favorite book?"

    # 3. Try to reset with incorrect answers
    reset_data_fail = {
        "username": "reset_user",
        "security_answer_1": "WrongAnswer1",
        "security_answer_2": "WrongAnswer2",
        "new_password": "newpassword123"
    }
    reset_res_fail = client.post("/api/auth/reset-password", json=reset_data_fail)
    assert reset_res_fail.status_code == 400

    # 4. Reset with correct answers
    reset_data_success = {
        "username": "reset_user",
        "security_answer_1": "  paris  ",  # Test case-insensitivity and whitespace stripping
        "security_answer_2": "dune",
        "new_password": "newpassword123"
    }
    reset_res_success = client.post("/api/auth/reset-password", json=reset_data_success)
    assert reset_res_success.status_code == 200

    # 5. Login with new password
    login_res = client.post(
        "/api/auth/token",
        data={"username": "reset_user", "password": "newpassword123"}
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

