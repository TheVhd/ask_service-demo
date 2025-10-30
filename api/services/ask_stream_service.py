import uuid
from openai import AsyncOpenAI
from api.config.config import Config
from api.services.ask_service import AskService
from langchain.schema import HumanMessage, AIMessage
from api.prompts.ask_prompt import AskPrompt
import json
import re

class AskStreamService:
    def __init__(self):
        self.ask_service = AskService()
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def get_history(self, session_id):
        if session_id:
            return await self.ask_service._get_chat_history(session_id)
        return []

    async def save_message(self, session_id, question, answer, prompt_tokens=0, completion_tokens=0, user_id=None):
        from api.models.query_model import QueryResponse
        result = QueryResponse(
            answer=answer,
            session_id=session_id,
            question=question,
            service_name="ask_service",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )
        await self.ask_service._run_background_tasks(result, question[:50], user_id or "stream_user")

    async def stream_openai_response(self, question, session_id=None, user_id=None):
        if session_id:
            session_id_str = str(session_id)
        else:
            session_id_str = str(uuid.uuid4())
        history = await self.get_history(session_id_str)
        openai_messages = [{"role": "system", "content": AskPrompt}]
        if history:
            for message in history:
                if isinstance(message, HumanMessage):
                    role = "user"
                elif isinstance(message, AIMessage):
                    role = "assistant"
                else:
                    continue
                openai_messages.append({"role": role, "content": message.content})
        openai_messages.append({"role": "user", "content": question})
        stream = await self.client.chat.completions.create(
            model=Config.LLM_MODEL_NAME,
            messages=openai_messages,
            stream=True
        )
        full_answer = ""
        prompt_tokens = 0
        completion_tokens = 0
        buffer = ""
        sentence_end_re = re.compile(r"([.!?\n]+)")
        # 1. İlk chunk olarak sessionID'yi gönder
        yield json.dumps({"sessionID": session_id_str, "type": "session_info"})
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                buffer += token
                # Cümle sonu veya satır sonu varsa buffer'ı chunk olarak gönder
                while True:
                    match = sentence_end_re.search(buffer)
                    if not match:
                        break
                    end_idx = match.end()
                    sentence = buffer[:end_idx]
                    is_newline = "\n" in sentence
                    chunk_obj = {
                        "content": sentence,
                        "is_newline": is_newline,
                        "format": "markdown"
                    }
                    yield json.dumps(chunk_obj)
                    buffer = buffer[end_idx:]
                full_answer += token
            if chunk.usage:
                prompt_tokens = chunk.usage.prompt_tokens or 0
                completion_tokens = chunk.usage.completion_tokens or 0
        # Kalan buffer'da cümle sonu yoksa, kalan kısmı da gönder
        if buffer.strip():
            is_newline = "\n" in buffer
            chunk_obj = {
                "content": buffer,
                "is_newline": is_newline,
                "format": "markdown"
            }
            yield json.dumps(chunk_obj)
        # Final answer chunk (sessionID ile birlikte)
        final_chunk = {
            "final_answer": True,
            "content": full_answer,
            "is_newline": True,
            "format": "markdown",
            "sessionID": session_id_str
        }
        yield json.dumps(final_chunk)
        await self.save_message(session_id_str, question, full_answer, prompt_tokens, completion_tokens, user_id)
