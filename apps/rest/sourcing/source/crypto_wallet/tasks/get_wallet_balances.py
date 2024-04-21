import asyncio

from bson import ObjectId
from celery import current_app as celery
from motor import motor_asyncio
from sourcing.config import (
    MONGODB_URL,
)
from sourcing.source.crypto_wallet.blockchain import BlockchainClient
from sourcing.source.models import Balance, SourceKind
from sourcing.user.models import User


async def _get_wallet_balance(
    source_id: str, wallet_address: str, coin_symbol: str, user_id: str
):
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    users_collection = db.get_collection("users")
    balances_collection = db.get_collection("balances")

    client = BlockchainClient()
    client.startup()

    try:
        wallet_data = await client.get_address_data(coin_symbol, wallet_address)
        balance = Balance(
            amount=wallet_data.get("balance", 0),
            source_id=source_id,
            name="",
        )

        await balances_collection.insert_one(
            balance.model_dump(),
        )

        await users_collection.update_one(
            {"_id": ObjectId(user_id), "sources.id": ObjectId(source_id)},
            {"$set": {"sources.$.latest_balances": [balance.to_nested().model_dump()]}},
        )
    finally:
        await client.clean_up()


@celery.task(name="_wrap_get_wallet_balance")
def _wrap_get_wallet_balance(
    source_id: str, wallet_address: str, coin_symbol: str, user_id: str
):
    asyncio.run(_get_wallet_balance(source_id, wallet_address, coin_symbol, user_id))


async def spawn_users_wallets_balance_collectors(test=False):
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    users_collection = db.get_collection("users")

    async for user in users_collection.find({}):
        user = User(**user)
        for source in user.sources:
            if source.kind != SourceKind.CRYPTO_WALLET:
                continue

            if not test:
                celery.send_task(
                    "_wrap_get_wallet_balance",
                    args=(
                        str(source.id),
                        source.details.wallet_address,
                        source.details.coin.symbol,
                        str(user.id),
                    ),
                )
            else:
                await _get_wallet_balance(
                    str(source.id),
                    source.details.wallet_address,
                    source.details.coin.symbol,
                    str(user.id),
                )


@celery.task(name="wrap_spawn_users_wallets_balance_collectors")
def wrap_spawn_users_wallets_balance_collectors():
    asyncio.run(spawn_users_wallets_balance_collectors())


if __name__ == "__main__":
    asyncio.run(spawn_users_wallets_balance_collectors(test=True))
