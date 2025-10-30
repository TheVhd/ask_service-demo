from enum import Enum


class Role(Enum):
    SYSTEM = "system"
    USER = "backend_data_manager"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"
    DEVELOPER = "developer"


class MessageType(Enum):
    TEXT = "text"
    SUMMARY = "summary"
    PROMPT = "prompt"
    SYSTEM = "system"