from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
import uuid


class PromptError(Exception):
    pass


class DuplicatePromptError(PromptError):
    pass


class PromptType(str, Enum):
    ASK = "AskPrompt"
    TUTOR = "TutorialPrompt"
    EXAM = "ExamPrompt"
    TEST = "TestPrompt"
    QUIZ = "QuizPrompt"
    SUMMARY = "SummaryPrompt"


class PromptName(str, Enum):
    science = "SciencePrompt"
    math = "MathPrompt"
    history = "HistoryPrompt"
    english = "EnglishPrompt"


class PromptRequest(BaseModel):
    type: PromptType
    template: str
    placeholders: List[str]
    description: Optional[str] = "No description provided."


class Prompt(PromptRequest):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __format__(self, format_spec: Dict[str, str]):
        """
        Allow the template to be formatted with dynamic values.

        :param format_spec: A dictionary containing the keys and values for formatting.
        :return: The formatted string.
        """
        if not isinstance(format_spec, dict):
            raise ValueError("Format specification must be a dictionary.")
        return self.template.format_map(format_spec)
