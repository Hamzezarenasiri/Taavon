from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic.fields import Field

from src.apps.file.constants import FileTypeEnum
from src.core.base.schema import BaseSchema
from src.core.mixins import ErrorMessage
from src.core.mixins.fields import SchemaID


class DeleteFileErrorMessage(ErrorMessage):
    detail: str = (
        "Faild - Unfortunately there is a problem with removing your file,"
        " Please try again later!"
    )


class FileOut(BaseSchema):
    id: Optional[SchemaID]
    file_url: Optional[str]
    file_name: Optional[str]


class DeletedFileResponse(BaseSchema):
    data: str


@dataclass
class ValidatedFile:
    content: bytes
    file_name: str
    content_type: str


class FileBaseSchema(BaseSchema):
    alt: Optional[str]
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    file_type: FileTypeEnum
    file_name: str = Field(max_length=100)
    is_used: bool = Field(
        default=False, description="True is file has been used in other documents."
    )
    entity_ids: Optional[List[SchemaID]]


class FileCreateIn(FileBaseSchema):
    alt: Optional[str]
    # file_category: Optional[FileCategoryEnum]


class FileUploadDataIn(BaseSchema):
    alt: Optional[str]
    # file_category: Optional[FileCategoryEnum]


class FileCreateOut(FileBaseSchema):
    id: SchemaID
    user_id: SchemaID
    # create_datetime: datetime
    # file_category: Optional[FileCategoryEnum]


class FileUpdateOut(FileBaseSchema):
    id: SchemaID
    user_id: SchemaID
    # create_datetime: datetime
    # update_datetime: Optional[datetime]
    # file_category: Optional[FileCategoryEnum]


class FileUpdateIn(BaseSchema):
    alt: str
    # file_category: Optional[FileCategoryEnum]


class FileGetListOut(FileBaseSchema):
    id: SchemaID
    user_id: SchemaID
    # create_datetime: datetime
    # update_datetime: Optional[datetime]
    # file_category: Optional[FileCategoryEnum]


class FileGetOut(BaseSchema):
    id: SchemaID
    alt: Optional[str]
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    file_type: FileTypeEnum
    file_name: str = Field(max_length=100)


class SubImageOut(BaseSchema):
    id: Optional[SchemaID]
    thumbnail_url: Optional[str]
    alt: Optional[str]
    file_type: Optional[str]
