from typing import TypeVar, Optional, List

from src.core.base.crud import BaseCRUD
from src.core.base.schema import BaseSchema
from .exceptions import StoreNotFound
from .models import Store
from ...core.mixins import DB_ID

T = TypeVar("T", bound=BaseSchema)


class StoreCRUD(BaseCRUD):
    async def get_joined(
        self,
        target_id: DB_ID,
        criteria: Optional[dict] = None,
    ) -> dict:
        if criteria is None:
            criteria = {}
        criteria.update({"_id": target_id})
        result = await self.get_all_joined(criteria)
        if not result:
            raise StoreNotFound
        return result[0]

    async def get_all_joined(
        self,
        criteria: Optional[dict] = None,
    ) -> List[dict]:
        if criteria is None:
            criteria = {}
        return await self.full_join_aggregate(criteria)

    async def full_join_aggregate(self, criteria) -> List[dict]:
        pipeline = [
            {"$match": criteria},
            # {
            #     "$lookup": {
            #         "from": collections_names.USER,
            #         "localField": "owner_id",
            #         "foreignField": "_id",
            #         "as": "owner",
            #     },
            # },
            # {"$unwind": {"path": "$owner", "preserveNullAndEmptyArrays": True}},
            # {
            #     "$group": {
            #         "_id": {"_id": "$id"},
            #     },
            # },
            {"$addFields": {"id": "$_id"}},
        ]
        return await self.aggregate(pipeline=pipeline)


store_crud = StoreCRUD(
    read_db_model=Store,
    create_db_model=Store,
    update_db_model=Store,
)
