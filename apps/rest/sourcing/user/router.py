from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends


from sourcing.user.models import RegisterUser, ResponseUser, User
from sourcing.user.db import users_collection
from sourcing.user.auth import get_current_active_user
from sourcing.security.crypto import hash_password


router = APIRouter(prefix="/users")


@router.post(
    "/register",
    response_model=ResponseUser,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False
)
async def register(user: RegisterUser) -> ResponseUser:
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


@router.get(
    "/me",
    response_model=ResponseUser,
    response_model_by_alias=False
)
async def me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> ResponseUser:
    return current_user
