from datetime import date, datetime
from typing import Optional

import pymongo
from beanie import Document
from pydantic import BaseModel, Field, validator

from src.apps.common.constants import FilterTypeEnum
from src.apps.report.constants import FilterBoxType
from src.core import mixins
from src.core.mixins import DB_ID
from src.main.config import collections_names


class Filter(BaseModel):
    field_name: str
    title: str
    description: None | str
    attr_type: FilterTypeEnum
    api_search_url: None | str
    icon: None | str
    placeholder: None | str
    filter_type: None | FilterBoxType
    is_mandatory: bool = False
    choices: None | list[int | str] = Field(
        default=None, description="only when attr_type = choice"
    )
    min: None | int | float | date | datetime = 0
    max: None | int | float | date | datetime = 256

    @validator("choices", always=True)
    @classmethod
    def validate_choices(cls, value, values):
        if values.get("attr_type") == FilterTypeEnum.CHOICE and not value:
            raise ValueError("choices is missing")
        elif values.get("attr_type") != FilterTypeEnum.CHOICE and value:
            return None
        return value


class Report(
    Document,
    mixins.IsEnableMixin,
    mixins.SoftDeleteMixin,
    mixins.CreateDatetimeMixin,
):
    title: str
    filters: list[Filter]
    category_id: DB_ID
    description: Optional[str]
    persian_key_title: dict[str, str] | None

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    class Meta:
        collection_name = collections_names.REPORT
        entity_name = "report"
        indexes = [pymongo.IndexModel("id", name="id", unique=True)]
