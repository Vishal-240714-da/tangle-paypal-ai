from datetime import datetime

import pytest

from agents.case_lifecycle import (
    transition_case_in_database,
)
from agents.review_manager import review_case
from database.connection import SessionLocal
from database.models import Case, CaseHistory, Review


def _create_test_case(case_id: str) -> None:
    session = SessionLocal()

    try:
        case = Case(
            case_id=case_id,
            record_type="TEST",
            record_id=case_id,
            invoice_id=None,
            category="TEST_CASE",
            confidence=0.95,
            suggested_action="INVESTIGATE",
            reason="Automated transaction test case.",
            next_action="Review test case.",
            status="PENDING_REVIEW",
            risk_level="MEDIUM",
            priority_score=50,
            human_review_required=True,
        )

        session.add(case)
        session.commit()

    finally:
        session.rollback()
        session.close()


def _delete_test_case(case_id: str) -> None:
    session = SessionLocal()

    try:
        session.query(CaseHistory).filter(
            CaseHistory.case_id == case_id
        ).delete(synchronize_session=False)

        session.query(Review).filter(
            Review.case_id == case_id
        ).delete(synchronize_session=False)

        session.query(Case).filter(
            Case.case_id == case_id
        ).delete(synchronize_session=False)

        session.commit()

    finally:
        session.rollback()
        session.close()


def _get_case(case_id: str):
    session = SessionLocal()

    try:
        return session.query(Case).filter(
            Case.case_id == case_id
        ).first()

    finally:
        session.close()


def _get_review(case_id: str):
    session = SessionLocal()

    try:
        return session.query(Review).filter(
            Review.case_id == case_id
        ).first()

    finally:
        session.close()


def _get_history(case_id: str):
    session = SessionLocal()

    try:
        return (
            session.query(CaseHistory)
            .filter(CaseHistory.case_id == case_id)
            .order_by(CaseHistory.id)
            .all()
        )

    finally:
        session.close()


def test_review_case_approve_updates_case_review_and_history():
    case_id = "TEST-REVIEW-APPROVE-001"

    try:
        _create_test_case(case_id)

        result = review_case(
            case_id=case_id,
            reviewer_decision="APPROVE",
            reviewer_comment="Approved during automated test.",
            reviewer="TEST-REVIEWER",
        )

        assert result["case_id"] == case_id
        assert result["review_status"] == "COMPLETED"
        assert result["reviewer_decision"] == "APPROVE"
        assert result["reviewer_comment"] == (
            "Approved during automated test."
        )
        assert result["case_status"] == "APPROVED"
        assert result["final_status"] == "APPROVED"

        case = _get_case(case_id)
        review = _get_review(case_id)
        history = _get_history(case_id)

        assert case is not None
        assert case.status == "APPROVED"

        assert review is not None
        assert review.review_status == "COMPLETED"
        assert review.reviewer == "TEST-REVIEWER"
        assert review.decision == "APPROVE"
        assert review.comment == (
            "Approved during automated test."
        )

        assert len(history) == 1
        assert history[0].previous_status == "PENDING_REVIEW"
        assert history[0].new_status == "APPROVED"
        assert history[0].changed_by == "TEST-REVIEWER"

    finally:
        _delete_test_case(case_id)


def test_review_case_reject_updates_case_review_and_history():
    case_id = "TEST-REVIEW-REJECT-001"

    try:
        _create_test_case(case_id)

        result = review_case(
            case_id=case_id,
            reviewer_decision="REJECT",
            reviewer_comment="Rejected during automated test.",
            reviewer="TEST-REVIEWER",
        )

        assert result["review_status"] == "COMPLETED"
        assert result["reviewer_decision"] == "REJECT"
        assert result["case_status"] == "REJECTED"
        assert result["final_status"] == "REJECTED"

        case = _get_case(case_id)
        review = _get_review(case_id)
        history = _get_history(case_id)

        assert case.status == "REJECTED"
        assert review.review_status == "COMPLETED"
        assert review.decision == "REJECT"
        assert review.reviewer == "TEST-REVIEWER"

        assert len(history) == 1
        assert history[0].previous_status == "PENDING_REVIEW"
        assert history[0].new_status == "REJECTED"

    finally:
        _delete_test_case(case_id)


def test_review_case_escalate_updates_case_review_and_history():
    case_id = "TEST-REVIEW-ESCALATE-001"

    try:
        _create_test_case(case_id)

        result = review_case(
            case_id=case_id,
            reviewer_decision="ESCALATE",
            reviewer_comment="Escalated during automated test.",
            reviewer="TEST-REVIEWER",
        )

        assert result["review_status"] == "COMPLETED"
        assert result["reviewer_decision"] == "ESCALATE"
        assert result["case_status"] == "ESCALATED"
        assert result["final_status"] == "ESCALATED"

        case = _get_case(case_id)
        review = _get_review(case_id)
        history = _get_history(case_id)

        assert case.status == "ESCALATED"
        assert review.review_status == "COMPLETED"
        assert review.decision == "ESCALATE"

        assert len(history) == 1
        assert history[0].previous_status == "PENDING_REVIEW"
        assert history[0].new_status == "ESCALATED"

    finally:
        _delete_test_case(case_id)


