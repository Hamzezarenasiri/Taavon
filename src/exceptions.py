from fastapi import status

from src.constants import ErrorDetailEnum, ErrorMessageEnum
from src.core.common.exceptions import CustomHTTPException

AccessDenied = CustomHTTPException(
    detail=ErrorDetailEnum.access_denied,
    message=ErrorMessageEnum.access_denied,
    status_code=status.HTTP_403_FORBIDDEN,
)
