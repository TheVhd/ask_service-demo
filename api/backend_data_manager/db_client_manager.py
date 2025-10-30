import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from api.config.config import Config


class MongoDbClientManager:
    _client = None

    @staticmethod
    def get_client():
        """Get or initialize the MongoDB client."""
        if MongoDbClientManager._client is None:
            try:
                logging.warning(f"[MONGO-DEBUG] Connecting to Backend MongoDB! URI: {Config.MONGO_BG_DB_URI}")
                logging.warning(f"[MONGO-DEBUG] Username: {Config.MONGO_USER}, Password: {Config.MONGO_PASSWORD}")
                logging.info("Bağlantı havuzu ve zaman aşımı ayarlari")
                MongoDbClientManager._client = AsyncIOMotorClient(
                    Config.MONGO_BG_DB_URI,
                    maxPoolSize=50,  # Maksimum bağlantı havuzu boyutu
                    minPoolSize=5,  # Minimum bağlantı havuzu boyutu
                    socketTimeoutMS=30000,  # Soket zaman aşımı (ms)
                    serverSelectionTimeoutMS=30000,
                    maxIdleTimeMS=60000)  # Sunucu seçimi zaman aşımı (ms)
                MongoDbClientManager._client.admin.command("ping")
                logging.info("MongoDB Backend client initialized successfully.")
            except ConnectionFailure as e:
                logging.error(f"[MONGO-DEBUG] MongoDB Backend connection failed: {e}")
                raise
            except Exception as e:
                logging.error(f"[MONGO-DEBUG] Unexpected error initializing MongoDB Backend client: {e}")
                raise
        return MongoDbClientManager._client

    @staticmethod
    def get_database(db_name: str):
        """Retrieve a database by name."""
        try:
            client = MongoDbClientManager.get_client()
            return client[db_name]
        except Exception as e:
            logging.error(f"Error accessing database '{db_name}': {e}")
            raise
