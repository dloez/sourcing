import os

from motor import motor_asyncio


client = motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.get_database("sourcing")
