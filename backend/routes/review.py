import logging

from fastapi import APIRouter, HTTPException

from agents.review_manager import (
    get_pending_reviews,
    get_review_summary,
    review_case,
)

from backend.schemas.review import (
    PendingReviewResponse,
    ReviewRequest,
    ReviewSubmissionResponse,
    ReviewSummaryResponse,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/reviews",
    tags=["Human Review"],
)


ALLOWED_DECISIONS = {
    "APPROVE",
    "REJECT",
    "ESCALATE",
}


@router.get(
    "/pending",
    response_model=list[PendingReviewResponse],
    summary="Get pending reviews",
    description=(
        "Retrieve all cases currently waiting "
        "for human review, ordered by priority."
    ),
)
def pending_reviews():
    try:
        reviews = get_pending_reviews()

        logger.info(
            "Pending reviews requested: %s records",
            len(reviews),
        )

        return reviews

    except Exception:
        logger.exception(
            "Failed to retrieve pending reviews."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve pending reviews.",
        )


@router.get(
    "/summary",
    response_model=ReviewSummaryResponse,
    summary="Get review summary",
    description=(
        "Return human review statistics including "
        "pending, completed, approved, rejected "
        "and escalated reviews."
    ),
)
def review_summary():
    try:
        summary = get_review_summary()

        logger.info(
            "Review summary requested."
        )

        return summary

    except Exception:
        logger.exception(
            "Failed to retrieve review summary."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve review summary.",
        )


@router.post(
    "/{case_id}",
    response_model=ReviewSubmissionResponse,
    summary="Submit human review",
    description=(
        "Submit an analyst decision for a TANGLE case."
    ),
)
def submit_review(
    case_id: str,
    request: ReviewRequest,
):
    case_id = case_id.strip()

    if not case_id:
        raise HTTPException(
            status_code=400,
            detail="Case ID cannot be empty.",
        )

    decision = (
        request.reviewer_decision
        .strip()
        .upper()
    )

    comment = (
        request.reviewer_comment
        .strip()
    )

    if decision not in ALLOWED_DECISIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid reviewer decision. "
                "Allowed values are: "
                "APPROVE, REJECT, ESCALATE."
            ),
        )

    try:
        result = review_case(
            case_id=case_id,
            reviewer_decision=decision,
            reviewer_comment=comment,
        )

        logger.info(
            "Review submitted: case=%s decision=%s",
            case_id,
            decision,
        )

        return result

    except ValueError as error:
        logger.warning(
            "Review validation failed: case=%s error=%s",
            case_id,
            str(error),
        )

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        logger.exception(
            "Failed to process review for case %s",
            case_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to process the review.",
        )