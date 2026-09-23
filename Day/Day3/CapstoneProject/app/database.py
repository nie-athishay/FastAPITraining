from pymongo import MongoClient
from pymongo.database import Database

from app.config import settings

#MongoClient manages  a pool of connections to the MOngoDB Server 
client : MongoClient = MongoClient(settings.MONGO_URI)
database: Database = client[settings.MONGO_DB_NAME]

#sends a pig command to MongoDB to confirm the connection is live
def ping_database() -> bool:
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False