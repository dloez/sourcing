from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from jose import JWTError

from sourcing.user.models import User
from sourcing.security.models import TokenData
from sourcing.security.token_factory import oauth2_scheme, decode_access_token
from sourcing.security.crypto import verify_password


async def authenticate_user(email: EmailStr, password: str) -> User | None:
    user = await User.find_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await User.find_by_email(email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
