from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sourcing.source.crypto_wallet.db import coins_collection
from sourcing.source.crypto_wallet.models import (
    Coin,
    CryptoWalletSourceDetails,
    RequestCryptoWallet,
)
from sourcing.source.models import Source, SourceKind
from sourcing.user.auth import get_current_user
from sourcing.user.db import users_collection
from sourcing.user.models import User

router = APIRouter(
    prefix="/cryptowallets",
)


@router.get("/coins/", response_model=List[Coin])
async def list_coins():
    return [coin async for coin in coins_collection.find()]


@router.post("/")
async def create_wallet_source(
    request_crypto_wallet: RequestCryptoWallet,
    current_user: User = Depends(get_current_user),
):
    coin = await coins_collection.find_one({"symbol": request_crypto_wallet.coin})
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not supported")

    source_details = CryptoWalletSourceDetails(
        coin=Coin(**coin),
        wallet_address=request_crypto_wallet.wallet_address,
    )
    source = Source(
        kind=SourceKind.CRYPTO_WALLET,
        details=source_details,
    )

    found = False
    for s in current_user.sources:
        if s.kind != SourceKind.CRYPTO_WALLET:
            continue

        if s.details.wallet_address != source.details.wallet_address:
            continue

        found = True
        await users_collection.update_one(
            {
                "_id": current_user.id,
                "sources.details.wallet_address": source.details.wallet_address,
            },
            {"$set": {"sources.$": source.model_dump()}},
        )

    if not found:
        await users_collection.update_one(
            {"_id": current_user.id},
            {"$push": {"sources": source.model_dump()}},
        )
    return {"status": "ok"}
