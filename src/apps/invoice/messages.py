from enum import Enum
from typing import List

from src.fastapi_babel import _


class InvoiceMessageEnum(str, Enum):
    create_new_invoice: str = _("Create new invoice")
    get_invoices: str = _("Get invoices")
    get_single_invoice: str = _("Get single invoice")
    update_invoice: str = _("Update invoice")


class InvoiceErrorMessageEnum(str, Enum):
    invoice_not_found: str = _("Invoice not found")


class InvoiceNotFoundErrorDetailEnum(list, Enum):
    invoice_not_found: List[str] = [InvoiceErrorMessageEnum.invoice_not_found]
