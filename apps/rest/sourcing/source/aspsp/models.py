from typing import Optional

from pydantic import BaseModel, Field

from sourcing.typing import PyObjectId


class ASPSPSourceDetails(BaseModel):
    iban: Optional[str] = Field(default=None)
    currency: str = Field()
    name: str = Field()
    eb_session: str = Field()
    eb_uid: str = Field()
    eb_id_hash: str = Field()


class ResponseASPSPSourceDetails(BaseModel):
    iban: str
    currency: str
    name: str


class ASPSP(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    maximum_consent_validity_seconds: int = Field()
    name: str = Field()
    country: str = Field()
    logo_url: str = Field()
    custom_id: str = Field()


class ASPSPResponse(BaseModel):
    id: str
    maximum_consent_validity_seconds: int
    name: str
    country: str
    logo_url: str


class ASPSPAuthRequest(BaseModel):
    aspsp_id: PyObjectId
    redirect_url: str
    state: Optional[str] = None


class ASPSPAuthResponse(BaseModel):
    url: str


class ASPSPSessionRequest(BaseModel):
    code: str
