from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from . import messages
from .constants import ProductNotFoundErrorDetailEnum

ProductNotFound = CustomHTTPException(
    detail=ProductNotFoundErrorDetailEnum.not_found,
    message=messages.ProductErrorMessageEnum.not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)

InvalidQuantity = CustomHTTPException(
    detail=ProductNotFoundErrorDetailEnum.invalid_quantity,
    message=messages.ProductErrorMessageEnum.invalid_quantity,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)
