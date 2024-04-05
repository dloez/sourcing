from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError

from sourcing.config import JWT_ALGORITHM, ACCESS_SECRET_KEY
from sourcing.user.models import User
from sourcing.security.models import TokenData


cryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def authenticate_user(email: EmailStr, password: str) -> User | None:
    user = await User.find_by_email(email)
    if not user:
        return None
    if not cryptContext.verify(password, user.password):
        return None
    return user


def hash_password(password: str) -> str:
    return cryptContext.hash(password)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[JWT_ALGORITHM])
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
