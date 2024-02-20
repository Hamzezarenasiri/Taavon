from src.apps.notification.models import (
    Notification,
)
from src.core.base.crud import BaseCRUD


class NotificationCRUD(BaseCRUD):
    pass


notification_crud = NotificationCRUD(
    read_db_model=Notification,
    create_db_model=Notification,
    update_db_model=Notification,
)
