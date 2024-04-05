from sourcing.db import db


users_collection = db.get_collection("users")
users_collection.create_index("email", unique=True)
