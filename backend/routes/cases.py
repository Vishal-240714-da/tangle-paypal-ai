import logging
import math

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, or_, select

from backend.schemas.case import (
    CaseHistoryResponse,
    CaseListResponse,
    CaseResponse,
)

from database.connection import SessionLocal
from database.models import Case, CaseHistory


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"],
)


# ============================================================
# GET CASES
# ============================================================

@router.get(
    "",
    response_model=CaseListResponse,
    summary="Get cases",
    description=(
        "Retrieve TANGLE cases with pagination, "
        "search, filtering and sorting."
    ),
)
def get_cases(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number.",
    ),

    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of cases per page.",
    ),

    search: str | None = Query(
        default=None,
        description=(
            "Search by case ID, record ID, "
            "invoice ID or category."
        ),
    ),

    status: str | None = Query(
        default=None,
        description="Filter by case status.",
    ),

    risk_level: str | None = Query(
        default=None,
        description="Filter by risk level.",
    ),

    sort_by: str = Query(
        default="case_id",
        description=(
            "Sort field: case_id, priority_score, "
            "created_at or updated_at."
        ),
    ),

    sort_order: str = Query(
        default="asc",
        description="Sort order: asc or desc.",
    ),
):
    session = SessionLocal()

    try:
        # ----------------------------------------------------
        # Validate sorting
        # ----------------------------------------------------

        allowed_sort_fields = {
            "case_id": Case.case_id,
            "priority_score": Case.priority_score,
            "created_at": Case.created_at,
            "updated_at": Case.updated_at,
        }

        sort_column = allowed_sort_fields.get(
            sort_by
        )

        if sort_column is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid sort_by. Allowed values: "
                    "case_id, priority_score, "
                    "created_at, updated_at."
                ),
            )

        sort_order = sort_order.strip().lower()

        if sort_order not in {"asc", "desc"}:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid sort_order. "
                    "Use 'asc' or 'desc'."
                ),
            )

        # ----------------------------------------------------
        # Base query
        # ----------------------------------------------------

        query = select(Case)

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        if search:
            search_value = search.strip()

            if search_value:
                pattern = f"%{search_value}%"

                query = query.where(
                    or_(
                        Case.case_id.ilike(pattern),
                        Case.record_id.ilike(pattern),
                        Case.invoice_id.ilike(pattern),
                        Case.category.ilike(pattern),
                    )
                )

        # ----------------------------------------------------
        # Status filter
        # ----------------------------------------------------

        if status:
            query = query.where(
                Case.status == status.strip().upper()
            )

        # ----------------------------------------------------
        # Risk filter
        # ----------------------------------------------------

        if risk_level:
            query = query.where(
                Case.risk_level
                == risk_level.strip().upper()
            )

        # ----------------------------------------------------
        # Total count
        # ----------------------------------------------------

        count_query = select(
            func.count()
        ).select_from(
            query.subquery()
        )

        total = session.scalar(
            count_query
        ) or 0

        # ----------------------------------------------------
        # Sorting
        # ----------------------------------------------------

        if sort_order == "desc":
            query = query.order_by(
                sort_column.desc()
            )
        else:
            query = query.order_by(
                sort_column.asc()
            )

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        offset = (
            (page - 1)
            * page_size
        )

        query = query.offset(
            offset
        ).limit(
            page_size
        )

        cases = session.scalars(
            query
        ).all()

        total_pages = (
            math.ceil(
                total / page_size
            )
            if total
            else 0
        )

        logger.info(
            "Cases requested: page=%s page_size=%s "
            "search=%s status=%s risk_level=%s "
            "returned=%s total=%s",
            page,
            page_size,
            search,
            status,
            risk_level,
            len(cases),
            total,
        )

        return CaseListResponse(
            items=cases,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to retrieve cases."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve cases.",
        )

    finally:
        session.close()


# ============================================================
# GET SINGLE CASE
# ============================================================

@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Get case by ID",
    description="Retrieve a single TANGLE case.",
)
def get_case_by_id(
    case_id: str,
):
    case_id = case_id.strip()

    if not case_id:
        raise HTTPException(
            status_code=400,
            detail="Case ID cannot be empty.",
        )

    session = SessionLocal()

    try:
        case = session.get(
            Case,
            case_id,
        )

        if case is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Case {case_id} not found."
                ),
            )

        logger.info(
            "Case retrieved: %s",
            case_id,
        )

        return case

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to retrieve case %s",
            case_id,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve case."
            ),
        )

    finally:
        session.close()


# ============================================================
# GET CASE HISTORY
# ============================================================

@router.get(
    "/{case_id}/history",
    response_model=list[CaseHistoryResponse],
    summary="Get case history",
    description=(
        "Retrieve the chronological lifecycle and "
        "audit history for a TANGLE case."
    ),
)
def get_case_history(
    case_id: str,
):
    """
    Return all lifecycle history records for a case.

    History is ordered from oldest to newest.
    """

    case_id = case_id.strip()

    if not case_id:
        raise HTTPException(
            status_code=400,
            detail="Case ID cannot be empty.",
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
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Case {case_id} not found."
                ),
            )

        # ----------------------------------------------------
        # Load history
        # ----------------------------------------------------

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

        logger.info(
            "Case history retrieved: "
            "case_id=%s records=%s",
            case_id,
            len(history),
        )

        return history

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to retrieve history for case %s",
            case_id,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve case history."
            ),
        )

    finally:
        session.close()