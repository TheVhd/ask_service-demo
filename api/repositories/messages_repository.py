import asyncio
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient  # motor kütüphanesi kullanılıyor
from api.config.config import Config
from api.models.type_model import Role


class MongoDBRepository:
    def __init__(self):
        # AsyncIOMotorClient kullanımı, mevcut event loop ile bağlanıyor
        self.loop = asyncio.get_running_loop()
        logging.warning(f"[MONGO-DEBUG] Connecting to MongoDB! URI: {Config.MONGO_URI}")
        logging.warning(f"[MONGO-DEBUG] Username: {Config.MONGO_USER}, Password: {Config.MONGO_PASSWORD}")
        self.client = AsyncIOMotorClient(
            Config.MONGO_URI,
            io_loop=self.loop  # Event loop bağlantısı
        )

        self.db_name = Config.MONGO_DB_NAME
        self.collection_name = Config.MONGO_DB_SESSIONS_COLLECTION_NAME
        self.collection = self.client[self.db_name][self.collection_name]

        # Index oluşturmayı asenkron başlat
        asyncio.create_task(self.ensure_indexes())

    async def ensure_indexes(self):
        """MongoDB koleksiyonları için gerekli indexleri oluşturur."""
        try:
            await self.collection.create_index([("session_uuid", 1)])
            logging.info("Index created for session_uuid.")
        except Exception as e:
            logging.error(f"Error while creating index: {e}")

    async def add_chat_log(self, session_uuid: str, question_uuid: str, question: str, answer: str, prompt_tokens: int,
                           completion_tokens: int):
        message_data = {
            "session_uuid": session_uuid,
            "question_uuid": question_uuid,
            "simplified": {
                "question": {
                    "role": "user",
                    "content": question
                },
                "answer": {
                    "role": "assistant",
                    "content": answer
                }
            },
            "created_at": datetime.now(timezone.utc),
            "token_count": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }
        }
        try:
            # Arka planda ekleme yap
            await self.collection.insert_one(message_data)
            logging.info(f"Message added to session: {session_uuid} to MongoDB.")
        except Exception as e:
            logging.error(f"An error occurred while adding message to session: {e}")

    async def get_session_history(self, session_uuid: str):
        try:
            # Projection ile sadece gerekli alanları çekiyoruz
            cursor = self.collection.find(
                {"session_uuid": session_uuid},
                projection={"simplified": 1, "_id": 0}  # Sadece simplified'ı al, _id'yi alma
            ).sort("created_at", 1)

            session_data = await cursor.to_list(length=None)
            return [item['simplified'] for item in session_data]
        except Exception as e:
            logging.error(f"Error fetching session history: {e}")
            return []
