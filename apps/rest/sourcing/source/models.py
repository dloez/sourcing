from datetime import UTC, datetime
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


class BankAccountBalance(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    amount: float = Field(...)
    source_id: PyObjectId = Field(...)
    date: datetime = Field(default=datetime.now(tz=UTC))
    name: str = Field(...)

    def to_nested(self) -> "NestedBankAccountBalance":
        return NestedBankAccountBalance(
            amount=self.amount,
            date=self.date,
            name=self.name,
        )


class NestedBankAccountBalance(BaseModel):
    amount: float = Field(...)
    date: datetime = Field(default=datetime.now(tz=UTC))
    name: str = Field(...)


class Source(BaseModel):
    kind: SourceKind = Field(...)
    details: BankAccountDetails | CryptoWalletDetails = Field(...)
    latest_balances: list[NestedBankAccountBalance] = Field(default=[])
    model_config: ConfigDict = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def check_details_type(self) -> "Source":
        kind = self.kind
        details = self.details

        if kind == SourceKind.BANK_ACCOUNT and not isinstance(
            details, BankAccountDetails
        ):
            raise ValueError("details must be a BankDetails type for bank kind")

        if kind == SourceKind.CRYPTO_WALLET and not isinstance(
            details, CryptoWalletDetails
        ):
            raise ValueError(
                "details must be a CryptoWalletDetails type for crypto_wallet kind"
            )
        return self
