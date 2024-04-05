from typing import Optional
from enum import Enum

from typing_extensions import Annotated
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator


PyObjectId = Annotated[str, BeforeValidator(str)]


class SourceKind(Enum):
    bank = "bank"
    crypto_wallet = "crypto_wallet"


class SourceModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    kind: SourceKind = Field(...)