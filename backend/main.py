from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import dashboard
from backend.routes import cases
from backend.routes import investigation
from backend.routes import review
from backend.routes import analytics


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
# Allows the React frontend running on localhost:5173
# to communicate with the FastAPI backend.
#
# Using "*" is suitable for local development.
# We can restrict this before deployment.
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

# Dashboard routes
app.include_router(
    dashboard.router
)


# Cases routes
app.include_router(
    cases.router
)


# Investigation routes
app.include_router(
    investigation.router
)


# Human Review routes
app.include_router(
    review.router
)


# Analytics routes
app.include_router(
    analytics.router
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
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

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }