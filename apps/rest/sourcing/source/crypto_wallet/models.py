from pydantic import BaseModel, Field


class Coin(BaseModel):
    symbol: str = Field(max_length=3, min_length=3)


class CryptoWalletSourceDetails(BaseModel):
    wallet_address: str = Field()
    coin: Coin = Field()


class RequestCryptoWallet(BaseModel):
    wallet_address: str
    coin: str
