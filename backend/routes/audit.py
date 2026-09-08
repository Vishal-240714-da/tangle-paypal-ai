import logging

from fastapi import APIRouter, HTTPException

from backend.schemas.audit import AuditTrailResponse
from backend.services.audit_service import (
    get_audit_trail,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/audit",
    tags=["Audit Trail"],
)


@router.get(
    "/cases/{case_id}",
    response_model=AuditTrailResponse,
    summary="Get case audit trail",
    description=(
        "Retrieve the complete chronological "
        "audit trail for a TANGLE case."
    ),
)
def get_case_audit_trail(
    case_id: str,
):
    try:
        return get_audit_trail(case_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception:
        logger.exception(
            "Failed to retrieve audit trail "
            "for case %s",
            case_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve audit trail.",
        )