from enum import Enum
from typing import List

from src.fastapi_babel import _


class StoreMessageEnum(str, Enum):
    create_new_store: str = _("Create new store")
    get_stores: str = _("Get stores")
    get_single_store: str = _("Get single store")
    update_store: str = _("Update store")


class StoreErrorMessageEnum(str, Enum):
    store_not_found: str = _("Store not found")


class StoreNotFoundErrorDetailEnum(list, Enum):
    store_not_found: List[str] = [StoreErrorMessageEnum.store_not_found]
