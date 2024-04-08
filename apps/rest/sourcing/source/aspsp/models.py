from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class ASPSP(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    maximum_consent_validity_seconds: int = Field(...)
    bank_name: str = Field(...)
    bank_country: str = Field(...)
    logo_uri: str = Field(...)
    custom_id: str = Field(...)


class ASPSPAuthRequest(BaseModel):
    aspsp_id: str
    redirect_uri: str
    state: str = None


class ASPSPAuthResponse(BaseModel):
    url: str
    authorization_id: str
    psu_id_hash: str


class ASPSPSessionRequest(BaseModel):
    code: str
