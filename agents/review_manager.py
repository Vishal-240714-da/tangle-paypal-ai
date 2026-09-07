from datetime import datetime

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import (
    Case,
    RiskAssessment,
    Review,
)


# ============================================================
# CONSTANTS
# ============================================================

ALLOWED_DECISIONS = {
    "APPROVE",
    "REJECT",
    "ESCALATE",
}


# ============================================================
# HELPER
# ============================================================

def normalize_string(value):
    """
    Safely convert a value into a string.

    None becomes an empty string.
    """

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# GET ALL REVIEWS
# ============================================================

def load_reviews():
    """
    Load all human review records from PostgreSQL.
    """

    session = SessionLocal()

    try:

        return session.scalars(
            select(Review).order_by(Review.id)
        ).all()

    finally:

        session.close()


# ============================================================
# GET PENDING REVIEWS
# ============================================================

def get_pending_reviews():
    """
    Return all cases currently waiting for human review.

    Highest priority cases are returned first.
    """

    session = SessionLocal()

    try:

        results = session.execute(
            select(
                Review,
                RiskAssessment,
            )
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

            pending.append({
                "case_id": review.case_id,
                "risk_level": risk.risk_level,
                "priority_score": risk.priority_score,
                "human_review_required": (
                    risk.human_review_required
                ),
                "case_status": review.case_status,
                "review_status": review.review_status,
                "reviewer_decision": (
                    review.reviewer_decision
                ),
                "reviewer_comment": (
                    review.reviewer_comment
                ),
                "reviewed_at": (
                    review.reviewed_at
                ),
                "final_status": review.final_status,
            })

        return pending

    finally:

        session.close()


# ============================================================
# REVIEW CASE
# ============================================================

def review_case(
    case_id,
    reviewer_decision,
    reviewer_comment="",
):
    """
    Record a human analyst decision.

    Allowed decisions:

        APPROVE
        REJECT
        ESCALATE

    Lifecycle:

        APPROVE
            → APPROVED

        REJECT
            → REJECTED

        ESCALATE
            → ESCALATED
    """

    # --------------------------------------------------------
    # Normalize inputs
    # --------------------------------------------------------

    case_id = normalize_string(case_id)

    reviewer_decision = (
        normalize_string(
            reviewer_decision
        )
        .upper()
    )

    reviewer_comment = normalize_string(
        reviewer_comment
    )

    # --------------------------------------------------------
    # Validate case ID
    # --------------------------------------------------------

    if not case_id:

        raise ValueError(
            "Case ID cannot be empty."
        )

    # --------------------------------------------------------
    # Validate decision
    # --------------------------------------------------------

    if reviewer_decision not in ALLOWED_DECISIONS:

        raise ValueError(
            "Invalid reviewer decision. "
            "Allowed values are: "
            "APPROVE, REJECT, ESCALATE."
        )

    session = SessionLocal()

    try:

        # ----------------------------------------------------
        # Verify case exists
        # ----------------------------------------------------

        case = session.get(
            Case,
            case_id,
        )

        if case is None:

            raise ValueError(
                f"Case {case_id} could not be found."
            )

        # ----------------------------------------------------
        # Find existing review
        # ----------------------------------------------------

        review = session.scalars(
            select(Review)
            .where(
                Review.case_id == case_id
            )
        ).first()

        # ----------------------------------------------------
        # If review does not exist, create one
        # ----------------------------------------------------

        if review is None:

            risk = session.scalars(
                select(RiskAssessment)
                .where(
                    RiskAssessment.case_id == case_id
                )
            ).first()

            review = Review(
                case_id=case_id,
                case_status="PENDING_REVIEW",
                review_status="PENDING",
                reviewer_decision=None,
                reviewer_comment=None,
                reviewed_at=None,
                final_status="PENDING_REVIEW",
            )

            session.add(review)

        # ----------------------------------------------------
        # Determine lifecycle status
        # ----------------------------------------------------

        if reviewer_decision == "APPROVE":

            new_case_status = "APPROVED"
            new_final_status = "APPROVED"

        elif reviewer_decision == "REJECT":

            new_case_status = "REJECTED"
            new_final_status = "REJECTED"

        else:

            new_case_status = "ESCALATED"
            new_final_status = "ESCALATED"

        # ----------------------------------------------------
        # Update review
        # ----------------------------------------------------

        review.review_status = "COMPLETED"

        review.reviewer_decision = (
            reviewer_decision
        )

        review.reviewer_comment = (
            reviewer_comment
        )

        review.reviewed_at = datetime.now()

        review.case_status = (
            new_case_status
        )

        review.final_status = (
            new_final_status
        )

        # ----------------------------------------------------
        # Save PostgreSQL transaction
        # ----------------------------------------------------

        session.commit()

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {
            "case_id": review.case_id,
            "review_status": (
                review.review_status
            ),
            "reviewer_decision": (
                review.reviewer_decision
            ),
            "reviewer_comment": (
                review.reviewer_comment
            ),
            "reviewed_at": (
                review.reviewed_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if review.reviewed_at
                else None
            ),
            "case_status": (
                review.case_status
            ),
            "final_status": (
                review.final_status
            ),
        }

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


# ============================================================
# REVIEW SUMMARY
# ============================================================

def get_review_summary():
    """
    Return human review statistics from PostgreSQL.
    """

    session = SessionLocal()

    try:

        reviews = session.scalars(
            select(Review)
        ).all()

        if not reviews:

            return {
                "total_reviews": 0,
                "pending": 0,
                "completed": 0,
                "approved": 0,
                "rejected": 0,
                "escalated": 0,
            }

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
            "total_reviews": len(reviews),
            "pending": pending,
            "completed": completed,
            "approved": approved,
            "rejected": rejected,
            "escalated": escalated,
        }

    finally:

        session.close()


