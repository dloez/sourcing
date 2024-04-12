from typing import List

from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from sourcing.source.models import ResponseSource, Source
from sourcing.user.db import users_collection

PyObjectId = Annotated[str, BeforeValidator(str)]


class RegisterUser(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    disabled: bool = Field(default=False)


class ResponseUser(BaseModel):
    id: PyObjectId
    name: str
    email: EmailStr
    sources: List[ResponseSource] = Field(default=[])


class User(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    sources: List[Source] = Field(default=[])
    password: str = Field(...)
    disabled: bool = Field(default=False)

    async def find_by_email(email: EmailStr):
        user = await users_collection.find_one({"email": email})
        if not user:
            return None
        return User(**user)
