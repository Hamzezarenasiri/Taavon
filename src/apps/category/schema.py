from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Any

from pydantic import validator, Field

from src.apps.category.constants import Category422MessageEnum
from src.apps.category.models import Category
from src.apps.common.constants import AttributeTypeEnum
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID
from src.services import global_services


class CategoryAttributesBaseSchema(BaseSchema):
    field_name: str
    title: str
    description: Optional[str]
    attr_type: AttributeTypeEnum
    icon: Optional[str]
    is_filterable: bool = False
    placeholder: Optional[str]
    is_mandatory: bool = False
    choices: None | list[int | str] = Field(
        default=None, description="only when attr_type = choice"
    )
    min: None | int | float | date | datetime = 0
    max: None | int | float | date | datetime = 256

    @validator("choices", always=True)
    @classmethod
    def validate_choices(cls, value, values):
        if values.get("attr_type") == AttributeTypeEnum.CHOICE and not value:
            raise ValueError("choices is missing")
        elif values.get("attr_type") != AttributeTypeEnum.CHOICE and value:
            return None
        return value


class CategoryAttributesSchema(CategoryAttributesBaseSchema):
    id: SchemaID


class CategoryAttributesCreateIn(CategoryAttributesBaseSchema):
    pass


class ImageSchema(BaseSchema):
    url: str
    thumbnail_url: str
    alt: str


class ParentSchema(BaseSchema):
    id: SchemaID
    title: str


class CategoryBaseSchema(BaseSchema):
    title: str
    icon: Optional[ImageSchema]
    parent: Optional[SchemaID]
    is_enabled: bool = True


class CategoryCreateIn(CategoryBaseSchema):
    attributes: Optional[List[CategoryAttributesCreateIn]]
    parent: Optional[SchemaID]

    @validator("parent")
    @classmethod
    def validate_parent(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[Category.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        else:
            raise ValueError(
                Category422MessageEnum.Invalid_parent__category_not_found.value
            )


class CategoryCreateOut(CategoryBaseSchema):
    id: SchemaID
    parent: Optional[ParentSchema]
    attributes: Optional[List[CategoryAttributesSchema]]
    create_datetime: Optional[datetime]


class SubCategoryGetListOut(BaseSchema):
    id: SchemaID
    title: Optional[str]
    icon: Optional[ImageSchema]
    sub_categories: Optional[list]
    is_enabled: bool


class CategoryGetListOut(BaseSchema):
    id: SchemaID
    title: str
    icon: Optional[ImageSchema]
    parent: Optional[SchemaID]
    update_datetime: Optional[datetime]
    sub_categories: Optional[List[SubCategoryGetListOut]]
    attributes: Optional[List[CategoryAttributesSchema]]
    is_enabled: bool
    update_datetime: Optional[datetime]


class CategoryGetOut(CategoryBaseSchema):
    attributes: Optional[List[CategoryAttributesSchema]]
    create_datetime: datetime
    id: SchemaID
    is_enabled: bool
    max_price: Optional[Decimal]
    parent: Optional[ParentSchema]
    update_datetime: Optional[datetime]


class CategoryUpdateIn(CategoryCreateIn):
    title: Optional[str]
    parent: Optional[SchemaID]
    attributes: Optional[List[CategoryAttributesCreateIn]]
    icon: Optional[ImageSchema]
    is_enabled: Optional[bool]


class CategoryUpdateOut(CategoryBaseSchema):
    id: SchemaID
    attributes: Optional[List[CategoryAttributesSchema]]
    is_enabled: Optional[bool]
    create_datetime: datetime
    update_datetime: Optional[datetime]


class SubProductCategoryOut(CategoryCreateOut):
    pass


class CatrgorySearchAttributesOut(CategoryCreateOut):
    pass


class CategoryAttributesGetOut(BaseSchema):
    id: SchemaID
    title: Optional[str]
    filterable_attributes: Optional[List[CatrgorySearchAttributesOut]]
    is_basket_limited: Optional[bool]
    is_enabled: bool
