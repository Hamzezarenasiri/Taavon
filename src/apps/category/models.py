from datetime import date, datetime
from typing import Any

import pymongo
from beanie import Document
from pydantic import BaseModel, Field, validator

from src.apps.category.constants import SearchAttributeType
from src.apps.common.constants import AttributeTypeEnum
from src.core import mixins
from src.core.mixins import DB_ID, default_id
from src.main.config import collections_names


class Attributes(BaseModel):
    id: DB_ID = Field(default_factory=default_id)
    field_name: str
    title: str
    description: None | str
    attr_type: AttributeTypeEnum
    icon: None | str
    placeholder: None | str
    is_filterable: bool = False
    filter_type: None | SearchAttributeType
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


class Image(BaseModel):
    url: str
    thumbnail_url: str
    alt: str


class Category(
    mixins.CreateDatetimeMixin,
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    Document,
):
    title: str
    icon: None | Image
    parent: None | DB_ID
    ancestors: None | list[DB_ID] = []
    attributes: None | list[Attributes] = []
    meta_data: None | dict[str, dict[str, Any]]

    class Meta:
        collection_name = collections_names.CATEGORY
        entity_name = "category"
        indexes = [
            pymongo.IndexModel("id", name="cat_id", unique=True),
        ]