def test_review_case_creates_review_when_review_is_missing():
    case_id = "TEST-REVIEW-CREATE-001"

    try:
        _create_test_case(case_id)

        assert _get_review(case_id) is None

        result = review_case(
            case_id=case_id,
            reviewer_decision="APPROVE",
            reviewer_comment="Created review automatically.",
            reviewer="TEST-REVIEWER",
        )

        assert result["review_status"] == "COMPLETED"

        review = _get_review(case_id)

        assert review is not None
        assert review.case_id == case_id
        assert review.review_status == "COMPLETED"
        assert review.reviewer_decision == "APPROVE"
        assert review.final_status == "APPROVED"

    finally:
        _delete_test_case(case_id)


def test_review_case_normalizes_decision_and_reviewer():
    case_id = "TEST-REVIEW-NORMALIZE-001"

    try:
        _create_test_case(case_id)

        result = review_case(
            case_id=f"  {case_id}  ",
            reviewer_decision="  approve  ",
            reviewer_comment="  Normalized comment  ",
            reviewer="  TEST-REVIEWER  ",
        )

        assert result["case_id"] == case_id
        assert result["reviewer_decision"] == "APPROVE"
        assert result["reviewer_comment"] == (
            "Normalized comment"
        )

        review = _get_review(case_id)

        assert review.reviewer == "TEST-REVIEWER"
        assert review.decision == "APPROVE"

    finally:
        _delete_test_case(case_id)


def test_review_case_rejects_missing_case_id():
    with pytest.raises(ValueError, match="Case ID is required"):
        review_case(
            case_id="",
            reviewer_decision="APPROVE",
        )


def test_review_case_rejects_invalid_decision():
    with pytest.raises(
        ValueError,
        match="Invalid reviewer decision",
    ):
        review_case(
            case_id="TEST-NOT-USED",
            reviewer_decision="INVALID",
        )


def test_review_case_rejects_nonexistent_case():
    case_id = "TEST-REVIEW-NONEXISTENT-001"

    with pytest.raises(
        ValueError,
        match=f"Case {case_id} not found",
    ):
        review_case(
            case_id=case_id,
            reviewer_decision="APPROVE",
        )


def test_review_case_prevents_duplicate_completed_review():
    case_id = "TEST-REVIEW-DUPLICATE-001"

    try:
        _create_test_case(case_id)

        first_result = review_case(
            case_id=case_id,
            reviewer_decision="APPROVE",
            reviewer="FIRST-REVIEWER",
        )

        assert first_result["review_status"] == "COMPLETED"

        with pytest.raises(
            ValueError,
            match="has already been reviewed",
        ):
            review_case(
                case_id=case_id,
                reviewer_decision="REJECT",
                reviewer="SECOND-REVIEWER",
            )

        case = _get_case(case_id)
        review = _get_review(case_id)
        history = _get_history(case_id)

        assert case.status == "APPROVED"
        assert review.reviewer_decision == "APPROVE"
        assert review.reviewer == "FIRST-REVIEWER"
        assert len(history) == 1

    finally:
        _delete_test_case(case_id)


def test_review_case_rolls_back_when_lifecycle_transition_fails():
    case_id = "TEST-REVIEW-ROLLBACK-001"

    try:
        _create_test_case(case_id)

        # Move the case to RESOLVED first.
        session = SessionLocal()

        try:
            case = session.query(Case).filter(
                Case.case_id == case_id
            ).first()

            case.status = "RESOLVED"
            session.commit()

        finally:
            session.rollback()
            session.close()

        with pytest.raises(ValueError):
            review_case(
                case_id=case_id,
                reviewer_decision="APPROVE",
                reviewer_comment="This should fail.",
                reviewer="TEST-REVIEWER",
            )

        case = _get_case(case_id)
        review = _get_review(case_id)
        history = _get_history(case_id)

        assert case.status == "RESOLVED"

        # Review creation must also be rolled back.
        assert review is None

        assert history == []

    finally:
        _delete_test_case(case_id)


def test_review_case_uses_system_reviewer_when_reviewer_is_blank():
    case_id = "TEST-REVIEW-SYSTEM-001"

    try:
        _create_test_case(case_id)

        result = review_case(
            case_id=case_id,
            reviewer_decision="APPROVE",
            reviewer_comment="System reviewer test.",
            reviewer="   ",
        )

        assert result["review_status"] == "COMPLETED"

        review = _get_review(case_id)

        assert review.reviewer == "SYSTEM"

        history = _get_history(case_id)

        assert len(history) == 1
        assert history[0].changed_by == "SYSTEM"

    finally:
        _delete_test_case(case_id)