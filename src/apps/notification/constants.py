from enum import Enum


class NotificationType(str, Enum):
    warning: str = "warning"


ALL_NOTIFICATION_TYPE = [i.value for i in NotificationType.__members__.values()]
