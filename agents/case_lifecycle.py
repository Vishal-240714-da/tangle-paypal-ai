
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import Case, CaseHistory


# ============================================================
# CASE LIFECYCLE
# ============================================================

VALID_STATUSES = {
    "OPEN",
    "INVESTIGATING",
    "PENDING_REVIEW",
    "APPROVED",
    "REJECTED",
    "ESCALATED",
    "RESOLVED",
}


ALLOWED_TRANSITIONS = {
    "OPEN": {
        "INVESTIGATING",
    },

    "INVESTIGATING": {
        "PENDING_REVIEW",
    },

    "PENDING_REVIEW": {
        "APPROVED",
        "REJECTED",
        "ESCALATED",
    },

    "APPROVED": {
        "RESOLVED",
    },

    "REJECTED": {
        "RESOLVED",
    },

    "ESCALATED": {
        "INVESTIGATING",
        "RESOLVED",
    },

    "RESOLVED": set(),
}


# ============================================================
# VALIDATION
# ============================================================

def is_valid_status(status: str) -> bool:
    """
    Check whether a status is a valid TANGLE lifecycle status.
    """
    return status in VALID_STATUSES


def can_transition(
    current_status: str,
    new_status: str,
) -> bool:
    """
    Check whether a case is allowed to move
    from current_status to new_status.
    """

    if not is_valid_status(current_status):
        return False

    if not is_valid_status(new_status):
        return False

    return new_status in ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )


# ============================================================
# IN-MEMORY TRANSITION
# ============================================================

def transition_case(
    current_status: str,
    new_status: str,
) -> dict:
    """
    Validate a lifecycle transition without touching
    the database.
    """

    if not is_valid_status(current_status):
        return {
            "success": False,
            "message": f"Invalid current status: {current_status}",
            "previous_status": current_status,
            "new_status": new_status,
        }

    if not is_valid_status(new_status):
        return {
            "success": False,
            "message": f"Invalid new status: {new_status}",
            "previous_status": current_status,
            "new_status": new_status,
        }

    if not can_transition(
        current_status,
        new_status,
    ):
        return {
            "success": False,
            "message": (
                f"Transition not allowed: "
                f"{current_status} -> {new_status}"
            ),
            "previous_status": current_status,
            "new_status": new_status,
        }

    return {
        "success": True,
        "message": (
            f"Transition allowed: "
            f"{current_status} -> {new_status}"
        ),
        "previous_status": current_status,
        "new_status": new_status,
    }


# ============================================================
# DATABASE TRANSITION USING EXISTING SESSION
# ============================================================

def transition_case_with_session(
    session: Session,
    case_id: str,
    new_status: str,
    changed_by: str = "SYSTEM",
    reason: str | None = None,
) -> dict:
    """
    Perform a lifecycle transition using an existing
    SQLAlchemy session.

    This function does NOT commit or close the session.

    The caller controls the final transaction.

    This allows multiple TANGLE operations, such as:

        Case update
        + CaseHistory
        + Review update

    to be committed atomically.
    """

    case = session.execute(
        select(Case).where(
            Case.case_id == case_id
        )
    ).scalar_one_or_none()

    if case is None:
        return {
            "success": False,
            "message": f"Case not found: {case_id}",
            "case_id": case_id,
        }

    current_status = case.status

    # --------------------------------------------------------
    # Validate new status
    # --------------------------------------------------------

    if not is_valid_status(new_status):
        return {
            "success": False,
            "message": f"Invalid new status: {new_status}",
            "case_id": case_id,
            "previous_status": current_status,
            "new_status": new_status,
        }

    # --------------------------------------------------------
    # Validate transition
    # --------------------------------------------------------

    if not can_transition(
        current_status,
        new_status,
    ):
        return {
            "success": False,
            "message": (
                f"Transition not allowed: "
                f"{current_status} -> {new_status}"
            ),
            "case_id": case_id,
            "previous_status": current_status,
            "new_status": new_status,
        }

    # --------------------------------------------------------
    # Update case
    # --------------------------------------------------------

    now = datetime.utcnow()

    case.status = new_status
    case.updated_at = now

    # --------------------------------------------------------
    # Create audit/history record
    # --------------------------------------------------------

    history = CaseHistory(
        case_id=case_id,
        previous_status=current_status,
        new_status=new_status,
        changed_by=changed_by,
        reason=reason,
        timestamp=now,
    )

    session.add(history)

    # --------------------------------------------------------
    # IMPORTANT:
    # Do NOT commit here.
    #
    # The caller owns the transaction.
    # --------------------------------------------------------

    return {
        "success": True,
        "message": (
            f"Case {case_id} transitioned "
            f"from {current_status} to {new_status}"
        ),
        "case_id": case_id,
        "previous_status": current_status,
        "new_status": new_status,
        "changed_by": changed_by,
        "reason": reason,
    }


# ============================================================
# DATABASE TRANSITION
# ============================================================

def transition_case_in_database(
    case_id: str,
    new_status: str,
    changed_by: str = "SYSTEM",
    reason: str | None = None,
) -> dict:
    """
    Perform a lifecycle transition directly in PostgreSQL.

    This is the standalone convenience version.

    It creates its own session and commits the transition.
    """

    session = SessionLocal()

    try:
        result = transition_case_with_session(
            session=session,
            case_id=case_id,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason,
        )

        if not result["success"]:
            return result

        session.commit()

        return result

    except Exception as exc:
        session.rollback()

        return {
            "success": False,
            "message": "Lifecycle transition failed",
            "error": str(exc),
            "case_id": case_id,
        }

    finally:
        session.close()


# ============================================================
# NEXT POSSIBLE STATUSES
# ============================================================

def get_next_statuses(
    current_status: str,
) -> list[str]:
    """
    Return all valid next statuses for a case.
    """

    if not is_valid_status(current_status):
        return []

    return sorted(
        ALLOWED_TRANSITIONS.get(
            current_status,
            set(),
        )
    )


# ============================================================
# LIFECYCLE DESCRIPTION
# ============================================================

def get_lifecycle_description() -> dict:
    """
    Return the complete TANGLE case lifecycle.
    """

    return {
        "OPEN": [
            "INVESTIGATING",
        ],

        "INVESTIGATING": [
            "PENDING_REVIEW",
        ],

        "PENDING_REVIEW": [
            "APPROVED",
            "REJECTED",
            "ESCALATED",
        ],

        "APPROVED": [
            "RESOLVED",
        ],

        "REJECTED": [
            "RESOLVED",
        ],

        "ESCALATED": [
            "INVESTIGATING",
            "RESOLVED",
        ],

        "RESOLVED": [],
    }


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> None:
    """
    Basic lifecycle validation tests.
    """

    assert is_valid_status("OPEN")
    assert is_valid_status("PENDING_REVIEW")
    assert is_valid_status("RESOLVED")

    assert not is_valid_status("INVALID")

    assert can_transition(
        "OPEN",
        "INVESTIGATING",
    )

    assert can_transition(
        "INVESTIGATING",
        "PENDING_REVIEW",
    )

    assert can_transition(
        "PENDING_REVIEW",
        "APPROVED",
    )

    assert can_transition(
        "PENDING_REVIEW",
        "REJECTED",
    )

    assert can_transition(
        "PENDING_REVIEW",
        "ESCALATED",
    )

    assert not can_transition(
        "OPEN",
        "APPROVED",
    )

    assert not can_transition(
        "RESOLVED",
        "INVESTIGATING",
    )

    print("Case lifecycle self-test passed.")


if __name__ == "__main__":
    run_self_test()
