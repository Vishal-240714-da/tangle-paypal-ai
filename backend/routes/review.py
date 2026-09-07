from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.review_manager import (
    review_case,
    get_pending_reviews,
    get_review_summary,
)

router = APIRouter(
    prefix="/api/review",
    tags=["Human Review"],
)


class ReviewRequest(BaseModel):
    reviewer_decision: str
    reviewer_comment: str = ""


@router.get("/pending")
def pending_reviews():
    return get_pending_reviews()


@router.get("/summary")
def review_summary():
    return get_review_summary()


@router.post("/{case_id}")
def submit_review(
    case_id: str,
    request: ReviewRequest,
):
    case_id = case_id.strip()

    decision = (
        request.reviewer_decision
        .strip()
        .upper()
    )

    comment = (
        request.reviewer_comment
        .strip()
    )

    allowed_decisions = {
        "APPROVE",
        "REJECT",
        "ESCALATE",
    }

    if decision not in allowed_decisions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid reviewer decision. "
                "Allowed values are: "
                "APPROVE, REJECT, ESCALATE."
            ),
        )

    if not case_id:
        raise HTTPException(
            status_code=400,
            detail="Case ID cannot be empty.",
        )

    try:
        result = review_case(
            case_id=case_id,
            reviewer_decision=decision,
            reviewer_comment=comment,
        )

        return {
            "success": True,
            "message": (
                f"Case {case_id} successfully "
                f"reviewed."
            ),
            "review": result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process the review: "
                f"{str(error)}"
            ),
        )