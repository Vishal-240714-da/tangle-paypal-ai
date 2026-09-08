from datetime import datetime

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import Case, RiskAssessment, Review

from agents.case_lifecycle import (
    transition_case_with_session,
)


ALLOWED_DECISIONS = {
    "APPROVE",
    "REJECT",
    "ESCALATE",
}


def normalize_string(value):
    if value is None:
        return ""

    return str(value).strip()


def load_reviews():
    session = SessionLocal()

    try:
        return session.scalars(
            select(Review).order_by(Review.id)
        ).all()

    finally:
        session.close()


def get_pending_reviews():
    session = SessionLocal()

    try:
        results = session.execute(
            select(Review, RiskAssessment)
            .join(
                RiskAssessment,
                Review.case_id == RiskAssessment.case_id,
            )
            .where(
                Review.review_status == "PENDING"
            )
            .order_by(
                RiskAssessment.priority_score.desc()
            )
        ).all()

        pending = []

        for review, risk in results:
            pending.append(
                {
                    "case_id": review.case_id,
                    "risk_level": risk.risk_level,
                    "priority_score": risk.priority_score,
                    "human_review_required": risk.human_review_required,
                    "case_status": review.case_status,
                    "review_status": review.review_status,
                    "reviewer_decision": review.reviewer_decision,
                    "reviewer_comment": review.reviewer_comment,
                    "reviewed_at": review.reviewed_at,
                    "final_status": review.final_status,
                }
            )

        return pending

    finally:
        session.close()


def review_case(
    case_id,
    reviewer_decision,
    reviewer_comment="",
    reviewer="SYSTEM",
):
    """
    Process a human review and synchronize:

        Review
        Case
        CaseHistory

    inside one database transaction.
    """

    case_id = normalize_string(case_id)

    reviewer_decision = normalize_string(
        reviewer_decision
    ).upper()

    reviewer_comment = normalize_string(
        reviewer_comment
    )

    reviewer = normalize_string(
        reviewer
    ) or "SYSTEM"

    # --------------------------------------------------------
    # Input validation
    # --------------------------------------------------------

    if not case_id:
        raise ValueError("Case ID is required.")

    if reviewer_decision not in ALLOWED_DECISIONS:
        raise ValueError(
            "Invalid reviewer decision. "
            "Allowed values are: APPROVE, REJECT, ESCALATE."
        )

    # --------------------------------------------------------
    # Decision -> lifecycle status
    # --------------------------------------------------------

    decision_to_status = {
        "APPROVE": "APPROVED",
        "REJECT": "REJECTED",
        "ESCALATE": "ESCALATED",
    }

    new_case_status = decision_to_status[
        reviewer_decision
    ]

    session = SessionLocal()

    try:
        # ----------------------------------------------------
        # Find case
        # ----------------------------------------------------

        case = session.scalar(
            select(Case).where(
                Case.case_id == case_id
            )
        )

        if case is None:
            raise ValueError(
                f"Case {case_id} not found."
            )

        # ----------------------------------------------------
        # Find review
        # ----------------------------------------------------

        review = session.scalar(
            select(Review).where(
                Review.case_id == case_id
            )
        )

        # ----------------------------------------------------
        # Prevent duplicate review
        # ----------------------------------------------------

        if (
            review is not None
            and review.review_status == "COMPLETED"
        ):
            raise ValueError(
                f"Case {case_id} has already been reviewed."
            )

        # ----------------------------------------------------
        # Create review if missing
        # ----------------------------------------------------

        if review is None:
            review = Review(
                case_id=case_id,
                case_status=case.status,
                review_status="PENDING",
                reviewer_decision=None,
                reviewer_comment=None,
                reviewed_at=None,
                final_status=case.status,
                reviewer=reviewer,
                decision=None,
                comment=None,
                created_at=datetime.utcnow(),
            )

            session.add(review)

            # Make the new Review visible to the transaction.
            session.flush()

        # ----------------------------------------------------
        # Use the TANGLE lifecycle engine
        # ----------------------------------------------------

        lifecycle_result = transition_case_with_session(
            session=session,
            case_id=case_id,
            new_status=new_case_status,
            changed_by=reviewer,
            reason=(
                f"Human review decision: "
                f"{reviewer_decision}"
            ),
        )

        if not lifecycle_result["success"]:
            raise ValueError(
                lifecycle_result["message"]
            )

        # ----------------------------------------------------
        # Update legacy Review fields
        # ----------------------------------------------------

        review.case_status = new_case_status
        review.review_status = "COMPLETED"
        review.reviewer_decision = reviewer_decision
        review.reviewer_comment = reviewer_comment
        review.reviewed_at = datetime.utcnow()
        review.final_status = new_case_status

        # ----------------------------------------------------
        # Update Phase 2 semantic fields
        # ----------------------------------------------------

        review.reviewer = reviewer
        review.decision = reviewer_decision
        review.comment = reviewer_comment

        # ----------------------------------------------------
        # ONE atomic commit
        # ----------------------------------------------------

        session.commit()

        return {
            "case_id": review.case_id,
            "review_status": review.review_status,
            "reviewer_decision": review.reviewer_decision,
            "reviewer_comment": (
                review.reviewer_comment or ""
            ),
            "reviewed_at": (
                review.reviewed_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if review.reviewed_at
                else None
            ),
            "case_status": review.case_status,
            "final_status": review.final_status,
        }

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_review_summary():
    reviews = load_reviews()

    total_reviews = len(reviews)

    pending = sum(
        1
        for review in reviews
        if review.review_status == "PENDING"
    )

    completed = sum(
        1
        for review in reviews
        if review.review_status == "COMPLETED"
    )

    approved = sum(
        1
        for review in reviews
        if review.reviewer_decision == "APPROVE"
    )

    rejected = sum(
        1
        for review in reviews
        if review.reviewer_decision == "REJECT"
    )

    escalated = sum(
        1
        for review in reviews
        if review.reviewer_decision == "ESCALATE"
    )

    return {
        "total_reviews": total_reviews,
        "pending": pending,
        "completed": completed,
        "approved": approved,
        "rejected": rejected,
        "escalated": escalated,
    }


