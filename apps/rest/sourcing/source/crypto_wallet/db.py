from sourcing.db import db

coins_collection = db.get_collection("coins")
coins_collection.create_index("symbol", unique=True)
