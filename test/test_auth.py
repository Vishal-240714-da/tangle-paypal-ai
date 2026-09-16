import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from backend.main import app
from backend.auth import get_db
from database.models import User


client = TestClient(app)


@pytest.fixture
def cleanup_test_users():
    created_emails = []

    def register_test_user(
        name="Automated Test User",
        role="ANALYST",
    ):
        email = unique_email()

        response = client.post(
            "/auth/register",
            json={
                "name": name,
                "email": email,
                "password": "TestPassword123!",
                "role": role,
            },
        )

        assert response.status_code == 201

        created_emails.append(email)

        return email, response

    yield register_test_user

    db_generator = get_db()
    db = next(db_generator)

    try:
        db.execute(
            delete(User).where(
                User.email.in_(created_emails)
            )
        )
        db.commit()
    finally:
        db.close()


def unique_email():
    return f"test_{uuid.uuid4().hex[:10]}@tangle-test.com"


def login(email, password):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


def get_admin_token():
    response = login(
        "admin@tangle.com",
        "TangleAdmin123!",
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_public_registration_creates_analyst(
    cleanup_test_users,
):
    email, response = cleanup_test_users()

    data = response.json()

    assert data["email"] == email
    assert data["role"] == "ANALYST"
    assert data["is_active"] is True


def test_public_registration_cannot_create_admin(
    cleanup_test_users,
):
    email, response = cleanup_test_users(
        name="Privilege Escalation Test",
        role="ADMIN",
    )

    data = response.json()

    assert data["email"] == email
    assert data["role"] == "ANALYST"


def test_duplicate_email_is_rejected(
    cleanup_test_users,
):
    email, first_response = cleanup_test_users(
        name="Duplicate Test",
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/register",
        json={
            "name": "Duplicate Test Again",
            "email": email,
            "password": "TestPassword123!",
            "role": "ANALYST",
        },
    )

    assert second_response.status_code == 409


def test_analyst_login_succeeds():
    response = login(
        "user@example.com",
        "stringst",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "user@example.com"
    assert data["user"]["role"] == "ANALYST"


def test_admin_login_succeeds():
    response = login(
        "admin@tangle.com",
        "TangleAdmin123!",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["email"] == "admin@tangle.com"
    assert data["user"]["role"] == "ADMIN"


def test_reviewer_login_succeeds():
    response = login(
        "reviewer@tangle.com",
        "TangleReviewer123!",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["email"] == "reviewer@tangle.com"
    assert data["user"]["role"] == "REVIEWER"


def test_invalid_password_is_rejected():
    response = login(
        "admin@tangle.com",
        "WrongPassword123!",
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid email or password."
    )


def test_invalid_jwt_is_rejected():
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid.token.test",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid access token."
    )


def test_auth_me_returns_current_user():
    token = get_admin_token()

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["email"] == "admin@tangle.com"
    assert data["user"]["role"] == "ADMIN"
    assert data["user"]["is_active"] is True


def test_protected_endpoint_requires_authentication():
    response = client.get(
        "/api/dashboard/summary"
    )

    assert response.status_code == 401


def test_analyst_can_access_dashboard():
    response = login(
        "user@example.com",
        "stringst",
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    dashboard_response = client.get(
        "/api/dashboard/summary",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert dashboard_response.status_code == 200


def test_reviewer_cannot_access_data_quality():
    response = login(
        "reviewer@tangle.com",
        "TangleReviewer123!",
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    data_quality_response = client.get(
        "/api/data-quality",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert data_quality_response.status_code == 403


def test_admin_can_access_user_administration():
    token = get_admin_token()

    response = client.get(
        "/api/users",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "users" in data
    assert "total" in data