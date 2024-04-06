import os
from pathlib import Path

# DB Settings
MONGODB_URL = os.environ["MONGODB_URL"]

# Security Settings
ACCESS_SECRET_KEY = os.environ["ACCESS_SECRET_KEY"]
REFRESH_SECRET_KEY = os.environ["REFRESH_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 43800

# Enable banking
EB_PRIVATE_KEY_FILE_PATH = Path("enable-banking-key.pem")
EB_APPLICATION_ID = os.environ["EB_APPLICATION_ID"]
