from motor import motor_asyncio

from sourcing.config import MONGODB_URL

client = motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("sourcing")
