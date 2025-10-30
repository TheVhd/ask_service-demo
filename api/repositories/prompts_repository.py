import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from pymongo.errors import PyMongoError

from api.config.config import Config
from api.db.mongo_client_manager import MongoClientManager
from api.models import Prompt


class MongoDBPromptRepository:
    def __init__(self):
        self.db_name = Config.MONGO_DB_NAME
        self.collection_name = Config.MONGO_DB_PROMPT_COLLECTION_NAME
        self.collection = MongoClientManager.get_database(self.db_name)[self.collection_name]

    async def add_prompt(self, prompt: Prompt):
        prompt_data = prompt.model_dump()
        try:
            await self.collection.insert_one(prompt_data)
            logging.info(f"Prompt added successfully: {prompt_data['type']}")
            return True
        except PyMongoError as e:
            logging.error(f"Error adding prompt: {e}")
            return False

    async def get_prompt(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        try:
            cursor = self.collection.find({"type": prompt_type}).sort("created_at", -1).limit(1)
            prompt_list = await cursor.to_list(length=1)

            if not prompt_list:
                logging.warning(f"Prompt not found: {prompt_type}")
                return None
            return prompt_list[0]

        except PyMongoError as e:
            logging.error(f"Error fetching prompt: {e}")
            return None

    async def update_prompt(self, prompt_type: str, template: str, placeholders: list, description: str):
        update_data = {
            "template": template,
            "placeholders": placeholders,
            "description": description,
            "updated_at": datetime.now(timezone.utc)
        }
        try:
            result = await self.collection.update_one({"type": prompt_type}, {"$set": update_data})
            if result.matched_count == 0:
                logging.warning(f"Prompt not found for update: {prompt_type}")
                return False
            logging.info(f"Prompt updated successfully: {prompt_type}")
            return True
        except PyMongoError as e:
            logging.error(f"Error updating prompt: {e}")
            return False

    async def delete_prompt(self, prompt_uuid: str):
        try:
            result = await self.collection.delete_one({"id": prompt_uuid})
            if result.deleted_count == 0:
                logging.warning(f"Prompt not found for deletion: {prompt_uuid}")
                return False
            logging.info(f"Prompt deleted successfully: {prompt_uuid}")
            return True
        except PyMongoError as e:
            logging.error(f"Error deleting prompt: {e}")
            return False

    async def list_all_prompts(self):
        try:
            prompts = await self.collection.find({}, {"_id": 0}).to_list(length=None)
            logging.info("Fetched all prompts successfully.")
            return prompts
        except PyMongoError as e:
            logging.error(f"Error listing prompts: {e}")
            return []
