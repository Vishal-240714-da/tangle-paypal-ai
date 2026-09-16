from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from backend.auth import get_current_user

from backend.schemas.reconciliation import ReconciliationResponse
from backend.services.reconciliation_service import run_reconciliation


router = APIRouter(
    prefix="/api/reconciliation",
    tags=["Reconciliation"],
)


@router.get("", response_model=ReconciliationResponse)
def get_reconciliation(
    current_user=Depends(get_current_user),
    match_type: str | None = Query(
        default=None,
        description="Filter by EXACT, FUZZY, or MERGED_PAYMENT.",
    ),
):
    try:
        result = run_reconciliation()

        if match_type is not None:
            normalized_match_type = match_type.strip().upper()

            allowed_match_types = {
                "EXACT",
                "FUZZY",
                "MERGED_PAYMENT",
            }

            if normalized_match_type not in allowed_match_types:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Invalid match_type. "
                        "Use EXACT, FUZZY, or MERGED_PAYMENT."
                    ),
                )

            filtered_items = [
                item
                for item in result.items
                if item["match_type"] == normalized_match_type
            ]

            return ReconciliationResponse(
                items=filtered_items,
                total=len(filtered_items),
                summary=result.summary,
            )

        return ReconciliationResponse(
            items=result.items,
            total=result.total,
            summary=result.summary,
        )

    except HTTPException:
        raise

    except FileNotFoundError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
            },
        )

    except ValueError as exc:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
            },
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Unable to load reconciliation data.",
            },
        )