
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import (
    analytics,
    audit,
    cases,
    dashboard,
    data_quality,
    investigation,
    reconciliation,
    review,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LOGGING
# ============================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

logging.basicConfig(
    level=getattr(
        logging,
        LOG_LEVEL,
        logging.INFO,
    ),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


# ============================================================
# CORS
# ============================================================

cors_origins_raw = os.getenv(
    "TANGLE_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

cors_origins = [
    origin.strip()
    for origin in cors_origins_raw.split(",")
    if origin.strip()
]


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="TANGLE API",
    description=(
        "Transaction Anomaly & Governance "
        "Ledger Engine API"
    ),
    version="1.0.0",
)


# ============================================================
# CORS MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    dashboard.router
)

app.include_router(
    cases.router
)

app.include_router(
    investigation.router
)

app.include_router(
    review.router
)

app.include_router(
    analytics.router
)

app.include_router(
    data_quality.router
)

app.include_router(
    reconciliation.router
)

app.include_router(
    audit.router
)


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    summary="TANGLE API root",
)
def root():
    return {
        "name": "TANGLE",
        "description": (
            "Transaction Anomaly & "
            "Governance Ledger Engine"
        ),
        "status": "running",
        "version": "1.0.0",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    summary="Health check",
)
def health():
    return {
        "status": "healthy",
        "service": "tangle-api",
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():
    logger.info(
        "TANGLE API started successfully."
    )
    logger.info(
        "CORS origins: %s",
        cors_origins,
    )


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event("shutdown")
def shutdown_event():
    logger.info(
        "TANGLE API shutting down."
    )
