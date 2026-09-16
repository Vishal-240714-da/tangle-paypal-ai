from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# REGISTER
# ============================================================

class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: str = Field(
        default="ANALYST",
        min_length=1,
        max_length=50,
    )


# ============================================================
# LOGIN
# ============================================================

class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool


# ============================================================
# LOGIN RESPONSE
# ============================================================

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================
# CURRENT USER RESPONSE
# ============================================================

class CurrentUserResponse(BaseModel):
    user: UserResponse

    # ============================================================
# USER ADMINISTRATION
# ============================================================

class AdminUserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: str = Field(
        default="ANALYST",
        min_length=1,
        max_length=50,
    )


class UserRoleUpdate(BaseModel):
    role: str = Field(
        min_length=1,
        max_length=50,
    )


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int