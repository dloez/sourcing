from pydantic import BaseModel, ConfigDict
from bson import ObjectId


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


class RefreshToken(BaseModel):
    refresh_token: str
    user_id: ObjectId
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
