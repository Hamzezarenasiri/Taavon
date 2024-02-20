from enum import Enum
from typing import List
from src.fastapi_babel import _


class ConfigNotFound404MessageEnum(str, Enum):
    config: str = _("Config not found")
    no_docs: str = _("Please insert config record into database")


class ConfigNotFound404DetailEnum(list, Enum):
    config: List[str] = [ConfigNotFound404MessageEnum.config]
    no_docs: List[str] = [ConfigNotFound404MessageEnum.no_docs]


class ConfigTypeAdmin(str, Enum):
    pass


ALL_ADMIN_CONFIG_TYPES = [i.value for i in ConfigTypeAdmin.__members__.values()]
