from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sourcing.user.models import RegisterUser, ReturnUser, User
from sourcing.user.db import users_collection
from sourcing.user.auth import authenticate_user, hash_password, get_current_active_user
from sourcing.security.models import Token
from sourcing.security.token_factory import create_token


router = APIRouter(prefix="/users")


@router.post(
    "/register",
    response_model=ReturnUser,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False
)
async def register(user: RegisterUser) -> ReturnUser:
    if await User.find_by_email(user.email):
        raise HTTPException(status_code=409, detail=f"User '{user.email}' already exists")
    user.password = hash_password(user.password)
    
    new_user = await users_collection.insert_one(
        user.model_dump(exclude=["id"])
    )
    if not new_user:
        return HTTPException(status_code=500, detail="Failed to create user")
    
    created_user = await users_collection.find_one({"_id": new_user.inserted_id})
    return User(**created_user)


@router.post(
    "/login",
    response_model=Token
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token(data={"sub": user.email})

@router.get(
    "/me",
    response_model=ReturnUser,
    response_model_by_alias=False
)
async def me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ReturnUser:
    return current_user
