from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any

from pydantic import Field, validator

from src.apps.product.constants import (
    ProductStateEnum,
    PeriodTypeEnum,
)
from src.apps.category.constants import Category422MessageEnum
from src.apps.category.models import Category
from src.apps.common.constants import ConfirmStatusEnum
from src.apps.organization.constants import Organization422MessageEnum
from src.apps.organization.models import Organization
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID
from src.services import global_services


class PriceSchema(BaseSchema):
    value: Decimal
    is_periodic: None | bool
    period_type: None | PeriodTypeEnum


class CategorySchema(BaseSchema):
    id: SchemaID
    title: str


class StatusHistorySchema(BaseSchema):
    last_state: ProductStateEnum
    current_state: ProductStateEnum
    description: Optional[str]
    change_date: datetime
    changer_id: SchemaID
    # fields: Optional[dict]


class AttributeSchema(BaseSchema):
    field_name: str
    value: Optional[Any]

    class Config:
        smart_union = True


class AttributeCreateSchema(BaseSchema):
    field_name: str
    title: str
    value: int | str | bool

    class Config:
        smart_union = True


class BaseProductSchema(BaseSchema):
    id: SchemaID
    organization_name: str | None
    title: str
    create_datetime: datetime


class ProductListSchema(BaseProductSchema):
    # product_state: ProductStateEnum
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    # product_state: ProductStateEnum
    category: CategorySchema
    picture: Optional[str] = Field(description="first image of product")
    # price:None| PriceSchema
    attributes: None | dict[str, Any]


class ProductDetailSchema(BaseProductSchema):
    # product_state: ProductStateEnum
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    attributes: None | dict[str, Any]
    category: CategorySchema
    description: Optional[str]
    is_enabled: bool
    pictures: Optional[List[str]]
    # price: None | PriceSchema
    # status_history: Optional[List[StatusHistorySchema]]
    confirm_status: ConfirmStatusEnum | None


class CreateProductIn(BaseSchema):
    # product_state: None | ProductStateEnum = Field(ProductStateEnum.DRAFT)
    attributes: dict[str, Any]
    category_id: SchemaID
    description: Optional[str]
    is_enabled: Optional[bool]
    organization_id: None | SchemaID
    # pictures: Optional[List[str]]
    # price: None | PriceSchema
    title: None | str

    # user_id: SchemaID

    @validator("organization_id")
    @classmethod
    def validate_organization_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[Organization.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        else:
            raise ValueError(
                Organization422MessageEnum.Invalid_organization_id_organization_not_found.value
            )

    @validator("category_id")
    @classmethod
    def validate_category_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[Category.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        else:
            raise ValueError(
                Category422MessageEnum.Invalid_category_id__category_not_found.value
            )


class UpdateProductIn(CreateProductIn):
    product_state: Optional[ProductStateEnum] = Field(ProductStateEnum.DRAFT)
    attributes: None | dict[str, Any]
    category_id: Optional[SchemaID]
    description: Optional[str]
    is_enabled: Optional[bool]
    organization_id: Optional[SchemaID]
    pictures: Optional[List[str]]
    # price: None|Optional[PriceSchema]
    title: Optional[str]


class SubActivityProduct(BaseProductSchema):
    pass


class ActivityProduct(BaseSchema):
    product: SubActivityProduct
    meta: dict = Field(alias="action_status")
    create_datetime: datetime
