import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.routes import dashboard
from backend.routes import cases
from backend.routes import investigation
from backend.routes import review
from backend.routes import analytics
from backend.routes import data_quality


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper(),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)


logger = logging.getLogger(__name__)


# ============================================================
# TANGLE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="TANGLE API",
    description=(
        "Transaction Anomaly & "
        "Governance Ledger Engine"
    ),
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

# Read allowed frontend origins from the environment.
#
# Example:
#
# TANGLE_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
#
# Multiple origins are separated by commas.

cors_origins_raw = os.getenv(
    "TANGLE_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

cors_origins = [
    origin.strip()
    for origin in cors_origins_raw.split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
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

# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    summary="TANGLE API root",
)
def root():
    return {
        "application": "TANGLE",
        "full_name": (
            "Transaction Anomaly & "
            "Governance Ledger Engine"
        ),
        "status": "operational",
        "version": "1.0.0",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    summary="Health check",
)
def health_check():
    return {
        "status": "healthy",
    }