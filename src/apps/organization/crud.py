from typing import TypeVar, Optional, List

from src.core.base.crud import BaseCRUD
from src.core.base.schema import BaseSchema
from .exceptions import OrganizationNotFound
from .models import Organization
from ...core.mixins import DB_ID

T = TypeVar("T", bound=BaseSchema)


class OrganizationCRUD(BaseCRUD):
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
            raise OrganizationNotFound
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
            #         "localField": "ceo.id",
            #         "foreignField": "_id",
            #         "as": "ceo",
            #     },
            # },
            # {"$unwind": {"path": "$ceo", "preserveNullAndEmptyArrays": True}},
            # {
            #     "$group": {
            #         "_id": {"_id": "$id"},
            #     },
            # },
            {"$addFields": {"id": "$_id"}},
        ]
        return await self.aggregate(pipeline=pipeline)

    async def get_child(
        self, parent_id: DB_ID, raise_exception=False, **kwargs
    ) -> Organization:
        return await self.get_object(
            criteria={"parent": parent_id},
            raise_exception=raise_exception,
            **kwargs,
        )

    async def update_children_ancestors(
        self,
        organization: Organization,
        ancestors: List[DB_ID],
    ):
        children = await self.get_list(criteria={"parents": organization.id})
        if children:
            ancestors.append(organization.id)
            await self.update_many(
                criteria={"parents": organization.id},
                update={"ancestors": ancestors},
            )
            for child in children:
                await self.update_children_ancestors(
                    organization=child, ancestors=ancestors
                )


organization_crud = OrganizationCRUD(
    read_db_model=Organization,
    create_db_model=Organization,
    update_db_model=Organization,
)
