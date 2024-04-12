from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class SourceKind(Enum):
    ASPSP = "aspsp"
    CRYPTO_WALLET = "crypto_wallet"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


class ASPSPSourceDetails(BaseModel):
    iban: Optional[str] = Field(default=None)
    currency: str = Field(...)
    name: str = Field(...)
    eb_session: str = Field(...)
    eb_uid: str = Field(...)
    eb_id_hash: str = Field(...)


class ResponseASPSPSourceDetails(BaseModel):
    iban: str
    currency: str
    name: str


class CryptoWalletSourceDetails(BaseModel):
    wallet_address: str = Field(...)
    coin: str = Field(...)


class Balance(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    amount: float = Field(...)
    source_id: PyObjectId = Field(...)
    date: datetime = Field(default=datetime.now(tz=UTC))
    name: str = Field(...)

    def to_nested(self) -> "NestedBalance":
        return NestedBalance(
            amount=self.amount,
            date=self.date,
            name=self.name,
        )


class NestedBalance(BaseModel):
    amount: float = Field(...)
    date: datetime = Field(default=datetime.now(tz=UTC))
    name: str = Field(...)


class Source(BaseModel):
    kind: SourceKind = Field(...)
    details: ASPSPSourceDetails | CryptoWalletSourceDetails = Field(...)
    latest_balances: list[NestedBalance] = Field(default=[])
    model_config: ConfigDict = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def check_details_type(self) -> "Source":
        if self.kind == SourceKind.ASPSP and not isinstance(
            self.details, ASPSPSourceDetails
        ):
            raise ValueError("details must be a ASPSPSourceDetails type for ASPSP kind")

        if self.kind == SourceKind.CRYPTO_WALLET and not isinstance(
            self.details, CryptoWalletSourceDetails
        ):
            raise ValueError(
                "details must be a CryptoWalletSourceDetails type for crypto_wallet kind"
            )
        return self


class ResponseSource(BaseModel):
    kind: SourceKind
    details: ResponseASPSPSourceDetails | CryptoWalletSourceDetails
    latest_balances: list[NestedBalance]
    model_config: ConfigDict = ConfigDict(use_enum_values=True)
