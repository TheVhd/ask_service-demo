import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_HOST = os.getenv("MONGO_HOST")
    MONGO_PORT = int(os.getenv("MONGO_PORT"))
    MONGO_USER = os.getenv("MONGO_USER")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGO_DB_SESSIONS_COLLECTION_NAME = os.getenv("MONGO_DB_SESSION_COLLECTION_NAME")
    MONGO_DB_PROMPT_COLLECTION_NAME = os.getenv("MONGO_DB_PROMPT_COLLECTION_NAME")

    MONGO_BG_DB_URI = os.getenv("MONGO_BG_DB_URI")
    MONGO_BG_DB_NAME = os.getenv("MONGO_BG_DB_NAME")
    MONGO_BG_DB_HOST = os.getenv("MONGO_BG_DB_HOST")
    MONGO_BG_DB_PORT = int(os.getenv("MONGO_BG_DB_PORT"))
    MONGO_BG_DB_USER = os.getenv("MONGO_BG_DB_USER")
    MONGO_BG_DB_PASSWORD = os.getenv("MONGO_BG_DB_PASSWORD")
    MONGO_BG_DB_CHAT_COLLECTION_NAME = os.getenv("MONGO_BG_DB_CHAT_COLLECTION_NAME")
    MONGO_BG_DB_SESSION_COLLECTION_NAME = os.getenv("MONGO_BG_DB_SESSION_COLLECTION_NAME")

    REDIS_URL = os.getenv("REDIS_URL")

    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # PostgreSQL bağlantı URL'si
    # POSTGRES_URL = f"postgresql+asyncpg://{PSQL_DB_USER}:{PSQL_DB_PASSWORD}@{PSQL_DB_HOST}:{PSQL_DB_PORT}/{PSQL_DB_NAME}"
    POSTGRES_URL = os.getenv("POSTGRES_URL")

    BACKEND_API_SECRET_KEY = "django-insecure---q#8j=*zyjms%y3z%dwi37(psp11)4c@mvr=(&$1oa7yjmb2k"
