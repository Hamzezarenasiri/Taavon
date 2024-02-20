from fastapi import status

from src.core.common.enums import (
    Forbidden403DetailEnum,
    Forbidden403MessageEnum,
    Unauthorized401DetailEnum,
    Unauthorized401MessageEnum,
)
from src.core.common.exceptions.base import CustomHTTPException

InvalidTempToken = CustomHTTPException(
    detail=Unauthorized401DetailEnum.invalid_temp_token,
    message=Unauthorized401MessageEnum.invalid_temp_token,
    status_code=status.HTTP_401_UNAUTHORIZED,
)
InvalidTokenProvided = CustomHTTPException(
    detail=Unauthorized401DetailEnum.invalid_token,
    message=Unauthorized401MessageEnum.invalid_token,
    status_code=status.HTTP_401_UNAUTHORIZED,
)
TokenExpired = CustomHTTPException(
    detail=Unauthorized401DetailEnum.access_token_expired,
    message=Unauthorized401MessageEnum.access_token_expired,
    status_code=status.HTTP_401_UNAUTHORIZED,
)
RefreshTokenExpired = CustomHTTPException(
    detail=Unauthorized401DetailEnum.refresh_token_expired,
    message=Unauthorized401MessageEnum.refresh_token_expired,
    status_code=status.HTTP_401_UNAUTHORIZED,
)

AccessDenied = CustomHTTPException(
    detail=Forbidden403DetailEnum.access_denied,
    message=Forbidden403MessageEnum.access_denied,
    status_code=status.HTTP_403_FORBIDDEN,
)
