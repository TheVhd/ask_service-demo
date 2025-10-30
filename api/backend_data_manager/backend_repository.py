import asyncio
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient  # motor kütüphanesi kullanılıyor
from api.config.config import Config
from api.models.type_model import Role


class BackendRepository:
    def __init__(self):
        self.loop = asyncio.get_running_loop()
        logging.warning(f"[MONGO-DEBUG] Connecting to Backend MongoDB! URI: {Config.MONGO_BG_DB_URI}")
        logging.warning(f"[MONGO-DEBUG] Username: {Config.MONGO_BG_DB_USER}, Password: {Config.MONGO_BG_DB_PASSWORD}")
        self.client = AsyncIOMotorClient(
            Config.MONGO_BG_DB_URI,
            io_loop=self.loop
        )

        self.db_name = Config.MONGO_BG_DB_NAME
        self._chat_collection_name = Config.MONGO_BG_DB_CHAT_COLLECTION_NAME
        self._session_collection_name = Config.MONGO_BG_DB_SESSION_COLLECTION_NAME

        self.chat_collection = self.client[self.db_name][self._chat_collection_name]
        self.session_collection = self.client[self.db_name][self._session_collection_name]

        # MongoDB için Unique Index oluştur
        asyncio.create_task(self.ensure_indexes())

    async def ensure_indexes(self):
        """MongoDB koleksiyonları için gerekli indexleri oluşturur."""
        try:
            # session_uuid için Unique Index oluştur
            await self.session_collection.create_index([("session_uuid", 1)], unique=True)
            logging.info("Unique index for session_uuid has been created.")
        except Exception as e:
            logging.error(f"Error while creating indexes: {e}")

    async def add_chat_log(self, user_id: str, session_uuid: str, question_uuid: str, question: str, answer: str,
                           prompt_tokens: int, completion_tokens: int, service_name: str = "ask_service"):
        message_data = {
            "user_id": str(user_id),
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
            },
            "service_name": service_name,
            "index_name": None

        }
        try:
            await self.chat_collection.insert_one(message_data)
            logging.info(f"Message added to session: {session_uuid} to Backend MongoDB.")
        except Exception as e:
            logging.error(f"An error occurred while adding message to session: {e}")

    async def add_session_log(self, user_id: str, session_uuid: str, session_name: str,
                              service_name: str = "ask_service"):
        """Yeni bir oturum kaydı ekler. Unique index sayesinde tekrar eklenmesini engeller."""
        message_data = {
            "user_id": str(user_id),
            "session_uuid": session_uuid,
            "session_name": session_name,
            "created_at": datetime.now(timezone.utc),
            "service_name": service_name,
            "is_active": True,
            "is_archived": False
        }

        try:
            await self.session_collection.insert_one(message_data)
            logging.info(f"Session {session_uuid} added to Backend MongoDB.")
        except Exception as e:
            if "duplicate key error" in str(e):
                logging.info(f"Session {session_uuid} already exists, skipping insertion.")
            else:
                logging.error(f"An error occurred while adding session: {e}")
