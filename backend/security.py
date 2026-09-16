from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)


# ============================================================
# PASSWORD HASHER
# ============================================================

password_hasher = PasswordHasher()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure Argon2 hash.
    """
    return password_hasher.hash(password)


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plain-text password against its stored Argon2 hash.
    """

    try:
        return password_hasher.verify(
            password_hash,
            password,
        )

    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False