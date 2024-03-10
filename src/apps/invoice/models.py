from typing import Optional

from beanie import Document
from pydantic import BaseModel

from src.core import mixins
from src.core.base.field import (
    PhoneStr,
    IranNationalCodeStr,
)
from src.core.mixins import DB_ID
from src.main.config import collections_names


class InvoiceDetailModel(BaseModel):
    product_name: Optional[str]
    price: Optional[int]
    number: Optional[int]
    total: Optional[int]

    class Config:
        arbitrary_types_allowed = True


class InvoiceUserModel(BaseModel):
    user_id: Optional[DB_ID]
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[IranNationalCodeStr]
    mobile_number: Optional[PhoneStr]
    telephone: Optional[PhoneStr]

    class Config:
        arbitrary_types_allowed = True


class InvoiceStoreModel(BaseModel):
    name: str
    store_id: str

    class Config:
        arbitrary_types_allowed = True


class Invoice(
    Document,
    mixins.SoftDeleteMixin,
    mixins.CreateDatetimeMixin,
    mixins.IsEnableMixin,
):
    customer: InvoiceUserModel
    store: InvoiceStoreModel
    invoice_title: str
    total_installments_count: int
    each_installment_amount: int | None
    remaining_installments_count: int | None
    invoice_details: list[InvoiceDetailModel]

    class Config:
        arbitrary_types_allowed = True
        collection = collections_names.INVOICE

    class Meta:
        entity_name = "invoice"
        indexes = []
