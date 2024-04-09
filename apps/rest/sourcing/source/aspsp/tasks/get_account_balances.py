import asyncio

from bson import ObjectId
from celery import current_app as celery
from motor import motor_asyncio
from sourcing.config import (
    EB_APPLICATION_ID,
    EB_PRIVATE_KEY_FILE_PATH,
    MONGODB_URL,
    Environment,
)
from sourcing.enable_banking.client import EnableBankingClient
from sourcing.source.models import (
    BankAccountBalance,
    SourceKind,
)
from sourcing.user.models import User

SUPPORTED_ASPSPS = {
    Environment.DEV: ["_MockASPSP_ES"],
    Environment.PROD: ["BSCHESMMXXX_BancoSantander_ES"],
}


async def get_bank_account_balances(eb_uid: str, eb_id_hash: str, user_id: str):
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    users_collection = db.get_collection("users")
    balances_collection = db.get_collection("balances")

    client = EnableBankingClient(
        private_key_file_path=EB_PRIVATE_KEY_FILE_PATH, application_id=EB_APPLICATION_ID
    )
    client.startup()

    try:
        balances = await client.get_account_balances(eb_uid)
        for balance in balances.get("balances", []):
            bank_account_balance = BankAccountBalance(
                amount=balance.get("balance_amount", {}).get("amount", 0),
                source_id=eb_id_hash,
                name=balance["name"],
            )
            await balances_collection.insert_one(
                bank_account_balance.model_dump(exclude=["id"]),
            )

            updated = await users_collection.find_one_and_update(
                {
                    "_id": ObjectId(user_id),
                },
                {
                    "$set": {
                        "sources.$[source].latest_balances.$[balance]": bank_account_balance.to_nested().model_dump()
                    }
                },
                array_filters=[
                    {"source.details.eb_id_hash": eb_id_hash},
                    {"balance.name": bank_account_balance.name},
                ],
            )

            if not updated:
                await users_collection.update_one(
                    {
                        "_id": ObjectId(user_id),
                        "sources.details.eb_id_hash": eb_id_hash,
                    },
                    {
                        "$push": {
                            "sources.$.latest_balances": bank_account_balance.to_nested().model_dump()
                        }
                    },
                )
    finally:
        await client.clean_up()


@celery.task(name="wrap_get_bank_account_balances")
def wrap_get_bank_account_balances(eb_uid: str, eb_id_hash: str, user_id: str):
    asyncio.run(get_bank_account_balances(eb_uid, eb_id_hash, user_id))


async def spawn_users_balance_collectors(test=False):
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    users_collection = db.get_collection("users")

    async for user in users_collection.find({}):
        user = User(**user)
        for source in user.sources:
            if source.kind == SourceKind.BANK_ACCOUNT:
                if not test:
                    celery.send_task(
                        "wrap_get_bank_account_balances",
                        args=(
                            source.details.eb_uid,
                            source.details.eb_id_hash,
                            user.id,
                        ),
                    )
                else:
                    await get_bank_account_balances(
                        source.details.eb_uid, source.details.eb_id_hash, user.id
                    )


@celery.task(name="wrap_spawn_users_balance_collectors")
def wrap_spawn_users_balance_collectors():
    asyncio.run(spawn_users_balance_collectors())


if __name__ == "__main__":
    asyncio.run(spawn_users_balance_collectors(test=True))
