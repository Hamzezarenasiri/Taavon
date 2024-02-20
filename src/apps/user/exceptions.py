from fastapi import status

from src.apps.user.constants import (
    UserBadRequestErrorDetailEnum,
    UserBadRequestErrorMessageEnum,
    UserForbiddenErrorDetailEnum,
    UserForbiddenErrorMessageEnum,
    UserNotFoundErrorDetailEnum,
    UserNotFoundErrorMessageEnum,
)
from src.core.common.exceptions import CustomHTTPException

UserNotFound = CustomHTTPException(
    detail=UserNotFoundErrorDetailEnum.not_found,
    message=UserNotFoundErrorMessageEnum.not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
UserIsDisabled = CustomHTTPException(
    detail=UserForbiddenErrorDetailEnum.is_disabled,
    message=UserForbiddenErrorMessageEnum.is_disabled,
    status_code=status.HTTP_403_FORBIDDEN,
)
UserIsBlocked = CustomHTTPException(
    detail=UserForbiddenErrorDetailEnum.is_blocked,
    message=UserForbiddenErrorMessageEnum.is_blocked,
    status_code=status.HTTP_403_FORBIDDEN,
)
UserPhoneNotVerified = CustomHTTPException(
    detail=UserForbiddenErrorDetailEnum.phone_not_verified,
    message=UserForbiddenErrorMessageEnum.phone_not_verified,
    status_code=status.HTTP_403_FORBIDDEN,
)
UserEmailNotVerified = CustomHTTPException(
    detail=UserForbiddenErrorDetailEnum.email_not_verified,
    message=UserForbiddenErrorMessageEnum.email_not_verified,
    status_code=status.HTTP_403_FORBIDDEN,
)
AccessDenied = CustomHTTPException(
    detail=UserForbiddenErrorDetailEnum.access_denied,
    message=UserForbiddenErrorMessageEnum.access_denied,
    status_code=status.HTTP_403_FORBIDDEN,
)
UserIsPending = CustomHTTPException(
    detail=UserForbiddenErrorDetailEnum.is_pending,
    message=UserForbiddenErrorMessageEnum.is_pending,
    status_code=status.HTTP_403_FORBIDDEN,
)
UserIsRejected = CustomHTTPException(
    detail=UserForbiddenErrorDetailEnum.is_rejected,
    message=UserForbiddenErrorMessageEnum.is_rejected,
    status_code=status.HTTP_403_FORBIDDEN,
)
GoogleCodeNotValid = CustomHTTPException(
    detail=UserBadRequestErrorDetailEnum.google_code_not_valid,
    message=UserBadRequestErrorMessageEnum.google_code_not_valid,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
)
