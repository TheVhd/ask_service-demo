import json
import logging
import redis.asyncio as redis
from redis.exceptions import RedisError
from api.config.config import Config
from api.models.base_message_model import BaseMessage


class RedisService:
    """
    Redis service class.
    """

    def __init__(self):
        """
        RedisService constructor.
        """
        self.redis_url = Config.REDIS_URL
        self.redis_client = None

    async def connect(self):
        """ Connect to Redis. """
        try:
            self.redis_client = await redis.from_url(self.redis_url,
                                                     decode_responses=True,
                                                     socket_timeout=5,
                                                     socket_connect_timeout=5)
            logging.info(f"Connected to Redis at {self.redis_url}")
        except redis.ConnectionError as e:
            logging.error(f"Redis connection error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during Redis connection: {e}")

    async def close(self):
        """ Close the Redis connection. """
        if self.redis_client:
            try:
                await self.redis_client.aclose()
                logging.info("Redis connection closed.")
            except Exception as e:
                logging.error(f"Error closing Redis connection: {e}")

    async def write_to_redis(self, redis_key, chat_data: BaseMessage):
        """
        Serialize the chat data and write it to Redis with a TTL.
        """
        try:
            if not self.redis_client:
                logging.error("Redis client is not connected. Attempting to reconnect...")
                await self.connect()
                if not self.redis_client:
                    logging.error("Failed to reconnect to Redis.")
                    return

            serialized_data = json.dumps(chat_data, ensure_ascii=False)

            set_result = await self.redis_client.set(redis_key, serialized_data)
            if set_result:
                logging.info(f"Chat data written to Redis for session: {redis_key}")
                await self.redis_client.expire(redis_key, 1800)  # 30 dakika TTL

        except RedisError as e:
            logging.error(f"Redis operation failed: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while writing to Redis: {e}")

    async def write_summary_to_redis(self, session_uuid: str, summaries: list):
        """
        Özetlenmiş mesajları Redis'e kaydet.
        :param session_uuid:
        :param session_uuid Session ID
        :param summaries: Özet mesaj listesi
        """
        try:
            if not self.redis_client:
                logging.error("Redis client is not connected. Attempting to reconnect...")
                await self.connect()
                if not self.redis_client:
                    logging.error("Failed to reconnect to Redis.")
                    return

            async with self.redis_client.pipeline() as pipe:
                for idx, summary in enumerate(summaries):
                    redis_key = f"{session_uuid}:summaries:{idx}"
                    serialized_data = json.dumps(summary, ensure_ascii=False)
                    pipe.set(redis_key, serialized_data)
                await pipe.execute()
            logging.info(f"Summaries written to Redis for session: {session_uuid}")

        except RedisError as e:
            logging.error(f"Redis operation failed: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while writing summaries to Redis: {e}")

    async def get_summaries_from_redis(self, session_uuid: str) -> list:
        """
        Redis'ten özetlenmiş mesajları al.
        :param session_uuid: Session ID
        :return: Özet mesaj listesi
        """
        try:
            if not self.redis_client:
                logging.error("Redis client is not connected. Attempting to reconnect...")
                await self.connect()
                if not self.redis_client:
                    logging.error("Failed to reconnect to Redis.")
                    return []

            redis_keys = [f"{session_uuid}:summaries:{idx}" for idx in range(10)]  # Maks 10 özet
            summaries_data = await self.redis_client.mget(redis_keys)
            summaries = [json.loads(data) for data in summaries_data if data]

            logging.info(f"Retrieved {len(summaries)} summaries from Redis for session: {session_uuid}")
            return summaries

        except RedisError as e:
            logging.error(f"Redis operation failed: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error while retrieving summaries from Redis: {e}")
            return []

    async def get_from_redis(self, key: str):
        """
        Get data from Redis.
        """
        try:
            if not self.redis_client:
                logging.error("Redis client is not connected. Attempting to reconnect...")
                await self.connect()
                if not self.redis_client:
                    logging.error("Failed to reconnect to Redis.")
                    return None

            data = await self.redis_client.get(key)
            if data:
                logging.info(f"Data retrieved from Redis for key: {key}")
                return data

        except RedisError as e:
            logging.error(f"Redis operation failed: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while getting data from Redis: {e}")

        return None

    async def get_all_by_session(self, session_id: str):
        """
        Get all records for a specific session_id by scanning Redis.
        :param session_id: The session ID to match keys.
        :return: List of all matching records.
        """
        try:
            if not self.redis_client:
                logging.error("Redis client is not connected. Attempting to reconnect...")
                await self.connect()
                if not self.redis_client:
                    logging.error("Failed to reconnect to Redis.")
                    return []

            # SCAN kullanarak session_id ile başlayan tüm anahtarları al
            pattern = f"{session_id}:*"
            cursor = "0"
            matching_keys = []

            cursor, keys = await self.redis_client.scan(cursor=cursor, match=pattern, count=100)
            matching_keys.extend(keys)

            # Eşleşen anahtarlar için değerleri getir
            if not matching_keys:
                logging.info(f"No records found for session_id: {session_id}")
                return []

            # Redis'ten eşleşen anahtarların verilerini getir
            records = await self.redis_client.mget(matching_keys)
            return [json.loads(record) for record in records if record]

        except Exception as e:
            logging.error(f"Error retrieving records for session_id {session_id}: {e}")
            return []
