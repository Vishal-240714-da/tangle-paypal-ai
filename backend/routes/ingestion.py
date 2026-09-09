from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.ingestion_service import (
    activate_staged_dataset,
    get_ingestion_status,
    import_active_datasets,
    run_ingestion_quality_check,
    save_uploaded_dataset,
    validate_staged_dataset,
    validate_staged_dataset_quality,
)


router = APIRouter(
    prefix="/api/ingestion",
    tags=["ingestion"],
)


@router.get("/status")
def ingestion_status():
    """
    Return the current active/staging status
    of all Phase 10 datasets.
    """
    try:
        return {
            "status": "ok",
            **get_ingestion_status(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to get ingestion status: {exc}",
        ) from exc


@router.post("/upload/{dataset_name}")
async def upload_dataset(
    dataset_name: str,
    file: UploadFile = File(...),
):
    """
    Upload a CSV dataset into staging.
    """
    try:
        result = save_uploaded_dataset(
            dataset_name=dataset_name,
            uploaded_file=file,
        )

        return {
            "status": "staged",
            "message": (
                f"{dataset_name} dataset uploaded "
                "to staging successfully."
            ),
            "upload": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset upload failed: {exc}",
        ) from exc


@router.post("/validate/{dataset_name}")
def validate_dataset(
    dataset_name: str,
):
    """
    Run the FULL Data Quality Engine against
    a staged dataset.

    The active datasets are never modified.
    """
    try:
        quality_result = validate_staged_dataset_quality(
            dataset_name
        )

        return {
            "status": "validated",
            "quality": quality_result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # IMPORTANT:
        # Return the actual backend exception so
        # development/debugging does not hide the cause.
        raise HTTPException(
            status_code=500,
            detail=(
                "Staged dataset validation failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc


@router.post("/activate/{dataset_name}")
def activate_dataset(
    dataset_name: str,
):
    """
    Validate and activate a staged dataset.

    Activation is blocked if the full Data Quality
    Engine reports any errors.
    """
    try:
        activation_result = activate_staged_dataset(
            dataset_name
        )

        return {
            "status": "activated",
            "message": (
                f"{dataset_name} dataset activated "
                "successfully."
            ),
            "activation": activation_result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset activation failed: {exc}",
        ) from exc


@router.post("/import")
def import_datasets():
    """
    Import the currently active source datasets
    into PostgreSQL.

    Only invoices, payments, and bank transactions
    are imported.
    """
    try:
        result = import_active_datasets()

        return {
            "status": "imported",
            "message": (
                "Active source datasets imported "
                "into PostgreSQL successfully."
            ),
            "import": result,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset import failed: {exc}",
        ) from exc


@router.post("/validate")
def validate_active_datasets():
    """
    Run the full Data Quality Engine against
    the currently active datasets.
    """
    try:
        quality_result = run_ingestion_quality_check()

        return {
            "status": "validated",
            "quality": quality_result,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Data quality validation failed: {exc}",
        ) from exc