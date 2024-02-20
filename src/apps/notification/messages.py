from enum import Enum
from src.fastapi_babel import _


class NotificationMessageEnum(str, Enum):
    create_new_notification: str = _("Create new notification")
    get_notifications: str = _("Get notifications")
    get_single_notification: str = _("Get single notification")
    update_notification: str = _("Update notification")


class NotificationErrorMessageEnum(str, Enum):
    notification_not_found: str = _("Notification not found")
