from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from .messages import StoreErrorMessageEnum, StoreNotFoundErrorDetailEnum

StoreNotFound = CustomHTTPException(
    detail=StoreNotFoundErrorDetailEnum.store_not_found,
    message=StoreErrorMessageEnum.store_not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
