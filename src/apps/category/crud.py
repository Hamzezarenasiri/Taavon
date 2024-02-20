import re
from typing import List, Optional

from src.apps.category.exception import CategoryNotFound
from src.apps.category.models import (
    Category,
)
from src.core.base.crud import BaseCRUD
from src.core.mixins import DB_ID, SchemaID
from src.main.config import collections_names


class CategoryCRUD(BaseCRUD):
    async def get_categories_pipeline(self, category_id_list: List) -> List:
        return [
            {"$match": {"id": {"$in": category_id_list}}},
        ]

    async def get_joined(
        self,
        criteria: Optional[dict] = None,
        raise_exception=True,
    ):
        if criteria is None:
            criteria = {}
        criteria.update(
            {
                "is_deleted": False,
            }
        )
        results = await self.full_join_aggregate(criteria)
        if not results and raise_exception:
            raise CategoryNotFound
        return results[0]

    async def get_all_joined(
        self,
        criteria: Optional[dict] = None,
    ) -> List[dict]:
        if criteria is None:
            criteria = {}
        return await self.full_join_aggregate(criteria)

    async def full_join_aggregate(self, criteria):
        pipeline = [
            {"$match": criteria},
            {
                "$lookup": {
                    "from": collections_names.CATEGORY,
                    "localField": "parent",
                    "foreignField": "_id",
                    "as": "parent",
                },
            },
            {"$unwind": {"path": "$parent", "preserveNullAndEmptyArrays": True}},
            {
                "$group": {
                    "_id": "$_id",
                    "image": {"$first": "$image"},
                    "id": {"$first": "$id"},
                    "create_datetime": {"$first": "$create_datetime"},
                    "is_enabled": {"$first": "$is_enabled"},
                    "is_deleted": {"$first": "$is_deleted"},
                    "title": {"$first": "$title"},
                    "parent": {"$first": "$parent"},
                    "ancestors": {"$first": "$ancestors"},
                    "attributes": {"$first": "$attributes"},
                },
            },
            {
                "$addFields": {
                    "parent.title": "$parent.title",
                    "id": "$_id",
                }
            },
        ]
        results = await categories_crud.aggregate(pipeline)
        for result in results:
            if not result["parent"]:
                result["parent"] = None
        return results

    async def join_aggregate_without_parent(self, criteria):
        if criteria is None:
            criteria = {}
        pipeline = [
            {"$match": criteria},
            {
                "$group": {
                    "_id": "$_id",
                    "image": {"$first": "$image"},
                    "id": {"$first": "$_id"},
                    "create_datetime": {"$first": "$create_datetime"},
                    "is_enabled": {"$first": "$is_enabled"},
                    "is_deleted": {"$first": "$is_deleted"},
                    "title": {"$first": f"$title"},
                    "parent": {"$first": "$parent"},
                    "ancestors": {"$first": "$ancestors"},
                    "attributes": {"$first": "$attributes"},
                },
            },
        ]
        results = await categories_crud.aggregate(pipeline)
        for result in results:
            if not result["parent"]:
                result["parent"] = None
        return results

    async def get_attributes(
        self,
        target_id: DB_ID = None,
        criteria: Optional[dict] = None,
    ) -> dict:
        if criteria is None:
            criteria = {}
        criteria["is_deleted"] = {"$ne": True}
        if target_id:
            criteria["id"] = target_id
        pipeline = [
            {"$match": criteria},
            {
                "$addFields": {
                    "title": "$title" if target_id else "All",
                    "filterable_attributes": {
                        "$map": {
                            "input": "$attributes",
                            "as": "attr",
                            "in": {
                                "title": "$$attr.title",
                                "attribute_key": "$$attr.attribute_key",
                                "filter_type": "$$attr.filter_type",
                                "values": "$$attr.values",
                                "show_filter": "$$attr.show_filter",
                                "is_mandatory": "$$attr.is_mandatory",
                            },
                        }
                    },
                }
            },
        ]
        results = await categories_crud.aggregate(pipeline)
        if not results:
            raise CategoryNotFound
        return results[0]

    async def get_child(
        self, parent_id: DB_ID, raise_exception=False, **kwargs
    ) -> Category:
        return await categories_crud.get_object(
            criteria={"parent": parent_id},
            raise_exception=raise_exception,
            **kwargs,
        )

    async def update_children_ancestors(
        self,
        target_category: Category,
        ancestors: List[DB_ID],
    ):
        children = await categories_crud.get_list(
            criteria={"parent": target_category.id}
        )
        if children:
            ancestors.append(target_category.id)
            await categories_crud.update_many(
                criteria={"parent": target_category.id},
                update={"ancestors": ancestors},
            )
            for child in children:
                await self.update_children_ancestors(
                    target_category=child, ancestors=ancestors
                )

    # async def get_mandatory_category_attributes(
    #     self, criteria: dict = None
    # ) -> List[SearchAttributes]:
    #     if criteria is None:
    #         criteria = {}
    #     criteria["is_deleted"] = {"$ne": True}
    #     pipeline = [
    #         {"$match": criteria},
    #         {
    #             "$unwind": {
    #                 "path": "$attributes",
    #                 "preserveNullAndEmptyArrays": True,
    #             }
    #         },
    #         {
    #             "$group": {
    #                 "_id": None,
    #                 "attributes": {"$addToSet": "$attributes"},
    #             }
    #         },
    #         {
    #             "$project": {
    #                 "attributes": {
    #                     "$filter": {
    #                         "input": "$attributes",
    #                         "cond": {"$eq": ["$$this.is_mandatory", True]},
    #                     }
    #                 }
    #             }
    #         },
    #     ]
    #     results = (await self.aggregate(pipeline=pipeline))[0]["attributes"]
    #     return [SearchAttributes(**result) for result in results] if results else []

    async def get_category_ids_from_string(
        self,
        cats: str,
        split_by: str = ">",
    ) -> List[SchemaID]:
        categories_name = [c.strip() for c in cats.split(split_by)]
        cat_ids = []
        for category_name in categories_name:
            criteria = {
                "title": re.compile(category_name, re.IGNORECASE),
                "ancestors": cat_ids,
            }
            cat_id = (await self.get_object(criteria=criteria)).id
            cat_ids.append(cat_id)
        return cat_ids


categories_crud = CategoryCRUD(
    read_db_model=Category,
    create_db_model=Category,
    update_db_model=Category,
)
