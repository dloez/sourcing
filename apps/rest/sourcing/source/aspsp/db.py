from sourcing.db import db

aspsps_collection = db.get_collection("apspsps")
aspsps_collection.create_index("custom_id", unique=True)
