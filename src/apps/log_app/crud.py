from datetime import datetime
from typing import List, Optional

from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.models import Log
from src.core.base.crud import BaseCRUD
from src.core.mixins.fields import DB_ID
from src.main.config import collections_names


class LogCRUD(BaseCRUD):
    async def get_single_log(
        self,
        schema,
        criteria: Optional[dict] = None,
        language: Optional[str] = None,
    ):
        entity = (await self.get_object(criteria=criteria)).entity
        pipeline = [
            {"$match": criteria},
            {
                "$lookup": {
                    "from": collections_names.USER,
                    "as": "action_by",
                    "localField": "action_by",
                    "foreignField": "_id",
                }
            },
            {"$unwind": {"path": "$action_by", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": entity,
                    "as": "entity_obj",
                    "localField": "entity_id",
                    "foreignField": "_id",
                }
            },
            {"$unwind": {"path": "$entity_obj", "preserveNullAndEmptyArrays": True}},
            {
                "$addFields": {
                    "description": f"$description.{language}"
                    if language
                    else "$description"
                }
            },
            {"$project": {"entity_obj._id": 0}},
        ]
        return (await self.aggregate_schema(pipeline=pipeline, schema=schema))[0]

    async def get_logs_pipeline(
        self,
        action: List[LogActionEnum],
        language: Optional[str] = None,
        criteria: Optional[dict] = None,
        action_by: Optional[DB_ID] = None,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
    ):
        if criteria is None:
            criteria = {}
        if action:
            criteria.update({"action": {"$in": action}})
        if action_by:
            criteria.update({"action_by": action_by})
        if from_datetime:
            criteria.update({"create_datetime": {"$gt": from_datetime}})
        if to_datetime:
            criteria.update({"create_datetime": {"$lt": to_datetime}})
        return [
            {"$match": criteria},
            {
                "$lookup": {
                    "from": collections_names.USER,
                    "as": "action_by",
                    "localField": "action_by",
                    "foreignField": "_id",
                }
            },
            {"$unwind": {"path": "$action_by", "preserveNullAndEmptyArrays": True}},
            {
                "$addFields": {
                    "description": f"$description.{language}"
                    if language
                    else "$description"
                }
            },
        ]


logs_crud = LogCRUD(
    read_db_model=Log,
    create_db_model=Log,
    update_db_model=Log,
)