# ============================================================
# CREATE / REFRESH REVIEW QUEUE
# ============================================================

def create_review_queue():
    """
    Ensure every case requiring human review has a
    corresponding PostgreSQL Review record.

    Existing analyst decisions are preserved.
    """

    session = SessionLocal()

    try:

        risk_assessments = session.scalars(
            select(RiskAssessment)
        ).all()

        created_count = 0

        for risk in risk_assessments:

            if not risk.human_review_required:
                continue

            existing_review = session.scalars(
                select(Review)
                .where(
                    Review.case_id == risk.case_id
                )
            ).first()

            if existing_review is not None:
                continue

            review = Review(
                case_id=risk.case_id,
                case_status="PENDING_REVIEW",
                review_status="PENDING",
                reviewer_decision=None,
                reviewer_comment=None,
                reviewed_at=None,
                final_status="PENDING_REVIEW",
            )

            session.add(review)

            created_count += 1

        session.commit()

        return load_reviews()

    except Exception:

        session.rollback()

        raise

    finally:

        session.close()


# ============================================================
# SELF TEST
# ============================================================

def run_self_test():

    print()
    print("=" * 60)
    print("TANGLE HUMAN REVIEW MANAGER")
    print("=" * 60)
    print()

    reviews = load_reviews()

    print(
        f"Total review records: {len(reviews)}"
    )

    print()

    summary = get_review_summary()

    print("REVIEW SUMMARY")
    print()

    print(
        f"Total reviews : "
        f"{summary['total_reviews']}"
    )

    print(
        f"Pending       : "
        f"{summary['pending']}"
    )

    print(
        f"Completed     : "
        f"{summary['completed']}"
    )

    print(
        f"Approved      : "
        f"{summary['approved']}"
    )

    print(
        f"Rejected      : "
        f"{summary['rejected']}"
    )

    print(
        f"Escalated     : "
        f"{summary['escalated']}"
    )

    print()

    pending = get_pending_reviews()

    print(
        f"Pending cases: "
        f"{len(pending)}"
    )

    print()

    if pending:

        print("TOP PRIORITY CASES")
        print()

        for review in pending[:10]:

            print(
                f"{review['case_id']} | "
                f"{review['risk_level']} | "
                f"Priority: "
                f"{review['priority_score']} | "
                f"{review['case_status']}"
            )

    print()
    print("REVIEW MANAGER READY")
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_self_test()