from api.models import Prompt
from api.models.prompt_model import PromptType, PromptError, DuplicatePromptError
from api.repositories.prompts_repository import MongoDBPromptRepository
from api.config.logger import logging
from pymongo.errors import DuplicateKeyError

# Logger instance for PromptService
logger = logging.getLogger("PromptService")


class PromptService:
    def __init__(self):
        """
        Initialize the PromptService with a MongoDBPromptRepository
        """
        self.repository = MongoDBPromptRepository()

    async def get_all_prompts(self):
        """
        Get all the available prompts.
        """
        try:
            prompts = await self.repository.list_all_prompts()
            logger.info(f"Successfully fetched {len(prompts)} prompts.")
            return prompts
        except Exception as e:
            logger.error(f"Error fetching all prompts: {e}", exc_info=True)
            raise ValueError(f"Error fetching all prompts: {e}")

    async def get_prompt_by_type(self, prompt_type: PromptType):
        """
        Fetch a specific prompt by its type.
        """
        try:
            prompt = await self.repository.get_prompt(prompt_type.value)
            if not prompt:
                logger.warning(f"Prompt type '{prompt_type}' not found.")
                raise PromptError(f"Prompt type '{prompt_type}' not found")

            if "date_time" not in prompt.get("placeholders", []):
                prompt["template"] += "\nDate: {date_time}"
                prompt["placeholders"].append("date_time")
                logger.info("Added date_time placeholder and updated template.")

            return Prompt(**prompt)
        except Exception as e:
            logger.error(f"Error fetching prompt by type '{prompt_type}': {e}", exc_info=True)
            raise PromptError(f"Error fetching prompt by type: {e}")

    async def add_prompt(self, prompt_data: dict):
        """
        Create a new prompt.
        """
        try:
            new_prompt = Prompt(**prompt_data)
            await self.repository.add_prompt(new_prompt)
            logger.info(f"Successfully added new prompt: {new_prompt.id}")
            return new_prompt
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate prompt ID detected: {e}")
            raise DuplicatePromptError("A prompt with this ID already exists.")
        except Exception as e:
            logger.error(f"Error adding new prompt: {e}", exc_info=True)
            raise PromptError(f"Error adding new prompt: {e}")


    async def update_prompt(self, prompt_type: str, updated_data: dict):
        """
        Update an existing prompt by its type.
        """
        try:
            existing_prompt = await self.repository.get_prompt(prompt_type)
            if not existing_prompt:
                logger.warning(f"Prompt type '{prompt_type}' not found for update.")
                raise PromptError(f"Prompt type '{prompt_type}' not found")
            await self.repository.update_prompt(
                prompt_type=prompt_type,
                **{k: v for k, v in updated_data.items() if v is not None}
            )
            logger.info(f"Successfully updated prompt: {prompt_type}")
        except Exception as e:
            logger.error(f"Error updating prompt '{prompt_type}': {e}", exc_info=True)
            raise PromptError(f"Error updating prompt: {e}")

    async def delete_prompt(self, prompt_uuid: str):
        """
        Delete a prompt by its UUID.
        """
        try:
            result = await self.repository.delete_prompt(prompt_uuid)
            if not result:
                logger.warning(f"Prompt type '{prompt_uuid}' not found for deletion.")
                raise ValueError(f"Prompt type '{prompt_uuid}' not found")
            logger.info(f"Successfully deleted prompt: {prompt_uuid}")
        except Exception as e:
            logger.error(f"Error deleting prompt '{prompt_uuid}': {e}", exc_info=True)
            raise ValueError(f"Error deleting prompt: {e}")
