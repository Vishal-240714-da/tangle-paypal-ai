import json
from datetime import datetime

from sqlalchemy import select

from agents.case_lifecycle import (
    transition_case_with_session,
)
from database.connection import SessionLocal
from database.models import (
    Case,
    Investigation,
    RiskAssessment,
    Review,
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


def safe_float(value):
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def build_review_evidence(case):
    """
    Build structured evidence directly from the
    financial values stored on the TANGLE case.
    """

    evidence = []

    currency = "INR"

    invoice_amount = safe_float(
        getattr(
            case,
            "original_invoice_amount",
            None,
        )
    )

    payment_amount = safe_float(
        getattr(
            case,
            "payment_amount",
            None,
        )
    )

    bank_amount = safe_float(
        getattr(
            case,
            "bank_amount",
            None,
        )
    )

    payment_fee = safe_float(
        getattr(
            case,
            "payment_fee",
            None,
        )
    )

    outstanding_amount = safe_float(
        getattr(
            case,
            "outstanding_amount",
            None,
        )
    )

    coverage = safe_float(
        getattr(
            case,
            "payment_coverage_percent",
            None,
        )
    )

    invoice_payment_difference = safe_float(
        getattr(
            case,
            "invoice_payment_difference",
            None,
        )
    )

    bank_payment_difference = safe_float(
        getattr(
            case,
            "bank_payment_difference",
            None,
        )
    )

    # --------------------------------------------------------
    # FALLBACK CALCULATIONS
    # --------------------------------------------------------

    if (
        outstanding_amount is None
        and invoice_amount is not None
        and payment_amount is not None
    ):
        outstanding_amount = max(
            invoice_amount - payment_amount,
            0,
        )

    if (
        coverage is None
        and invoice_amount
        and payment_amount is not None
    ):
        coverage = (
            payment_amount
            / invoice_amount
            * 100
        )

    if (
        invoice_payment_difference is None
        and invoice_amount is not None
        and payment_amount is not None
    ):
        invoice_payment_difference = (
            invoice_amount - payment_amount
        )

    if (
        bank_payment_difference is None
        and bank_amount is not None
        and payment_amount is not None
    ):
        bank_payment_difference = (
            bank_amount - payment_amount
        )

    # --------------------------------------------------------
    # SOURCE VALUES
    # --------------------------------------------------------

    if invoice_amount is not None:
        evidence.append(
            {
                "label": "Invoice Amount",
                "value": (
                    f"{currency} "
                    f"{invoice_amount:,.2f}"
                ),
                "source": "Invoice",
            }
        )

    if payment_amount is not None:
        evidence.append(
            {
                "label": "Payment Amount",
                "value": (
                    f"{currency} "
                    f"{payment_amount:,.2f}"
                ),
                "source": "Payment",
            }
        )

    if bank_amount is not None:
        evidence.append(
            {
                "label": "Bank Amount",
                "value": (
                    f"{currency} "
                    f"{bank_amount:,.2f}"
                ),
                "source": "Bank Transaction",
            }
        )

    # --------------------------------------------------------
    # CALCULATED VALUES
    # --------------------------------------------------------

    if outstanding_amount is not None:
        evidence.append(
            {
                "label": "Outstanding Amount",
                "value": (
                    f"{currency} "
                    f"{outstanding_amount:,.2f}"
                ),
                "source": "Calculated",
            }
        )

    if coverage is not None:
        evidence.append(
            {
                "label": "Payment Coverage",
                "value": f"{coverage:.2f}%",
                "source": "Calculated",
            }
        )

    if invoice_payment_difference is not None:
        evidence.append(
            {
                "label": "Invoice-Payment Difference",
                "value": (
                    f"{currency} "
                    f"{invoice_payment_difference:,.2f}"
                ),
                "source": "Calculated",
            }
        )

    if bank_payment_difference is not None:
        evidence.append(
            {
                "label": "Bank-Payment Difference",
                "value": (
                    f"{currency} "
                    f"{bank_payment_difference:,.2f}"
                ),
                "source": "Calculated",
            }
        )

    if payment_fee:
        evidence.append(
            {
                "label": "Payment Fee",
                "value": (
                    f"{currency} "
                    f"{payment_fee:,.2f}"
                ),
                "source": "Payment",
            }
        )

    return evidence


def load_reviews():
    session = SessionLocal()

    try:
        return session.scalars(
            select(Review).order_by(Review.id)
        ).all()

    finally:
        session.close()


def get_pending_reviews():
    """
    Return all pending human-review cases with
    enough context for an informed decision.

    Includes:

    Case
    Financial information
    AI investigation
    Evidence
    Risk
    Review status
    """

    session = SessionLocal()

    try:
        results = session.execute(
            select(
                Review,
                Case,
                RiskAssessment,
                Investigation,
            )
            .join(
                Case,
                Review.case_id == Case.case_id,
            )
            .outerjoin(
                RiskAssessment,
                Review.case_id
                == RiskAssessment.case_id,
            )
            .outerjoin(
                Investigation,
                Review.case_id
                == Investigation.case_id,
            )
            .where(
                Review.review_status == "PENDING"
            )
            .order_by(
                RiskAssessment.priority_score.desc()
            )
        ).all()

        pending = []

        for (
            review,
            case,
            risk,
            investigation,
        ) in results:

            evidence = build_review_evidence(
                case
            )

            investigation_confidence = None

            if investigation:
                investigation_confidence = (
                    investigation.investigation_confidence
                    if investigation.investigation_confidence
                    is not None
                    else investigation.confidence
                )

            pending.append(
                {
                    # ------------------------------------------------
                    # REVIEW
                    # ------------------------------------------------

                    "case_id": review.case_id,

                    "case_status":
                        review.case_status,

                    "review_status":
                        review.review_status,

                    "reviewer_decision":
                        review.reviewer_decision,

                    "reviewer_comment":
                        review.reviewer_comment,

                    "reviewed_at":
                        review.reviewed_at,

                    "final_status":
                        review.final_status,

                    # ------------------------------------------------
                    # CASE
                    # ------------------------------------------------

                    "record_type":
                        case.record_type,

                    "record_id":
                        case.record_id,

                    "invoice_id":
                        case.invoice_id,

                    "payment_id":
                        getattr(
                            case,
                            "payment_id",
                            None,
                        ),

                    "category":
                        case.category,

                    "exception_type":
                        getattr(
                            case,
                            "exception_type",
                            None,
                        ),

                    "decision":
                        case.decision,

                    "decision_confidence":
                        case.decision_confidence,

                    "human_review_required":
                        case.human_review_required,

                    # ------------------------------------------------
                    # RISK
                    # ------------------------------------------------

                    "risk_level":
                        (
                            risk.risk_level
                            if risk
                            else case.risk_level
                        ),

                    "priority_score":
                        (
                            risk.priority_score
                            if risk
                            else case.priority_score
                        ),

                    # ------------------------------------------------
                    # FINANCIAL
                    # ------------------------------------------------

                    "currency":
                        "INR",

                    "invoice_amount":
                        safe_float(
                            case.original_invoice_amount
                        ),

                    "payment_amount":
                        safe_float(
                            case.payment_amount
                        ),

                    "bank_amount":
                        safe_float(
                            case.bank_amount
                        ),

                    "payment_fee":
                        safe_float(
                            case.payment_fee
                        ),

                    "outstanding_amount":
                        safe_float(
                            case.outstanding_amount
                        ),

                    "payment_coverage_percent":
                        safe_float(
                            case.payment_coverage_percent
                        ),

                    "invoice_payment_difference":
                        safe_float(
                            case.invoice_payment_difference
                        ),

                    "bank_payment_difference":
                        safe_float(
                            case.bank_payment_difference
                        ),

                    "financial_status":
                        case.financial_status,

                    "financial_impact":
                        case.financial_impact,

                    # ------------------------------------------------
                    # AI INVESTIGATION
                    # ------------------------------------------------

                    "investigation_finding":
                        (
                            investigation.investigation_finding
                            if investigation
                            else None
                        ),

                    "likely_cause":
                        (
                            investigation.likely_cause
                            if investigation
                            else None
                        ),

                    "recommended_action":
                        (
                            investigation.recommended_action
                            if investigation
                            else None
                        ),

                    "investigation_confidence":
                        investigation_confidence,

                    "evidence":
                        evidence,

                    "reasoning_steps":
                        (
                            investigation.reasoning_steps
                            if investigation
                            else None
                        ),

                    "rationale":
                        (
                            investigation.rationale
                            if investigation
                            else None
                        ),

                    "evidence_summary":
                        (
                            investigation.evidence_summary
                            if investigation
                            else None
                        ),
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
        raise ValueError(
            "Case ID is required."
        )

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

            session.flush()

        # ----------------------------------------------------
        # Use TANGLE lifecycle engine
        # ----------------------------------------------------

        lifecycle_result = (
            transition_case_with_session(
                session=session,
                case_id=case_id,
                new_status=new_case_status,
                changed_by=reviewer,
                reason=(
                    f"Human review decision: "
                    f"{reviewer_decision}"
                ),
            )
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
            "reviewer_decision":
                review.reviewer_decision,
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

    Review-required cases are moved through the TANGLE
    lifecycle into PENDING_REVIEW before the Review
    record is created.
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

            # ------------------------------------------------
            # Move case into the review lifecycle state.
            # ------------------------------------------------

            if case.status == "OPEN":
                lifecycle_result = (
                    transition_case_with_session(
                        session=session,
                        case_id=case.case_id,
                        new_status="INVESTIGATING",
                        changed_by="SYSTEM",
                        reason=(
                            "Case requires human review."
                        ),
                    )
                )

                if not lifecycle_result["success"]:
                    raise ValueError(
                        lifecycle_result["message"]
                    )

            if case.status == "INVESTIGATING":
                lifecycle_result = (
                    transition_case_with_session(
                        session=session,
                        case_id=case.case_id,
                        new_status="PENDING_REVIEW",
                        changed_by="SYSTEM",
                        reason=(
                            "Case requires human review."
                        ),
                    )
                )

                if not lifecycle_result["success"]:
                    raise ValueError(
                        lifecycle_result["message"]
                    )

            if case.status != "PENDING_REVIEW":
                raise ValueError(
                    f"Case {case.case_id} cannot enter "
                    f"the review queue from status "
                    f"{case.status}."
                )

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


if __name__ == "__main__":
    run_self_test()