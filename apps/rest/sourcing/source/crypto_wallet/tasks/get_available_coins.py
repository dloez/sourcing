import asyncio

from motor import motor_asyncio
from sourcing.config import MONGODB_URL
from sourcing.source.crypto_wallet.models import Coin

SUPPORTED_COINTS = ({"symbol": "BTC"}, {"symbol": "ETH"})


async def get_store_coins():
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    coins_collection = db.get_collection("coins")
    coins_collection.create_index("symbol", unique=True)

    for c in SUPPORTED_COINTS:
        coin = Coin(symbol=c["symbol"])
        found_coin = await coins_collection.find_one_and_replace(
            {"symbol": coin.symbol},
            coin.model_dump(by_alias=True, exclude=["id"]),
        )

        if not found_coin:
            await coins_collection.insert_one(
                coin.model_dump(exclude=["id"]),
            )


if __name__ == "__main__":
    asyncio.run(get_store_coins())
