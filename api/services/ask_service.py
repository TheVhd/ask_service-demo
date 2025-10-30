import asyncio
from typing import List, Optional, Dict

import openai
from uuid import uuid4
from datetime import datetime, timezone
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from api.backend_data_manager import BackendRepository
from api.config.config import Config
from api.config.logger import logging
from api.models import QueryRequest, QueryResponse
from api.models.base_message_model import BaseMessage
from api.models.type_model import Role, MessageType
from api.prompts.ask_prompt import AskPrompt

from api.repositories.messages_repository import MongoDBRepository
from api.services.redis_service import RedisService


class AskService:
    def __init__(self):
        self._mongo_repository = MongoDBRepository()
        self._redis_service = RedisService()
        self._question_uuid = str(uuid4())
        self._session_uuid = None
        self._session_history_messages = None

        logging.warning("🚀 [MONGO-DEBUG] BackendRepository (Backend MongoDB) bağlantısı şimdi başlatılıyor...")
        logging.warning(f"🔑 [MONGO-DEBUG] Backend MongoDB URI: {Config.MONGO_BG_DB_URI}")
        logging.warning(f"🧑‍💻 [MONGO-DEBUG] Backend MongoDB Username: {Config.MONGO_USER}, Password: {Config.MONGO_PASSWORD}")
        self._backend_data_saver = BackendRepository()

    async def execute_ask_query_service(self, query: QueryRequest, user_data: dict):
        """
        Execute the Ask Service with the given query.
        """
        logging.info(f"Executing AskService with query")
        user_id = str(user_data["user_id"])

        if query.sessionID:
            self._session_uuid = str(query.sessionID)
            self._session_history_messages = await self._get_chat_history(self._session_uuid)
        else:
            self._session_uuid = str(uuid4())

        logging.info(f"Model invoked")
        response = await self._query_openai(query.question, self._session_history_messages)

        result = QueryResponse(answer=response["response"],
                               session_id=self._session_uuid,
                               question=query.question,
                               service_name="ask_service",
                               prompt_tokens=response["prompt_tokens"],
                               completion_tokens=response["completion_tokens"]
                               )

        asyncio.create_task(self._run_background_tasks(chat_log_data=result,
                                                       session_name=query.question[:50],
                                                       user_id=user_id))
        logging.info(f"response received")
        logging.info(f"Saved to db")
        return result, None

    async def _get_chat_history(self, session_uuid: str) -> List[BaseMessage]:
        """
        Fetch chat history for a session by session ID.
        Prioritize Redis, fallback to MongoDB if not found.
        """
        try:

            chat_records = await self._mongo_repository.get_session_history(session_uuid=session_uuid)
            messages = self._convert_chat_hist_to_messages(chat_records)
            return messages

        except Exception as e:
            logging.error(f"Error retrieving chat history from Redis and MongoDB: {e}")
            return []

    async def _run_background_tasks(self, chat_log_data: QueryResponse, session_name: str, user_id: str):
        """
        Runs all background database tasks concurrently.
        """
        tasks = [
            self._add_chat_log(chat_log_data=chat_log_data),
            self._save_to_backend_db(chat_log_data=chat_log_data, session_name=session_name, user_id=user_id)
        ]

        for task in tasks:
            asyncio.create_task(self._handle_background_task(task))

    async def _add_chat_log(self, chat_log_data: QueryResponse):
        """
        Add chat log to MongoDB and Redis.
        """
        # save chat log to MongoDB
        asyncio.create_task(self._mongo_repository.add_chat_log(session_uuid=chat_log_data.session_id,
                                                                question_uuid=self._question_uuid,
                                                                question=chat_log_data.question,
                                                                answer=chat_log_data.answer,
                                                                prompt_tokens=chat_log_data.prompt_tokens,
                                                                completion_tokens=chat_log_data.completion_tokens))

    async def _save_to_backend_db(self, chat_log_data: QueryResponse, session_name: str, user_id: str):
        """
        Save chat log to backend database.
        """
        asyncio.create_task(self._backend_data_saver.add_chat_log(
            user_id=user_id,
            session_uuid=chat_log_data.session_id,
            question_uuid=self._question_uuid,
            question=chat_log_data.question,
            answer=chat_log_data.answer,
            prompt_tokens=int(chat_log_data.prompt_tokens),
            completion_tokens=int(chat_log_data.completion_tokens)
        ))

        asyncio.create_task(self._backend_data_saver.add_session_log(
            user_id=user_id,
            session_uuid=chat_log_data.session_id,
            session_name=session_name
        ))

    @classmethod
    def _convert_chat_hist_to_messages(cls, chat_hist: List[dict]) -> List[BaseMessage]:
        messages: List[BaseMessage] = []

        for entry in chat_hist:
            question = entry.get('question')
            if question:
                messages.append(HumanMessage(content=question['content']))

            answer = entry.get('answer')
            if answer:
                messages.append(AIMessage(content=answer['content']))

        return messages

    @classmethod
    async def _query_openai(cls, content: str, messages: List[BaseMessage]):
        """
        Query OpenAI with the given prompt and chat history.
        :param content: The new user input to be appended to the chat history.
        :param messages: The chat history as a list of BaseMessage objects.
        :return: The assistant's response as a dictionary.
        """
        try:

            prompt = AskPrompt
            openai.api_key = Config.OPENAI_API_KEY
            openai_messages = [{"role": "system", "content": prompt}]

            # Mesaj geçmişini işleme
            if messages:
                for message in messages:
                    if isinstance(message, HumanMessage):
                        role = "user"
                    elif isinstance(message, AIMessage):
                        role = "assistant"
                    else:
                        raise ValueError(f"Invalid message format: {message}")

                    openai_messages.append({"role": role, "content": message.content})

            # Yeni kullanıcı girdisini ekleme
            openai_messages.append({"role": "user", "content": content})

            # OpenAI'ye istek gönderme
            response = await openai.ChatCompletion.acreate(
                model=Config.LLM_MODEL_NAME,
                messages=openai_messages
            )

            # Yanıtın içeriği
            assistant_response = response['choices'][0]['message']['content']

            # Token bilgileri
            usage = response.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)

            return {
                "response": assistant_response,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }

        except Exception as e:
            logging.error("Error querying OpenAI: %s", e)
            raise

    @classmethod
    async def _handle_background_task(cls, task):
        """
        Runs a background task and logs any exceptions that occur.
        """
        try:
            await task
        except Exception as e:
            logging.error(f"Background task failed: {e}")
