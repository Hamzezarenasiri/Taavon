from typing import List, Optional

from src.apps.product.constants import ProductStateEnum
from src.apps.product.crud import product_crud
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse
from src.core.common.exceptions import UpdateFailed, DeleteFailed
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.main.config import collections_names
from . import schema as category_schema
from .constants import SearchAttributeType
from .crud import categories_crud
from .exception import (
    CannotRecursiveCategory,
    CategoryHasChild,
    CategoryHasProduct,
    CategoriesHaveChild,
    CategoriesHaveProduct,
)
from .models import Category


class CategoryController(BaseController):
    async def create_new_category(
        self,
        new_category_data: category_schema.CategoryCreateIn,
    ) -> category_schema.CategoryCreateOut:
        ancestors = []
        if new_category_data.parent:
            parent = await categories_crud.get_by_id(_id=new_category_data.parent)
            ancestors = parent.ancestors
            ancestors.append(new_category_data.parent)
        created = await categories_crud.create(
            Category(**new_category_data.dict(exclude_none=True), ancestors=ancestors)
        )
        result = await self.get_single_category(cat_id=created.id)
        return category_schema.CategoryCreateOut(**result.dict())

    async def get_all_category_admin(
        self,
        pagination: Pagination,
        ordering: Ordering,
        criteria: dict = None,
    ) -> PaginatedResponse[List[category_schema.CategoryGetListOut]]:
        if criteria is None:
            criteria = {}
        criteria["is_deleted"] = {"$ne": True}
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
                "$addFields": {
                    "title": "$title",
                    "parent": "$parent.title",
                    "id": "$_id",
                }
            },
        ]
        return await pagination.paginate(
            crud=categories_crud,
            list_item_model=category_schema.CategoryGetListOut,
            pipeline=pipeline,
            _sort=await ordering.get_ordering_criteria(),
        )

    async def get_all_category_hierarchical(
        self,
        criteria: dict = None,
        depth: Optional[int] = 0,
    ) -> List[category_schema.CategoryGetListOut]:
        results = await categories_crud.join_aggregate_without_parent(criteria)
        for i, result in enumerate(results):
            if depth and await categories_crud.get_child(result.get("id")):
                sub_cats = await self.get_all_category_hierarchical(
                    criteria={"parent": result.get("id")}, depth=depth - 1
                )
                results[i]["sub_categories"] = sub_cats

        return results

    async def get_single_category(
        self,
        cat_id: SchemaID,
    ) -> category_schema.CategoryGetOut:
        target_category = await categories_crud.get_joined(
            criteria=dict(_id=cat_id),
        )
        return category_schema.CategoryGetOut(**target_category)

    async def get_category_attributes(
        self,
        target_id: SchemaID,
        criteria: dict = None,
    ) -> category_schema.CategoryAttributesGetOut:
        result = await categories_crud.get_attributes(
            target_id=target_id,
            criteria=criteria,
        )
        products_criteria = {
            "is_enabled": True,
            "is_deleted": {"$ne": True},
            # "product_status": ProductStateEnum.DRAFT,
        }
        if target_id:
            products_criteria["category_ids"] = target_id
        price_values = await product_crud.get_price_min_max(criteria=products_criteria)

        price_attr = category_schema.CatrgorySearchAttributesOut(
            attribute_key="price",
            filter_type=SearchAttributeType.range,
            values=price_values,
            title="Price",
            show_filter=True,
        )
        tags_values = await product_crud.get_distinct_tags_list(
            criteria=products_criteria,
        )
        tags_attr = category_schema.CatrgorySearchAttributesOut(
            attribute_key="tags",
            filter_type=SearchAttributeType.multi_checkbox,
            values=tags_values,
            title="Variety",
            is_mandatory=False,
            show_filter=True,
        )
        # flavor_values = await products_crud.get_distinct_field_list(
        #     field="flavor",
        #     criteria=products_criteria,
        # )
        # flavor_attr = category_schema.CatrgorySearchAttributesOut(
        #     attribute_key="flavor",
        #     filter_type=SearchAttributeType.multi_checkbox,
        #     values=flavor_values,
        #     title="Flavors",
        #     is_mandatory=False,
        #     show_filter=True,
        # )
        personalize_values = await product_crud.get_distinct_field_list(
            field="personalization",
            criteria=products_criteria,
        )
        personalize_attr = category_schema.CatrgorySearchAttributesOut(
            filter_type=SearchAttributeType.multi_checkbox,
            values=personalize_values,
            title="Type of Personalization",
            show_filter=True,
        )
        # brand_attr = category_schema.CatrgorySearchAttributesOut(
        #     attribute_key="brand",
        #     filter_type=SearchAttributeType.multi_checkbox,
        #     values=brand_values,
        #     title="ماركة",
        #     is_mandatory=True,
        #     show_filter=True,
        # )
        # if flavor_values:
        #     result["filterable_attributes"] += [flavor_attr.dict()]
        if tags_values:
            result["filterable_attributes"] += [tags_attr.dict()]
        if personalize_values:
            result["filterable_attributes"] += [personalize_attr.dict()]
        if price_values and price_values[0] != price_values[-1]:
            result["filterable_attributes"] += [price_attr.dict()]
        return category_schema.CategoryAttributesGetOut(**result)

    @staticmethod
    async def update_single_category(
        target_id: SchemaID,
        new_category_data: category_schema.CategoryUpdateIn,
    ) -> category_schema.CategoryUpdateOut:
        target_category = await categories_crud.get_by_id(
            _id=target_id,
        )
        new_category_dict = new_category_data.dict()
        ancestors = []
        if new_category_data.parent:
            parent = await categories_crud.get_by_id(_id=new_category_data.parent)
            ancestors = parent.ancestors
            if new_category_data.parent == target_id or target_id in ancestors:
                raise CannotRecursiveCategory
            ancestors.append(new_category_data.parent)
            new_category_dict.update(ancestors=ancestors)
        (updated_category, is_updated) = await categories_crud.default_update_and_get(
            criteria=dict(id=target_id), new_doc=new_category_dict
        )
        if not is_updated:
            raise UpdateFailed
        if updated_category.parent != target_category.parent:
            categories_crud.update_children_ancestors(target_category, ancestors)
        updated_category = await categories_crud.get_joined(
            criteria=dict(id=updated_category.id),
        )
        return category_schema.CategoryUpdateOut(**updated_category)

    @staticmethod
    async def soft_delete_single_category(
        target_category_id: SchemaID,
    ) -> bool:
        sub_categories = await categories_crud.get_child(target_category_id)
        if sub_categories:
            raise CategoryHasChild(data={"sub_categories": sub_categories})
        products = await product_crud.get_list({"category_ids": target_category_id})
        if products:
            raise CategoryHasProduct(
                data={
                    "products": [
                        {
                            "id": product.id,
                            "title": product.title,
                        }
                        for product in products
                    ]
                }
            )
        target_category = await categories_crud.get_by_id(_id=target_category_id)
        is_deleted = await categories_crud.soft_delete_by_id(
            _id=target_category_id,
        )
        if target_category and is_deleted:
            return is_deleted
        else:
            raise DeleteFailed

    async def bulk_delete_categories(
        self,
        obj_ids: List[SchemaID],
    ) -> List[Category]:
        sub_categories_ids = await categories_crud.get_ids({"parent": {"$in": obj_ids}})
        categories_have_product_ids_ = await product_crud.get_list_of_a_field_values(
            target_field="category_ids", criteria={"category_ids": {"$in": obj_ids}}
        )
        if categories_have_product_ids_:
            categories_have_product_ids = {
                val for sublist in categories_have_product_ids_ for val in sublist
            }
        else:
            categories_have_product_ids = set()
        updated_categories = await categories_crud.bulk_soft_delete(
            obj_ids=list(
                set(obj_ids)
                .difference(sub_categories_ids)
                .difference(categories_have_product_ids)
            )
        )
        if sub_categories_ids:
            raise CategoriesHaveChild(data={"categories_child": sub_categories_ids})

        if categories_have_product_ids:
            raise CategoriesHaveProduct(
                data={
                    "categories_have_product": categories_have_product_ids.intersection(
                        obj_ids
                    )
                }
            )

        return updated_categories


category_controller = CategoryController(
    crud=categories_crud,
)
