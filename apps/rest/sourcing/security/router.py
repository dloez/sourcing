from fastapi import APIRouter, status, HTTPException
from jose import jwt, JWTError

from sourcing.security.models import Token, TokenRequest, TokenValidationResponse, TokenValidationRequest, RegisteredRefreshToken
from sourcing.security.token_factory import create_token, decode_refresh_token, decode_access_token, get_fields_from_refresh_token
from sourcing.user.auth import authenticate_user
from sourcing.security.db import refresh_tokens_collection


router = APIRouter()


async def _get_user_token(token_request: TokenRequest) -> Token:
    if not token_request.username or not token_request.password:
        raise HTTPException(status_code=400, detail="username and password are required")
    
    user = await authenticate_user(token_request.username, token_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token(data={"sub": user.email})


async def _get_refresh_token(token_request: TokenRequest) -> Token:
    if not token_request.refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token is required")
    
    try:
        payload = decode_refresh_token(token=token_request.refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    return create_token(payload)


@router.post(
    "/token",
    response_model=Token
)
async def token(
    token_request: TokenRequest,
) -> Token:
    if token_request.grant_type == "password":
        token = await _get_user_token(token_request)
    
    if token_request.grant_type == "refresh_token":
        registered_token = await RegisteredRefreshToken.get_and_delete_by_refresh_token(token_request.refresh_token)
        if not registered_token:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        token = await _get_refresh_token(token_request)
    
    email_expires = get_fields_from_refresh_token(token.refresh_token, ["sub", "exp"])
    registered_token = RegisteredRefreshToken(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        user_email=email_expires.get("sub"),
        expires_in=email_expires.get("exp")
    )
    await refresh_tokens_collection.insert_one(registered_token.model_dump())
    return token
    

@router.post(
    "/token/verify",
    response_model=TokenValidationResponse
)
async def verify_token(
    token_validation_request: TokenValidationRequest
) -> TokenValidationResponse:
    if token_validation_request.access_token:
        try:
            payload = decode_access_token(token_validation_request.access_token)
            return TokenValidationResponse(expires_in=payload.get("exp"))
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid access token")
        
    if token_validation_request.refresh_token:
        try:
            payload = decode_refresh_token(token_validation_request.refresh_token)
            return TokenValidationResponse(expires_in=payload.get("exp"))
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    raise HTTPException(status_code=400, detail="access_token or refresh_token is required")
