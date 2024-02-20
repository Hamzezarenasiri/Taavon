from typing import List, Optional

from beanie import Document
from pydantic import Field

from src.apps.file.constants import FileTypeEnum
from src.core import mixins
from src.core.mixins import DB_ID
from src.core.mixins.fields import SchemaID
from src.main.config import collections_names


class File(mixins.SoftDeleteMixin, mixins.IsEnableMixin, Document):
    alt: Optional[str]
    user_id: DB_ID
    file_url: str
    thumbnail_url: Optional[str]
    file_type: FileTypeEnum
    # file_category: Optional[FileCategoryEnum]
    file_name: str = Field(max_length=100)
    is_used: bool = Field(
        default=False, description="True is file has been used in other documents."
    )
    entity_ids: Optional[List[SchemaID]]

    class Config:
        collection = collections_names.FILE

    class Meta:
        entity_name = "file"
