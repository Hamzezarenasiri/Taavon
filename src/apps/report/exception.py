from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from . import messages
from .constants import ReportNotFoundErrorDetailEnum

ReportNotFound = CustomHTTPException(
    detail=ReportNotFoundErrorDetailEnum.not_found,
    message=messages.ReportErrorMessageEnum.not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)

InvalidQuantity = CustomHTTPException(
    detail=ReportNotFoundErrorDetailEnum.invalid_quantity,
    message=messages.ReportErrorMessageEnum.invalid_quantity,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)
