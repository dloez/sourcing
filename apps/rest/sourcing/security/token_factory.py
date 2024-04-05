from datetime import datetime, timedelta, timezone

from jose import jwt

from sourcing.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_SECRET_KEY, REFRESH_SECRET_KEY, JWT_ALGORITHM
from sourcing.security.models import Token


def create_token(data: dict) -> Token:
    access_token = _create_token(data, ACCESS_SECRET_KEY, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refres_token = _create_token(data, REFRESH_SECRET_KEY, timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer", refresh_token=refres_token)


def _create_token(data,  secret_key, expire_delta: timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=JWT_ALGORITHM)
