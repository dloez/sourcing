import asyncio

from motor import motor_asyncio

from sourcing.config import EB_APPLICATION_ID, EB_PRIVATE_KEY_FILE_PATH, MONGODB_URL
from sourcing.enable_banking.client import EnableBankingClient
from sourcing.source.aspsp.models import ASPSP

SUPPORTED_ASPSPS = ["BSCHESMMXXX_BancoSantander_ES"]


async def main():
    db_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = db_client.get_database("sourcing")
    aspsps_collection = db.get_collection("apspsps")
    aspsps_collection.create_index("custom_id", unique=True)

    client = EnableBankingClient(
        private_key_file_path=EB_PRIVATE_KEY_FILE_PATH, application_id=EB_APPLICATION_ID
    )

    try:
        aspsps = (await client.get_aspsps("ES"))["aspsps"]
        for aspsp in aspsps:
            custom_id = f"{aspsp.get("bic", "")}_{aspsp["name"].replace(" ", "")}_{aspsp["country"]}"

            if custom_id in SUPPORTED_ASPSPS:
                clean_aspsp = ASPSP(
                    maximum_consent_validity_seconds=aspsp["maximum_consent_validity"],
                    name=aspsp["name"],
                    logo_uri=aspsp["logo"],
                    custom_id=custom_id,
                )

                found_aspsp = await aspsps_collection.find_one({"custom_id": custom_id})
                if not found_aspsp:
                    await aspsps_collection.insert_one(clean_aspsp.model_dump())
    finally:
        await client.clean_up()


if __name__ == "__main__":
    asyncio.run(main())
