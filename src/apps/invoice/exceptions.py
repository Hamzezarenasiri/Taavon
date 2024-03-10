from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from .messages import InvoiceErrorMessageEnum, InvoiceNotFoundErrorDetailEnum

InvoiceNotFound = CustomHTTPException(
    detail=InvoiceNotFoundErrorDetailEnum.invoice_not_found,
    message=InvoiceErrorMessageEnum.invoice_not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
