import logging

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import Case, CaseHistory

logger = logging.getLogger(__name__)


def derive_audit_action(
    previous_status: str | None,
    new_status: str,
    reason: str | None,
) -> str:
    """
    Convert a lifecycle transition into a
    human-readable audit action.
    """

    normalized_reason = (
        (reason or "").strip().upper()
    )

    if "HUMAN REVIEW" in normalized_reason:
        return "HUMAN_REVIEW"

    if (
        previous_status is None
        and new_status == "PENDING_REVIEW"
    ):
        return "CASE_CREATED"

    if new_status == "INVESTIGATING":
        return "INVESTIGATION_STARTED"

    if new_status == "PENDING_REVIEW":
        return "SUBMITTED_FOR_REVIEW"

    if new_status == "APPROVED":
        return "CASE_APPROVED"

    if new_status == "REJECTED":
        return "CASE_REJECTED"

    if new_status == "ESCALATED":
        return "CASE_ESCALATED"

    if new_status == "RESOLVED":
        return "CASE_RESOLVED"

    return "STATUS_CHANGED"


def get_audit_trail(case_id: str) -> dict:
    """
    Return the complete chronological audit trail
    for a TANGLE case.
    """

    case_id = case_id.strip()

    if not case_id:
        raise ValueError(
            "Case ID cannot be empty."
        )

    session = SessionLocal()

    try:
        # ------------------------------------------------
        # Verify case exists
        # ------------------------------------------------

        case = session.get(
            Case,
            case_id,
        )

        if case is None:
            raise LookupError(
                f"Case {case_id} not found."
            )

        # ------------------------------------------------
        # Load lifecycle history
        # ------------------------------------------------

        history = session.scalars(
            select(CaseHistory)
            .where(
                CaseHistory.case_id == case_id
            )
            .order_by(
                CaseHistory.timestamp.asc(),
                CaseHistory.id.asc(),
            )
        ).all()

        # ------------------------------------------------
        # Transform lifecycle records into audit events
        # ------------------------------------------------

        events = []

        for item in history:
            events.append(
                {
                    "id": item.id,
                    "case_id": item.case_id,
                    "previous_status": (
                        item.previous_status
                    ),
                    "new_status": item.new_status,
                    "changed_by": item.changed_by,
                    "action": derive_audit_action(
                        item.previous_status,
                        item.new_status,
                        item.reason,
                    ),
                    "reason": item.reason,
                    "timestamp": item.timestamp,
                }
            )

        logger.info(
            "Audit trail retrieved: "
            "case_id=%s events=%s current_status=%s",
            case_id,
            len(events),
            case.status,
        )

        return {
            "case_id": case_id,
            "current_status": case.status,
            "total_events": len(events),
            "events": events,
        }

    finally:
        session.close()