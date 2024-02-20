from datetime import datetime
from typing import Optional

from pydantic import Field

from src.apps.log_app.constants import LogActionEnum
from src.apps.user.models import User
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID


class LogBaseSchema(BaseSchema):
    action: LogActionEnum
    action_by: SchemaID
    entity: str
    entity_id: Optional[SchemaID]
    meta: dict
    description: Optional[str]


class LogGetListSchema(LogBaseSchema):
    id: SchemaID
    action_by: User
    meta: Optional[dict]
    entity: str
    is_enabled: bool
    create_datetime: datetime


class LogGetOut(LogBaseSchema):
    id: SchemaID = Field(alias="_id")
    action_by: User
    meta: Optional[dict]
    entity_obj: Optional[dict]
    is_enabled: bool
    create_datetime: datetime