def create_review_queue():
    """
    Ensure every risk assessment requiring human review
    has a corresponding Review record.
    """

    session = SessionLocal()

    try:
        risk_assessments = session.scalars(
            select(RiskAssessment).where(
                RiskAssessment.human_review_required.is_(True)
            )
        ).all()

        created = 0

        for risk in risk_assessments:

            existing_review = session.scalar(
                select(Review).where(
                    Review.case_id == risk.case_id
                )
            )

            if existing_review:
                continue

            case = session.scalar(
                select(Case).where(
                    Case.case_id == risk.case_id
                )
            )

            if case is None:
                continue

            review = Review(
                case_id=risk.case_id,
                case_status=case.status,
                review_status="PENDING",
                reviewer_decision=None,
                reviewer_comment=None,
                reviewed_at=None,
                final_status=case.status,
                reviewer=None,
                decision=None,
                comment=None,
                created_at=datetime.utcnow(),
            )

            session.add(review)
            created += 1

        session.commit()

        return {
            "created": created,
            "message": (
                f"Created {created} missing review records."
            ),
        }

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def run_self_test():
    summary = get_review_summary()

    print("Review manager self-test")
    print("------------------------")
    print(f"Total reviews : {summary['total_reviews']}")
    print(f"Pending       : {summary['pending']}")
    print(f"Completed     : {summary['completed']}")
    print(f"Approved      : {summary['approved']}")
    print(f"Rejected      : {summary['rejected']}")
    print(f"Escalated     : {summary['escalated']}")


if __name__ == "__main__":
    run_self_test()