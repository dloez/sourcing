import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv


class Environment(Enum):
    DEV = "dev"
    PROD = "prod"

    def __str__(self):
        return str(self.value)


ENVIRONMENT = Environment.DEV
load_dotenv(f"{ENVIRONMENT}.env")

# DB Settings
MONGODB_URL = os.environ["MONGODB_URL"]
REDIS_URL = os.environ["REDIS_URL"]

# Security Settings
ACCESS_SECRET_KEY = os.environ["ACCESS_SECRET_KEY"]
REFRESH_SECRET_KEY = os.environ["REFRESH_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 43800

# Enable banking
EB_PRIVATE_KEY_FILE_PATH = Path(os.environ["EB_PRIVATE_KEY_FILE_PATH"])
EB_APPLICATION_ID = os.environ["EB_APPLICATION_ID"]
