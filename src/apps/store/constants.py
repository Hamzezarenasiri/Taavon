from enum import Enum

from src.fastapi_babel import _


class LegalTypeEnum(str, Enum):
    REAL: str = "real"
    LEGAL: str = "legal"


ALL_LEGAL_TYPE_TYPES = [i.value for i in LegalTypeEnum.__members__.values()]


class Store422MessageEnum(str, Enum):
    Invalid_city_id_city_not_found: str = _("Invalid city_id. City not found")
    Invalid_state_id_state_not_found: str = _("Invalid state_id. State not found")
    Invalid_parent__store_not_found: str = _("Invalid parent. Store not found")
    Invalid_user_id__user_not_found: str = _("Invalid user_id. User not found")
    Invalid_store_id_store_not_found: str = _("Invalid store_id. Store not found")
