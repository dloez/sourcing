import asyncio

from celery import current_app as celery
from motor import motor_asyncio
from sourcing.config import (
    EB_APPLICATION_ID,
    EB_PRIVATE_KEY_FILE_PATH,
    ENVIRONMENT,
    MONGODB_URL,
    Environment,
)
from sourcing.source.aspsp.enable_banking import EnableBankingClient
from sourcing.source.aspsp.models import ASPSP

SUPPORTED_ASPSPS = {
    Environment.DEV: ["_MockASPSP_ES"],
    Environment.PROD: ["BSCHESMMXXX_BancoSantander_ES"],
}


async def get_store_aspsps():
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    aspsps_collection = db.get_collection("apspsps")
    aspsps_collection.create_index("custom_id", unique=True)

    client = EnableBankingClient(
        private_key_file_path=EB_PRIVATE_KEY_FILE_PATH, application_id=EB_APPLICATION_ID
    )
    client.startup()

    supported_aspsps = SUPPORTED_ASPSPS[ENVIRONMENT]
    try:
        aspsps = (await client.get_aspsps("ES"))["aspsps"]
        for aspsp in aspsps:
            custom_id = f"{aspsp.get('bic', '')}_{aspsp['name'].replace(' ', '')}_{aspsp['country']}"

            if custom_id in supported_aspsps:
                clean_aspsp = ASPSP(
                    maximum_consent_validity_seconds=aspsp["maximum_consent_validity"],
                    name=aspsp["name"],
                    country=aspsp["country"],
                    logo_url=aspsp["logo"],
                    custom_id=custom_id,
                )

                found_aspsp = await aspsps_collection.find_one_and_replace(
                    {"custom_id": custom_id},
                    clean_aspsp.model_dump(by_alias=True, exclude=["id"]),
                )
                if not found_aspsp:
                    await aspsps_collection.insert_one(
                        clean_aspsp.model_dump(exclude=["id"]),
                    )
    finally:
        await client.clean_up()


@celery.task(name="wrap_get_store_aspsps")
def wrap_get_store_aspsps():
    asyncio.run(get_store_aspsps())


if __name__ == "__main__":
    asyncio.run(get_store_aspsps())
