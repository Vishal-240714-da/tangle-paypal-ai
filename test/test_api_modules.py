from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def login(email, password):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )


def get_token(email, password):
    response = login(email, password)
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def get_admin_token():
    return get_token(
        "admin@tangle.com",
        "TangleAdmin123!",
    )


def get_analyst_token():
    return get_token(
        "user@example.com",
        "stringst",
    )


def get_reviewer_token():
    return get_token(
        "reviewer@tangle.com",
        "TangleReviewer123!",
    )


# ============================================================
# CASES
# ============================================================


def test_cases_requires_authentication():
    response = client.get("/api/cases")

    assert response.status_code == 401


def test_cases_accessible_to_authenticated_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/cases",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_case_detail_accessible():
    token = get_analyst_token()

    response = client.get(
        "/api/cases/1",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 404)


def test_case_history_accessible():
    token = get_analyst_token()

    response = client.get(
        "/api/cases/1/history",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 404)


# ============================================================
# INVESTIGATION
# ============================================================


def test_investigation_requires_authentication():
    response = client.get("/api/investigation/1")

    assert response.status_code == 401


def test_investigation_accessible_to_authenticated_user():
    token = get_analyst_token()

    response = client.get(
        "/api/investigation/1",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 404)


# ============================================================
# HUMAN REVIEW
# ============================================================


def test_pending_reviews_requires_authentication():
    response = client.get("/api/reviews/pending")

    assert response.status_code == 401


def test_review_summary_requires_authentication():
    response = client.get("/api/reviews/summary")

    assert response.status_code == 401


def test_pending_reviews_accessible_to_reviewer():
    token = get_reviewer_token()

    response = client.get(
        "/api/reviews/pending",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_review_summary_accessible_to_reviewer():
    token = get_reviewer_token()

    response = client.get(
        "/api/reviews/summary",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_analyst_can_access_pending_reviews():
    token = get_analyst_token()

    response = client.get(
        "/api/reviews/pending",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


# ============================================================
# ANALYTICS
# ============================================================


def test_analytics_summary_requires_authentication():
    response = client.get("/api/analytics/summary")

    assert response.status_code == 401


def test_analytics_risk_requires_authentication():
    response = client.get("/api/analytics/risk")

    assert response.status_code == 401


def test_analytics_exceptions_requires_authentication():
    response = client.get("/api/analytics/exceptions")

    assert response.status_code == 401


def test_analytics_lifecycle_requires_authentication():
    response = client.get("/api/analytics/lifecycle")

    assert response.status_code == 401


def test_analytics_summary_accessible_to_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/analytics/summary",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_analytics_risk_accessible_to_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/analytics/risk",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_analytics_exceptions_accessible_to_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/analytics/exceptions",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_analytics_lifecycle_accessible_to_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/analytics/lifecycle",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


# ============================================================
# DATA QUALITY
# ============================================================


def test_data_quality_requires_authentication():
    response = client.get("/api/data-quality")

    assert response.status_code == 401


def test_data_quality_accessible_to_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/data-quality",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_reviewer_cannot_access_data_quality():
    token = get_reviewer_token()

    response = client.get(
        "/api/data-quality",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


# ============================================================
# RECONCILIATION
# ============================================================


def test_reconciliation_requires_authentication():
    response = client.get("/api/reconciliation")

    assert response.status_code == 401


def test_reconciliation_accessible_to_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/reconciliation",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_reviewer_can_access_reconciliation():
    token = get_reviewer_token()

    response = client.get(
        "/api/reconciliation",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


# ============================================================
# AUDIT TRAIL
# ============================================================


def test_audit_requires_authentication():
    response = client.get("/api/audit/cases/1")

    assert response.status_code == 401


def test_audit_accessible_to_analyst():
    token = get_analyst_token()

    response = client.get(
        "/api/audit/cases/1",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 404)


def test_audit_accessible_to_reviewer():
    token = get_reviewer_token()

    response = client.get(
        "/api/audit/cases/1",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 404)


def test_audit_accessible_to_admin():
    token = get_admin_token()

    response = client.get(
        "/api/audit/cases/1",
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 404)