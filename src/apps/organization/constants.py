from enum import Enum
from typing import List
from src.fastapi_babel import _


class OrganizationCategoryEnum(str, Enum):
    government: str = "government"
    private: str = "private"
    semi_state: str = "semi_state"


ALL_ORGANIZATION_CATEGORY_TYPES = [
    i.value for i in OrganizationCategoryEnum.__members__.values()
]


class Organization422MessageEnum(str, Enum):
    recursive: str = _("Can't be recursive (parent)")
    has_child: str = _("Organization has child")
    Invalid_city_id_city_not_found: str = _("Invalid city_id. City not found")
    Invalid_state_id_state_not_found: str = _("Invalid state_id. State not found")
    Invalid_parent__organization_not_found: str = _(
        "Invalid parent. Organization not found"
    )
    Invalid_user_id__user_not_found: str = _("Invalid user_id. User not found")
    Invalid_organization_id_organization_not_found: str = _(
        "Invalid organization_id. Organization not found"
    )


class Organization422DetailEnum(list, Enum):
    recursive: List[str] = [Organization422MessageEnum.recursive]
    has_child: List[str] = [Organization422MessageEnum.has_child]
