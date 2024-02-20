from src.apps.notification.crud import notification_crud
from src.core.base.controller import BaseController


class NotificationController(BaseController):
    pass


notification_controller = NotificationController(
    crud=notification_crud,
)
