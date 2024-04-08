from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from sourcing.security.db import refresh_tokens_collection


class GrantType(str, Enum):
    password = "password"
    refresh_token = "refresh_token"


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


class RegisteredRefreshToken(BaseModel):
    access_token: str = Field(...)
    refresh_token: str = Field(...)
    expires_in: datetime = Field(...)
    user_email: EmailStr = Field(...)

    async def get_and_delete_by_refresh_token(
        refresh_token: str,
    ) -> "RegisteredRefreshToken":
        return await refresh_tokens_collection.find_one_and_delete(
            {"refresh_token": refresh_token}
        )


class TokenRequest(BaseModel):
    refresh_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    grant_type: GrantType


class TokenValidationRequest(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


class TokenValidationResponse(BaseModel):
    expires_in: datetime
