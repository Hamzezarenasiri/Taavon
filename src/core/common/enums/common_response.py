from enum import Enum
from typing import List

from src.fastapi_babel import _


class ServerError500MessageEnum(str, Enum):
    server_error: str = _("Internal server error try again later")


class ServerError500DetailEnum(List[str], Enum):
    server_error: List[str] = [ServerError500MessageEnum.server_error]


class BadRequest400MessageEnum(str, Enum):
    delete_failed: str = _("Delete failed")
    update_failed: str = _("Update failed")


class BadRequest400DetailEnum(List[str], Enum):
    delete_failed: List[str] = [BadRequest400MessageEnum.delete_failed]
    update_failed: List[str] = [BadRequest400MessageEnum.update_failed]


class Unauthorized401MessageEnum(str, Enum):
    limited_token: str = _("Limited token")
    invalid_token: str = _("Your session has expired please login again")
    invalid_temp_token: str = _("Invalid temp token please login again")
    access_token_expired: str = _("Access token expired")
    refresh_token_expired: str = _("Refresh token expired")


class Unauthorized401DetailEnum(List[str], Enum):
    limited_token: List[str] = [Unauthorized401MessageEnum.limited_token]
    invalid_token: List[str] = [Unauthorized401MessageEnum.invalid_token]
    invalid_temp_token: List[str] = [Unauthorized401MessageEnum.invalid_temp_token]
    access_token_expired: List[str] = [Unauthorized401MessageEnum.access_token_expired]
    refresh_token_expired: List[str] = [
        Unauthorized401MessageEnum.refresh_token_expired
    ]


class Forbidden403MessageEnum(str, Enum):
    detail: str = _("Forbidden action.")
    user_not_allowed: str = _("User is not allowed to perform this action.")
    access_denied: str = _("Access denied")


class Forbidden403DetailEnum(List[str], Enum):
    detail: List[str] = [Forbidden403MessageEnum.detail]
    user_not_allowed: List[str] = [Forbidden403MessageEnum.user_not_allowed]
    access_denied: List[str] = [Forbidden403MessageEnum.access_denied]


class NotFound404MessageEnum(str, Enum):
    not_found: str = _("Not found")
    detail: str = _("Not found")
    user: str = _("User not found")


class Conflict409MessageEnum(str, Enum):
    detail: str = _("Duplicated entry")


class FileSizeTooLarge413MessageEnum(str, Enum):
    file: str = _("File size is too large")


class UpdatePass422MessageEnum(str, Enum):
    old_password_not_match: str = _("Old password not match")


class UpdatePass422DetailEnum(List[str], Enum):
    old_password_not_match: List[str] = [
        UpdatePass422MessageEnum.old_password_not_match
    ]


class NotFound404DetailEnum(List[str], Enum):
    not_found: List[str] = ["Not Found"]


class QueryParams422MessageEnum(str, Enum):
    invalid_query_params: str = "Invalid query params"


class QueryParams422DetailEnum(List[str], Enum):
    invalid_query_params: List[str] = [QueryParams422MessageEnum.invalid_query_params]
