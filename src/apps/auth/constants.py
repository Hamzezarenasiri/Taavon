from enum import Enum
from typing import List
from src.fastapi_babel import _


class AuthOTPTypeEnum(str, Enum):
    sms: str = "sms"
    email: str = "email"


class AuthMessageEnum(str, Enum):
    login_username_password: str = _("Login username password")
    register_user: str = _("Register user")
    otp_request: str = _("Otp request")
    logout_user: str = _("Logout user")
    google_login: str = _("Google login")
    facebook_login: str = _("Facebook login")
    refresh_token: str = _("Refresh token")
    changed_password: str = _("Changed password")
    changed_password_failed: str = _("Changed password failed")
    otp_verify_limited: str = _("Otp verify limited")


class AuthErrorMessageEnum(str, Enum):
    changed_password: str = _("Failed password changed unsuccessful")
    user_exists_email: str = _("User already exists with this email")
    user_exists_phone: str = _("User already exists with this phone")
    social_login_failed: str = _("Social login failed")


class AuthForbidden403MessageEnum(str, Enum):
    time: str = _("Current date is not between user start date and end date")
    block: str = _("The specified user is blocked")
    permission_denied: str = _("Permission denied")
    is_force_login: str = _("You must login again")


class AuthForbidden403DetailEnum(list, Enum):
    time: List[str] = [AuthForbidden403MessageEnum.time]
    block: List[str] = [AuthForbidden403MessageEnum.block]
    permission_denied: List[str] = [AuthForbidden403MessageEnum.permission_denied]
    is_force_login: List[str] = [AuthForbidden403MessageEnum.is_force_login]


class AuthNotFound404MessageEnum(str, Enum):
    user: str = _("User not found")
    otp_expired: str = _("Otp expired or invalid")


class AuthNotFound404DetailEnum(List[str], Enum):
    user: List[str] = [AuthNotFound404MessageEnum.user]
    otp_expired: List[str] = [AuthNotFound404MessageEnum.otp_expired]


class AuthConflict409MessageEnum(str, Enum):
    invalid_password: str = _("Invalid password")


class RoleMessageEnum(str, Enum):
    create_new_role: str = _("Create new role")
    get_roles: str = _("Get roles")
    get_single_role: str = _("Get single role")
    update_role: str = _("Update role")


class RoleErrorMessageEnum(str, Enum):
    roles_have_user: str = _("Roles have user")


class EntityMessageEnum(str, Enum):
    create_new_entity: str = _("Create new entity")
    get_entities: str = _("Get entities")
    get_single_entity: str = _("Get single entity")
    update_entity: str = _("Update entity")
    bulk_update_entities: str = _("Bulk update entities")
