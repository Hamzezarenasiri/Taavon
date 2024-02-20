from typing import Optional

from beanie import Document

from src.apps.notification.constants import NotificationType
from src.core import mixins
from src.core.mixins import DB_ID
from src.main.config import collections_names


class Notification(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    Document,
):
    title: str
    is_read: bool
    notification_type: Optional[NotificationType]
    text: Optional[str]
    image_url: Optional[str]
    rtl: Optional[bool]
    user_id: Optional[DB_ID]

    class Config:
        collection = collections_names.NOTIFICATION

    class Meta:
        entity_name = "notification"
