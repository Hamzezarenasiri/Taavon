from typing import List, Optional

from pydantic import Field

from src.apps.notification.constants import NotificationType
from src.core.base.schema import BaseSchema
from src.core.mixins.fields import SchemaID


class NotificationBaseSchema(BaseSchema):
    title: str
    is_read: bool
    notification_type: Optional[NotificationType]
    text: Optional[str]
    image_url: Optional[str]
    rtl: Optional[bool]
    user_id: Optional[SchemaID]


class NotificationCreateIn(NotificationBaseSchema):
    is_read: Optional[bool] = False


class NotificationCreateOut(NotificationBaseSchema):
    id: SchemaID = Field(alias="_id")


class NotificationSubListOut(NotificationBaseSchema):
    id: SchemaID


class NotificationGetOut(NotificationBaseSchema):
    id: SchemaID = Field(alias="_id")
    is_enabled: bool


class NotificationUpdateIn(BaseSchema):
    is_enabled: Optional[bool]
    title: Optional[str]
    is_read: Optional[bool]
    notification_type: Optional[NotificationType]
    text: Optional[str]
    image_url: Optional[str]
    rtl: Optional[bool]
    user_id: Optional[SchemaID]


class NotificationBulkUpdateIn(NotificationUpdateIn):
    ids: List[SchemaID]


class UserNotificationUpdateIn(BaseSchema):
    is_read: bool = True


class UserNotificationBulkUpdateIn(UserNotificationUpdateIn):
    ids: List[SchemaID]


class NotificationUpdateOut(NotificationBaseSchema):
    id: SchemaID = Field(alias="_id")
    is_enabled: bool


class BulkUpdateOut(BaseSchema):
    is_updated: bool
