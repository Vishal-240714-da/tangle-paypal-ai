import os

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# JWT CONFIGURATION
# ============================================================

JWT_SECRET_KEY = os.getenv(
    "TANGLE_JWT_SECRET_KEY",
)

JWT_ALGORITHM = os.getenv(
    "TANGLE_JWT_ALGORITHM",
    "HS256",
)

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "TANGLE_JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "60",
    )
)


if not JWT_SECRET_KEY:
    raise RuntimeError(
        "TANGLE_JWT_SECRET_KEY is not configured."
    )
