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
# AUTHENTICATION ERROR HANDLING
# ============================================================


def test_login_with_wrong_password_is_rejected():
    response = login(
        "user@example.com",
        "WrongPassword123!",
    )

    assert response.status_code == 401


def test_login_with_unknown_email_is_rejected():
    response = login(
        "does-not-exist@tangle.com",
        "TestPassword123!",
    )

    assert response.status_code == 401


def test_invalid_jwt_is_rejected():
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid.jwt.token",
        },
    )

    assert response.status_code == 401


def test_missing_bearer_token_is_rejected():
    response = client.get(
        "/api/cases",
        headers={
            "Authorization": "invalid-token",
        },
    )

    assert response.status_code == 401


def test_missing_authorization_header_is_rejected():
    response = client.get("/api/cases")

    assert response.status_code == 401


# ============================================================
# CASE ERROR HANDLING
# ============================================================


def test_case_with_nonexistent_id_returns_not_found():
    token = get_analyst_token()

    response = client.get(
        "/api/cases/CASE-DOES-NOT-EXIST",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_case_history_with_nonexistent_id_returns_not_found():
    token = get_analyst_token()

    response = client.get(
        "/api/cases/CASE-DOES-NOT-EXIST/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


# ============================================================
# RECONCILIATION ERROR HANDLING
# ============================================================


def test_reconciliation_rejects_invalid_match_type():
    token = get_analyst_token()

    response = client.get(
        "/api/reconciliation",
        params={
            "match_type": "INVALID_TYPE",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_reconciliation_accepts_exact_match_type():
    token = get_analyst_token()

    response = client.get(
        "/api/reconciliation",
        params={
            "match_type": "EXACT",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_reconciliation_accepts_fuzzy_match_type():
    token = get_analyst_token()

    response = client.get(
        "/api/reconciliation",
        params={
            "match_type": "FUZZY",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_reconciliation_accepts_merged_payment_match_type():
    token = get_analyst_token()

    response = client.get(
        "/api/reconciliation",
        params={
            "match_type": "MERGED_PAYMENT",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


# ============================================================
# REVIEW ERROR HANDLING
# ============================================================


def test_review_rejects_invalid_decision():
    token = get_reviewer_token()

    response = client.post(
        "/api/reviews/CASE-0001",
        json={
            "reviewer_decision": "INVALID_DECISION",
            "reviewer_comment": "Invalid decision test",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_review_rejects_empty_case_id():
    token = get_reviewer_token()

    response = client.post(
        "/api/reviews/%20",
        json={
            "reviewer_decision": "APPROVE",
            "reviewer_comment": "Empty case ID test",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_review_rejects_missing_decision():
    token = get_reviewer_token()

    response = client.post(
        "/api/reviews/CASE-0001",
        json={
            "reviewer_comment": "Missing decision test",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_review_rejects_invalid_request_body():
    token = get_reviewer_token()

    response = client.post(
        "/api/reviews/CASE-0001",
        json={
            "invalid_field": "invalid",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================
# USER ADMINISTRATION ERROR HANDLING
# ============================================================


def test_user_administration_requires_admin():
    token = get_analyst_token()

    response = client.get(
        "/api/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_user_administration_rejects_invalid_role():
    token = get_admin_token()

    response = client.post(
        "/api/users",
        json={
            "name": "Invalid Role Test",
            "email": "invalid-role-test@tangle.com",
            "password": "TestPassword123!",
            "role": "SUPERADMIN",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_user_administration_rejects_weak_password():
    token = get_admin_token()

    response = client.post(
        "/api/users",
        json={
            "name": "Weak Password Test",
            "email": "weak-password-test@tangle.com",
            "password": "123",
            "role": "ANALYST",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_user_administration_rejects_duplicate_email():
    token = get_admin_token()

    response = client.post(
        "/api/users",
        json={
            "name": "Duplicate Admin Test",
            "email": "admin@tangle.com",
            "password": "TestPassword123!",
            "role": "ANALYST",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 409


def test_user_role_update_rejects_invalid_role():
    token = get_admin_token()

    response = client.patch(
        "/api/users/1/role",
        json={
            "role": "SUPERADMIN",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_user_role_update_returns_not_found_for_unknown_user():
    token = get_admin_token()

    response = client.patch(
        "/api/users/999999/role",
        json={
            "role": "ANALYST",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_user_status_update_returns_not_found_for_unknown_user():
    token = get_admin_token()

    response = client.patch(
        "/api/users/999999/status",
        json={
            "is_active": False,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 404


# ============================================================
# DATA QUALITY / ANALYTICS / AUDIT AUTHORIZATION ERRORS
# ============================================================


def test_reviewer_cannot_access_data_quality():
    token = get_reviewer_token()

    response = client.get(
        "/api/data-quality",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_reviewer_cannot_access_ingestion_status():
    token = get_reviewer_token()

    response = client.get(
        "/api/ingestion/status",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_analyst_cannot_access_user_administration():
    token = get_analyst_token()

    response = client.get(
        "/api/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_reviewer_cannot_access_user_administration():
    token = get_reviewer_token()

    response = client.get(
        "/api/users",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


# ============================================================
# HTTP METHOD / ROUTING ERRORS
# ============================================================


def test_unknown_api_route_returns_not_found():
    token = get_analyst_token()

    response = client.get(
        "/api/this-route-does-not-exist",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_wrong_http_method_returns_method_not_allowed():
    token = get_analyst_token()

    response = client.delete(
        "/api/cases",
        headers=auth_headers(token),
    )

    assert response.status_code == 405