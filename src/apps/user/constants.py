from enum import Enum
from typing import List

from src.fastapi_babel import _


class UserNotFoundErrorMessageEnum(str, Enum):
    not_found: str = _("User not found")
    not_found_or_disabled: str = _("User not found or disabled")


class UserNotFoundErrorDetailEnum(List[str], Enum):
    not_found: List[str] = [UserNotFoundErrorMessageEnum.not_found]


class UserForbiddenErrorMessageEnum(str, Enum):
    is_blocked: str = _("Your account is blocked. Please contact administrator")
    is_pending: str = _("Your account status is pending. Please contact administrator")
    is_rejected: str = _(
        "Your account status is rejected. Please contact administrator"
    )
    is_disabled: str = _("Your account is disabled. Please contact administrator")
    access_denied: str = _("Can't perform this action")
    phone_not_verified: str = _("Phone not verified")
    email_not_verified: str = _("Email not verified")


class User422MessageEnum(str, Enum):
    Invalid_organization_id_organization_not_found: str = _(
        "Invalid organization_id. Organization not found"
    )
    Invalid_user_id__user_not_found: str = _("Invalid user_id. User not found")


class UserForbiddenErrorDetailEnum(List[str], Enum):
    is_disabled: List[str] = [UserForbiddenErrorMessageEnum.is_disabled]
    is_blocked: List[str] = [UserForbiddenErrorMessageEnum.is_blocked]
    is_pending: List[str] = [UserForbiddenErrorMessageEnum.is_pending]
    is_rejected: List[str] = [UserForbiddenErrorMessageEnum.is_rejected]
    access_denied: List[str] = [UserForbiddenErrorMessageEnum.access_denied]
    phone_not_verified: List[str] = [UserForbiddenErrorMessageEnum.phone_not_verified]
    email_not_verified: List[str] = [UserForbiddenErrorMessageEnum.email_not_verified]


class UserMessageEnum(str, Enum):
    changed_password: str = _("Success password changed successfully")
    register_new_user_and_sent_otp: str = _("Register new user and sent otp")


class UserBadRequestErrorMessageEnum(str, Enum):
    addresses: str = _("Address ids not found")
    google_code_not_valid: str = _("Google code not valid")


class UserBadRequestErrorDetailEnum(List[str], Enum):
    addresses: List[str] = ["One or more Address IDs not found"]
    google_code_not_valid: List[str] = ["Google code not valid"]


class LoginType(str, Enum):
    DIRECT: str = "direct"
    SOCIAL: str = "social"


ALL_LOGIN_TYPES = [i.value for i in LoginType.__members__.values()]


class UserStatus(str, Enum):
    PENDING: str = "pending"
    JUST_ADDED: str = "just_added"
    CONFIRMED: str = "confirmed"
    REJECTED: str = "rejected"


ALL_USER_STATUSES = [i.value for i in UserStatus.__members__.values()]


class UserType(str, Enum):
    VENDOR: str = "vendor"
    CUSTOMER: str = "customer"


ALL_USER_TYPES = [i.value for i in UserType.__members__.values()]


class GenderEnum(str, Enum):
    FEMALE: str = "female"
    MALE: str = "male"
    OTHER: str = "other"


ALL_GENDERS = [i.value for i in GenderEnum.__members__.values()]


class AddressType(str, Enum):
    WORK: str = "work"
    HOME: str = "home"


ALL_Address_Types = [i.value for i in AddressType.__members__.values()]


class DefaultRoleNameEnum(str, Enum):
    SUPER_ADMIN: str = "super_admin"
    ADMIN: str = "admin"
    VENDOR: str = "vendor"
    CUSTOMER: str = "customer"


ALL_ROLE_NAMES = [i.value for i in DefaultRoleNameEnum.__members__.values()]


class DeviceType(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    OTHER = "web"


class DeviceMessageEnum(str, Enum):
    ADD_NEW_DEVICE: str = _("Add new device")
