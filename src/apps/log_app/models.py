from datetime import datetime
from typing import Optional, Union

from beanie import Document
from pydantic import Field, BaseModel

from src.apps.log_app.constants import LogActionEnum
from src.core.mixins import DB_ID
from src.main.config import collections_names


class Log(
    Document,
):
    action: LogActionEnum
    action_by: DB_ID
    entity: str
    entity_id: Optional[Union[DB_ID, str]]
    meta: Optional[dict]
    description: Optional[dict]
    is_enabled: Optional[bool] = True
    is_deleted: Optional[bool] = False
    create_datetime: Optional[datetime] = Field(default_factory=datetime.utcnow)
    update_datetime: Optional[datetime]

    class Config:
        collection = collections_names.LOG

    class Meta:
        entity_name = "log"
