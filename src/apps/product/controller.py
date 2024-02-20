import json
import re
from datetime import datetime
from typing import List, TypeVar, Any

import phonenumbers
from fastapi import BackgroundTasks
from pydantic import validate_email

from src.apps.product.crud import product_crud
from src.apps.category.models import Attributes as CategoryAttributes
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse, BaseSchema
from src.core.common.exceptions import InvalidQueryParams
from src.core.common.exceptions.common import CustomHTTPException
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.main.config import collections_names
from . import schema as product_schemas
from .constants import ProductStateEnum
from .models import Product
from .models import (
    StatusHistoryModel,
)
from ..category.crud import categories_crud
from ..common.constants import AttributeTypeEnum, ConfirmStatusEnum
from ..organization.crud import organization_crud
from ..user.models import User
from ...core.utils import phone_to_e164_format

SCHEMA = TypeVar("SCHEMA", bound=BaseSchema)


class ProductController(BaseController):
    async def create_product(
        self,
        payload: product_schemas.CreateProductIn,
    ) -> dict:
        category = await categories_crud.get_by_id(_id=payload.category_id)
        organization = await organization_crud.get_by_id(_id=payload.organization_id)
        organization_ids = organization.ancestors + [organization.id]
        attributes = self.validate_attributes(category.attributes, payload.attributes)
        category_ids = category.ancestors + [category.id]
        product = await product_crud.create(
            Product(
                **payload.dict(exclude_none=True, exclude={"address", "attributes"}),
                category_ids=category_ids,
                organization_ids=organization_ids,
                attributes=attributes,
            )
        )
        return await product_crud.get_product_joined(product_id=product.id)

    async def get_products_joined(
        self,
        pagination: Pagination,
        ordering: Ordering,
        schema: SCHEMA,
        criteria: dict = None,
    ) -> PaginatedResponse[List[SCHEMA]]:
        if not criteria:
            criteria = {}
        criteria["is_deleted"] = {"$ne": True}
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
                    "picture": {"$first": "$pictures"},
                    "organization_name": "$organization.name",
                    "category.id": "$category._id",
                    "id": "$_id",
                }
            },
        ]
        return await pagination.paginate(
            crud=self.crud,
            list_item_model=schema,
            pipeline=pipeline,
            _sort=await ordering.get_ordering_criteria(),
        )

    async def update_product(
        self,
        payload: product_schemas.UpdateProductIn,
        product_id: SchemaID,
        current_user: User,
        background_tasks: BackgroundTasks,
    ) -> dict:
        product: Product = await self.crud.get_by_id(_id=product_id)
        new_state = payload.product_state or product.product_state
        updated_data = payload.dict(exclude_none=True)
        category_id = payload.category_id or product.category_id
        category = await categories_crud.get_by_id(_id=category_id)
        if payload.category_id:
            updated_data["category_ids"] = category.ancestors + [category.id]
        if payload.organization_id:
            organization = await organization_crud.get_by_id(
                _id=payload.organization_id
            )
            updated_data["organization_ids"] = organization.ancestors + [
                organization.id
            ]
        if updated_data.get("attributes"):
            attributes = self.validate_attributes(
                category.attributes, payload.attributes
            )
            updated_data["attributes"] = attributes

        product.status_history.append(
            StatusHistoryModel(
                last_state=product.product_state,
                current_state=new_state,
                changer_id=current_user.id,
                fields=updated_data,
            )
        )
        new_doc = product.copy(update=updated_data).dict()
        await self.crud.default_update(criteria={"_id": product.id}, new_doc=new_doc)

        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.update,
            action_by=current_user.id,
            entity=collections_names.PRODUCT,
            entity_id=product_id,
            meta=updated_data,
        )

        return await product_crud.get_product(product_id=product.id)

    def validate_attributes(
        self,
        category_attrs: List[CategoryAttributes],
        product_attrs: dict[str, Any],
    ) -> dict[str, Any]:
        validated_attrs = {}
        for cat_attr in category_attrs:
            product_value = product_attrs.get(cat_attr.field_name)
            if product_value is None and cat_attr.is_mandatory:
                raise CustomHTTPException(
                    status_code=422,
                    message=f"{cat_attr.title} attribute is required",
                    detail=[f"{cat_attr.field_name} attribute is required"],
                )
            validated_value = self._validate_attr_type(cat_attr, product_value)
            validated_attrs[cat_attr.field_name] = validated_value
        return validated_attrs

    def _validate_attr_isinstance(self, instance_type):
        def validate_attr_by_instance_type(value, attribute):
            if not isinstance(value, instance_type):
                raise ValueError(
                    f"{attribute.field_name}: '{value}' is not valid {attribute.attr_type}"
                )
            return value

        return validate_attr_by_instance_type

    def _validate_attr_date(self, value: str, attribute):
        try:
            value = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise CustomHTTPException(
                status_code=422,
                message=f"{attribute.title}: '{value}' is not valid {attribute.attr_type}",
                detail=[
                    f"{attribute.field_name}: '{value}' is not valid {attribute.attr_type} (valid example: 2002-02-02)"
                ],
            )
        return value

    def _validate_attr_datetime(self, value: str, attribute):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            raise CustomHTTPException(
                status_code=422,
                message=f"{attribute.title}: '{value}' is not valid {attribute.attr_type}",
                detail=[
                    f"{attribute.field_name}: '{value}' is not valid {attribute.attr_type} (valid example: 2002-02-02)"
                ],
            )
        return value

    def _validate_attr_phone_number(self, value: str, attribute):
        try:
            if value.startswith("00"):
                value = value.replace("00", "+", 1)
            return phone_to_e164_format(value)
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e

    def _validate_attr_choice(self, value, attribute):
        if not value in attribute.choices:
            raise CustomHTTPException(
                status_code=422,
                message=f"{attribute.title}: '{value}' is not valid {attribute.attr_type}",
                detail=[
                    f"{attribute.field_name}: '{value}' is not valid {attribute.attr_type} , valid choice : {attribute.choices}"
                ],
            )
        return value

    def _validate_attr_email(self, value, attribute):
        self._validate_attr_isinstance(str)(value, attribute)
        validate_email(value)
        return value

    def _validate_attr_national_code(self, value, attribute):
        if not re.search(r"^\d{10}$", value):
            raise ValueError("The national code is invalid, it must be ten digits")

        check = int(value[9])
        s = sum([int(value[x]) * (10 - x) for x in range(9)]) % 11
        if (2 > s == check) or (s >= 2 and (check + s) == 11):
            return value
        else:
            raise ValueError(
                "The national code is invalid, There is no such national code"
            )

    def _validate_attr_type(self, attribute: CategoryAttributes, value: Any):
        validation_dict = {
            AttributeTypeEnum.INT: self._validate_attr_isinstance(int),
            AttributeTypeEnum.STR: self._validate_attr_isinstance(str),
            AttributeTypeEnum.BOOL: self._validate_attr_isinstance(bool),
            AttributeTypeEnum.FLOAT: self._validate_attr_isinstance(float),
            AttributeTypeEnum.DATE: self._validate_attr_date,
            AttributeTypeEnum.DATETIME: self._validate_attr_datetime,
            AttributeTypeEnum.CHOICE: self._validate_attr_choice,
            AttributeTypeEnum.NATIONAL_CODE: self._validate_attr_national_code,
            AttributeTypeEnum.EMAIL: self._validate_attr_email,
            AttributeTypeEnum.PRICE: self._validate_attr_isinstance(int),
            AttributeTypeEnum.PHONE_NUMBER: self._validate_attr_phone_number,
        }
        try:
            result = validation_dict.get(attribute.attr_type)(value, attribute)
        except ValueError as error:
            raise CustomHTTPException(
                status_code=422,
                message=f"{attribute.title}: '{value}' is not valid {attribute.attr_type}",
                detail=[{attribute.field_name: str(error)}],
            )
        return result

    async def validate_attributes_query_params(self, request) -> dict:
        criteria = {}
        query_params = request.query_params
        try:
            for key, value in query_params.items():
                if key.startswith("attributes"):
                    values = json.loads(value)
                    criteria[f'details.{key.strip("]").replace("[", ".")}'] = {
                        "$in": list(set(values))
                        if hasattr(values, "__iter__")
                        else [values]
                    }
            return criteria
        except ValueError as message:
            raise InvalidQueryParams(detail=[message]) from message

    async def bulk_confirm_objs(
        self, obj_ids: List[SchemaID], status: ConfirmStatusEnum, current_user: User
    ):
        for product_id in obj_ids:
            product: Product = await product_crud.get_by_id(product_id)
            updated_data = {
                "confirm_status": status,
                "product_state": ProductStateEnum.ACTIVE
                if status == ConfirmStatusEnum.Confirm
                else ProductStateEnum.REJECTED,
            }
            product.status_history.append(
                StatusHistoryModel(
                    last_state=product.product_state,
                    current_state=ProductStateEnum.ACTIVE
                    if status == ConfirmStatusEnum.Confirm
                    else ProductStateEnum.REJECTED,
                    changer_id=current_user.id,
                    fields=updated_data,
                )
            )
            new_doc = product.copy(update=updated_data).dict()
            await self.crud.default_update(criteria={"_id": product.id}, new_doc=new_doc)

    async def confirm_obj(
        self, obj_id: SchemaID, status: ConfirmStatusEnum, current_user: User
    ):
        product: Product = await product_crud.get_by_id(obj_id)
        updated_data = {
            "confirm_status": status,
            "product_state": ProductStateEnum.ACTIVE
            if status == ConfirmStatusEnum.Confirm
            else ProductStateEnum.REJECTED,
        }
        product.status_history.append(
            StatusHistoryModel(
                last_state=product.product_state,
                current_state=ProductStateEnum.ACTIVE
                if status == ConfirmStatusEnum.Confirm
                else ProductStateEnum.REJECTED,
                changer_id=current_user.id,
                fields=updated_data,
            )
        )
        new_doc = product.copy(update=updated_data).dict()
        await self.crud.default_update(criteria={"_id": product.id}, new_doc=new_doc)
        return await product_crud.get_by_id(obj_id)


product_controller = ProductController(
    crud=product_crud,
)
