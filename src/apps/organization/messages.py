from enum import Enum
from typing import List
from src.fastapi_babel import _


class OrganizationMessageEnum(str, Enum):
    create_new_organization: str = _("Create new organization")
    get_organizations: str = _("Get organizations")
    get_single_organization: str = _("Get single organization")
    update_organization: str = _("Update organization")


class OrganizationErrorMessageEnum(str, Enum):
    organization_not_found: str = _("Organization not found")
    parent_organization_not_found: str = _("Parent organization not found")


class OrganizationNotFoundErrorDetailEnum(list, Enum):
    organization_not_found: List[str] = [
        OrganizationErrorMessageEnum.organization_not_found
    ]
    parent_organization_not_found: List[str] = [
        OrganizationErrorMessageEnum.parent_organization_not_found
    ]
