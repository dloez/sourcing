from sourcing.db import db


refresh_tokens_collection = db.get_collection("refresh_tokens")
refresh_tokens_collection.create_index("refresh_token", unique=True)
