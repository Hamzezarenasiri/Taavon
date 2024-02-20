from datetime import datetime, date

from pydantic import validator, Field

from src.apps.category.constants import Category422MessageEnum
from src.apps.category.models import Category
from src.apps.common.constants import FilterTypeEnum
from src.apps.report.constants import FilterBoxType
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID
from src.services import global_services


class FilterSchema(BaseSchema):
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


class BaseReportSchema(BaseSchema):
    id: SchemaID
    title: str
    filters: list[FilterSchema]
    create_datetime: datetime


class ReportListSchema(BaseReportSchema):
    pass


class ReportDetailSchema(BaseReportSchema):
    filters: None | list[FilterSchema]
    is_enabled: bool


class CreateReportIn(BaseSchema):
    category_id: SchemaID
    description: str | None
    filters: list[FilterSchema]
    is_enabled: bool | None
    persian_key_title: dict[str, str] | None
    title: str

    @validator("category_id")
    @classmethod
    def validate_category_id(cls, value: SchemaID):
        if not value :
            return value
        if global_services.SYNC_DB[Category.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        else:
            raise ValueError(
                Category422MessageEnum.Invalid_category_id__category_not_found.value
            )


class GenerateReportFileIn(BaseSchema):
    report_filter_id: SchemaID
    filters: dict
