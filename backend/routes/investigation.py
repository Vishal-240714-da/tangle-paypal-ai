import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from backend.schemas.investigation import (
    InvestigationResponse,
)
from database.connection import SessionLocal
from database.models import Investigation


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/investigation",
    tags=["Investigation"],
)


@router.get(
    "/{case_id}",
    response_model=InvestigationResponse,
    summary="Get investigation by case ID",
    description=(
        "Retrieve the AI investigation result "
        "associated with a TANGLE case."
    ),
)
def get_investigation(case_id: str):
    case_id = case_id.strip()

    if not case_id:
        raise HTTPException(
            status_code=400,
            detail="Case ID cannot be empty.",
        )

    session = SessionLocal()

    try:
        investigation = session.scalars(
        select(Investigation)
            .where(
                Investigation.case_id == case_id
            )
        ).first()

        if investigation is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Investigation for case "
                    f"{case_id} not found."
                ),
            )

        logger.info(
            "Investigation retrieved: %s",
            case_id,
        )

        return investigation

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to retrieve investigation for %s",
            case_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve investigation.",
        )

    finally:
        session.close()