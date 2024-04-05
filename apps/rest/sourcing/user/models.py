from typing import Optional, List

from typing_extensions import Annotated
from pydantic import BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator

from sourcing.source.models import SourceModel
from sourcing.user.db import users_collection


PyObjectId = Annotated[str, BeforeValidator(str)]


class RegisterUser(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    disabled: bool = False


class LoginUser(BaseModel):
    name: str = Field(...)
    password: str = Field(...)


class ReturnUser(BaseModel):
    id: PyObjectId = Field(...)
    name: str = Field(...)
    email: EmailStr = Field(...)
    sources: List[SourceModel] = Field(default=[])


class User(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    sources: List[SourceModel] = Field(default=[])
    password: str = Field(...)
    disabled: bool = Field(default=False)

    async def find_by_email(email: EmailStr):
        user = await users_collection.find_one({"email": email})
        if not user:
            return None
        return User(**user)
