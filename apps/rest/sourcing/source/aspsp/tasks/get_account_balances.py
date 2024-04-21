import asyncio
from typing import List

from bson import ObjectId
from celery import current_app as celery
from motor import motor_asyncio
from sourcing.config import (
    EB_APPLICATION_ID,
    EB_PRIVATE_KEY_FILE_PATH,
    MONGODB_URL,
    Environment,
)
from sourcing.source.aspsp.enable_banking import EnableBankingClient
from sourcing.source.models import Balance, SourceKind
from sourcing.user.models import User

SUPPORTED_ASPSPS = {
    Environment.DEV: ["_MockASPSP_ES"],
    Environment.PROD: ["BSCHESMMXXX_BancoSantander_ES"],
}


async def _get_aspsp_balances(
    source_id: str, eb_uid: str, eb_id_hash: str, user_id: str
):
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    users_collection = db.get_collection("users")
    balances_collection = db.get_collection("balances")

    client = EnableBankingClient(
        private_key_file_path=EB_PRIVATE_KEY_FILE_PATH, application_id=EB_APPLICATION_ID
    )
    client.startup()

    try:
        eb_balances = await client.get_account_balances(eb_uid)
        balances: List[dict] = []
        for eb_balance in eb_balances.get("balances", []):
            balance = Balance(
                amount=eb_balance.get("balance_amount", {}).get("amount", 0),
                source_id=source_id,
                name=eb_balance["name"],
            )
            await balances_collection.insert_one(
                balance.model_dump(exclude=["id"]),
            )
            balances.append(balance.to_nested().model_dump())

        await users_collection.update_one(
            {
                "_id": ObjectId(user_id),
                "sources.id": ObjectId(source_id),
            },
            {
                "$set": {
                    "sources.$.latest_balances": balances,
                }
            },
        )
    finally:
        await client.clean_up()


@celery.task(name="_wrap_get_aspsp_balances")
def _wrap_get_aspsp_balances(
    source_id: str, eb_uid: str, eb_id_hash: str, user_id: str
):
    asyncio.run(_get_aspsp_balances(source_id, eb_uid, eb_id_hash, user_id))


async def spawn_users_aspsps_balance_collectors(test=False):
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    users_collection = db.get_collection("users")

    async for user in users_collection.find({}):
        user = User(**user)
        for source in user.sources:
            if source.kind != SourceKind.ASPSP:
                continue

            if not test:
                celery.send_task(
                    "_wrap_get_aspsp_balances",
                    args=(
                        str(source.id),
                        source.details.eb_uid,
                        source.details.eb_id_hash,
                        str(user.id),
                    ),
                )
            else:
                await _get_aspsp_balances(
                    str(source.id),
                    source.details.eb_uid,
                    source.details.eb_id_hash,
                    str(user.id),
                )


@celery.task(name="wrap_spawn_users_aspsps_balance_collectors")
def wrap_spawn_users_aspsps_balance_collectors():
    asyncio.run(spawn_users_aspsps_balance_collectors())


if __name__ == "__main__":
    asyncio.run(spawn_users_aspsps_balance_collectors(test=True))
