import logging

from fastapi import APIRouter, HTTPException

from backend.schemas.data_quality import DataQualityResponse
from backend.services.data_quality_service import (
    run_data_quality_check,
)


router = APIRouter(
    prefix="/api/data-quality",
    tags=["Data Quality"],
)

logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=DataQualityResponse,
)
def get_data_quality():
    """
    Run the TANGLE Data Quality Engine against
    the incoming financial datasets.
    """

    try:

        result = run_data_quality_check()

        return result

    except FileNotFoundError as exc:

        logger.exception(
            "Data quality source file not found."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Data quality source data is unavailable."
            ),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Data quality check failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Data quality check failed."
            ),
        ) from exc