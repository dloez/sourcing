from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class ASPSP(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    maximum_consent_validity_seconds: int = Field(...)
    name: str = Field(...)
    country: str = Field(...)
    logo_url: str = Field(...)
    custom_id: str = Field(...)


class ASPSPResponse(BaseModel):
    id: str
    maximum_consent_validity_seconds: int
    name: str
    country: str
    logo_url: str


class ASPSPAuthRequest(BaseModel):
    aspsp_id: str
    redirect_url: str
    state: str = None


class ASPSPAuthResponse(BaseModel):
    url: str


class ASPSPSessionRequest(BaseModel):
    code: str
