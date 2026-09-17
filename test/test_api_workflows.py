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
# AUTHENTICATED USER WORKFLOW
# ============================================================


def test_login_to_current_user_workflow():
    response = login(
        "user@example.com",
        "stringst",
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    assert token
    assert response.json()["token_type"].lower() == "bearer"

    me_response = client.get(
        "/auth/me",
        headers=auth_headers(token),
    )

    assert me_response.status_code == 200

    user = me_response.json()["user"]

    assert user["email"] == "user@example.com"
    assert user["role"] == "ANALYST"
    assert user["is_active"] is True

# ============================================================
# CASE → INVESTIGATION → HISTORY → AUDIT
# ============================================================


def test_case_to_investigation_history_and_audit_workflow():
    token = get_analyst_token()
    headers = auth_headers(token)

    cases_response = client.get(
        "/api/cases",
        headers=headers,
    )

    assert cases_response.status_code == 200

    cases_data = cases_response.json()

    assert cases_data is not None

    # The endpoint may return either a list or a wrapped response.
    if isinstance(cases_data, list):
        cases = cases_data
    elif isinstance(cases_data, dict):
        cases = (
            cases_data.get("cases")
            or cases_data.get("data")
            or cases_data.get("items")
            or []
        )
    else:
        cases = []

    assert len(cases) > 0

    first_case = cases[0]

    if isinstance(first_case, dict):
        case_id = (
            first_case.get("case_id")
            or first_case.get("id")
        )
    else:
        case_id = first_case

    assert case_id is not None

    # Case detail
    detail_response = client.get(
        f"/api/cases/{case_id}",
        headers=headers,
    )

    assert detail_response.status_code == 200

    detail = detail_response.json()

    assert detail is not None

    # Investigation
    investigation_response = client.get(
        f"/api/investigation/{case_id}",
        headers=headers,
    )

    assert investigation_response.status_code == 200

    investigation = investigation_response.json()

    assert investigation is not None

    # Case history
    history_response = client.get(
        f"/api/cases/{case_id}/history",
        headers=headers,
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert history is not None

    # Audit trail
    audit_response = client.get(
        f"/api/audit/cases/{case_id}",
        headers=headers,
    )

    assert audit_response.status_code == 200

    audit = audit_response.json()

    assert audit is not None


# ============================================================
# ANALYTICS WORKFLOW
# ============================================================


def test_authenticated_user_can_move_from_cases_to_analytics():
    token = get_analyst_token()
    headers = auth_headers(token)

    cases_response = client.get(
        "/api/cases",
        headers=headers,
    )

    assert cases_response.status_code == 200

    analytics_summary = client.get(
        "/api/analytics/summary",
        headers=headers,
    )

    assert analytics_summary.status_code == 200
    assert analytics_summary.json() is not None

    analytics_risk = client.get(
        "/api/analytics/risk",
        headers=headers,
    )

    assert analytics_risk.status_code == 200
    assert analytics_risk.json() is not None

    analytics_exceptions = client.get(
        "/api/analytics/exceptions",
        headers=headers,
    )

    assert analytics_exceptions.status_code == 200
    assert analytics_exceptions.json() is not None

    analytics_lifecycle = client.get(
        "/api/analytics/lifecycle",
        headers=headers,
    )

    assert analytics_lifecycle.status_code == 200
    assert analytics_lifecycle.json() is not None


# ============================================================
# REVIEW QUEUE WORKFLOW
# ============================================================


def test_reviewer_can_load_review_workspace():
    token = get_reviewer_token()
    headers = auth_headers(token)

    pending_response = client.get(
        "/api/reviews/pending",
        headers=headers,
    )

    assert pending_response.status_code == 200

    pending = pending_response.json()

    assert pending is not None

    summary_response = client.get(
        "/api/reviews/summary",
        headers=headers,
    )

    assert summary_response.status_code == 200

    summary = summary_response.json()

    assert summary is not None


# ============================================================
# DATA QUALITY → RECONCILIATION WORKFLOW
# ============================================================


def test_analyst_can_move_from_data_quality_to_reconciliation():
    token = get_analyst_token()
    headers = auth_headers(token)

    quality_response = client.get(
        "/api/data-quality",
        headers=headers,
    )

    assert quality_response.status_code == 200

    quality = quality_response.json()

    assert quality is not None

    reconciliation_response = client.get(
        "/api/reconciliation",
        headers=headers,
    )

    assert reconciliation_response.status_code == 200

    reconciliation = reconciliation_response.json()

    assert reconciliation is not None