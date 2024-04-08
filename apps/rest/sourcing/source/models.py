from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class SourceKind(Enum):
    BANK_ACCOUNT = "bank_account"
    CRYPTO_WALLET = "crypto_wallet"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


class BankAccountDetails(BaseModel):
    iban: Optional[str] = Field(default=None)
    currency: str = Field(...)
    name: str = Field(...)
    eb_session: str = Field(...)
    eb_uid: str = Field(...)
    eb_id_hash: str = Field(...)


class CryptoWalletDetails(BaseModel):
    wallet_address: str = Field(...)
    coin: str = Field(...)


class Source(BaseModel):
    kind: SourceKind = Field(...)
    details: BankAccountDetails | CryptoWalletDetails = Field(...)
    model_config: ConfigDict = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def check_details_type(self) -> "Source":
        kind = self.kind
        details = self.details

        if kind == SourceKind.bank and not isinstance(details, BankAccountDetails):
            raise ValueError("details must be a BankDetails type for bank kind")

        if kind == SourceKind.crypto_wallet and not isinstance(
            details, CryptoWalletDetails
        ):
            raise ValueError(
                "details must be a CryptoWalletDetails type for crypto_wallet kind"
            )
        return self
