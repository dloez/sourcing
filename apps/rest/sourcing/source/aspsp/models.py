from pydantic import BaseModel


class ASPSP(BaseModel):
    maximum_consent_validity_seconds: int
    name: str
    logo_uri: str
    custom_id: str
