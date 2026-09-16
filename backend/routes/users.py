from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import require_roles
from backend.routes.auth import get_db
from backend.schemas.auth import (
    AdminUserCreate,
    UserListResponse,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)
from backend.security import hash_password
from database.models import User


router = APIRouter(
    prefix="/api/users",
    tags=["User Administration"],
)


ALLOWED_ROLES = {
    "ADMIN",
    "ANALYST",
    "REVIEWER",
}


@router.get(
    "",
    response_model=UserListResponse,
)
def list_users(
    current_user=Depends(
        require_roles("ADMIN")
    ),
    db: Session = Depends(get_db),
):
    users = db.scalars(
        select(User).order_by(User.id)
    ).all()

    return UserListResponse(
        users=users,
        total=len(users),
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: AdminUserCreate,
    current_user=Depends(
        require_roles("ADMIN")
    ),
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(User).where(
            User.email == user_data.email
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    role = user_data.role.strip().upper()

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid role. Allowed values are: "
                "ADMIN, ANALYST, REVIEWER."
            ),
        )

    user = User(
        name=user_data.name.strip(),
        email=str(user_data.email).lower(),
        role=role,
        password_hash=hash_password(
            user_data.password
        ),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
def update_user_role(
    user_id: int,
    user_data: UserRoleUpdate,
    current_user=Depends(
        require_roles("ADMIN")
    ),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    role = user_data.role.strip().upper()

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid role. Allowed values are: "
                "ADMIN, ANALYST, REVIEWER."
            ),
        )

    user.role = role

    db.commit()
    db.refresh(user)

    return user


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
)
@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    user_data: UserStatusUpdate,
    current_user=Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)

    return user