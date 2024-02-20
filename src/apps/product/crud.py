from decimal import Decimal

import pymongo

from src.apps.user.models import User
from src.core.base.crud import BaseCRUD
from src.core.mixins.fields import SchemaID
from .constants import ProductStateEnum
from .exception import ProductNotFound
from .models import (
    Product,
)
from ...main.config import collections_names


class ProductCRUD(BaseCRUD):
    async def get_product_joined(
        self,
        product_id: SchemaID,
        criteria: dict = None,
    ) -> dict:
        if not criteria:
            criteria = {}
        criteria["_id"] = product_id
        pipeline = [
            {"$match": criteria},
            {
                "$lookup": {
                    "from": collections_names.CATEGORY,
                    "localField": "category_id",
                    "foreignField": "_id",
                    "as": "category",
                }
            },
            {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": collections_names.ORGANIZATION,
                    "localField": "organization_id",
                    "foreignField": "_id",
                    "as": "organization",
                },
            },
            {"$unwind": {"path": "$organization", "preserveNullAndEmptyArrays": True}},
            {
                "$addFields": {
                    "id": "$_id",
                    "organization_name": "$organization.name",
                    "category.id": "$category._id",
                }
            },
        ]
        product = await self.aggregate(pipeline=pipeline)
        if not product:
            raise ProductNotFound
        return product[0]

    async def get_product(self, product_id: SchemaID) -> dict:
        criteria = {"_id": product_id}
        pipeline = [
            {"$match": criteria},
            {
                "$lookup": {
                    "from": collections_names.CATEGORY,
                    "localField": "category_id",
                    "foreignField": "_id",
                    "as": "category",
                }
            },
            {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": collections_names.ORGANIZATION,
                    "localField": "organization_id",
                    "foreignField": "_id",
                    "as": "organization",
                },
            },
            {"$unwind": {"path": "$organization", "preserveNullAndEmptyArrays": True}},
            {
                "$addFields": {
                    "id": "$_id",
                    "organization_name": "$organization.name",
                    "category.id": "$category._id",
                }
            },
        ]
        product = await self.aggregate(pipeline=pipeline)
        if not product:
            raise ProductNotFound
        return product[0]

    async def get_min_max_price(
        self,
        criteria: dict = None,
    ) -> tuple[Decimal, Decimal]:
        if criteria is None:
            criteria = {}
        criteria |= {
            "is_deleted": False,
            "product_state": ProductStateEnum.DRAFT,
            "is_enabled": True,
        }
        min_obj = await self.get_list(
            criteria=criteria,
            limit=1,
            sort=[("price.value", pymongo.ASCENDING)],
        )
        max_obj = await self.get_list(
            criteria=criteria,
            limit=1,
            sort=[("price.value", pymongo.DESCENDING)],
        )
        if min_obj and max_obj:
            min_price = min_obj[0].price.value
            max_price = max_obj[0].price.value
        else:
            min_price = 0
            max_price = 0
        return min_price, max_price

    async def export_dict_and_keys_join_aggregate(
        self, criteria
    ) -> tuple[list[dict], list | None]:
        pipeline = [
            {"$match": criteria},
            {
                "$lookup": {
                    "from": collections_names.ORGANIZATION,
                    "localField": "organization_id",
                    "foreignField": "_id",
                    "as": "organization",
                },
            },
            {"$unwind": {"path": "$organization", "preserveNullAndEmptyArrays": True}},
            {
                "$addFields": {
                    "organization_name": "$organization.name",
                }
            },
        ]
        entities = await self.aggregate(pipeline=pipeline)
        return entities, None


product_crud = ProductCRUD(
    read_db_model=Product,
    create_db_model=Product,
    update_db_model=Product,
)
