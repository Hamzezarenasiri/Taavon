from datetime import datetime
from typing import List, Optional

from pydantic import Field, validator

from src.core.base.field import PhoneStr, IranNationalCodeStr
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID
from src.services import global_services
from .constants import Invoice422MessageEnum
from ..store.models import Store
from ..user.models import User


class InvoiceDetailSchema(BaseSchema):
    product_name: Optional[str]
    price: Optional[int]
    number: Optional[int]
    total: Optional[int]


class InvoiceUserSchema(BaseSchema):
    user_id: Optional[SchemaID]
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[IranNationalCodeStr]
    mobile_number: Optional[PhoneStr]
    telephone: Optional[PhoneStr]


class InvoiceStoreSchema(BaseSchema):
    name: str
    store_id: str


class InvoiceBaseSchema(BaseSchema):
    invoice_title: str
    total_installments_count: int
    each_installment_amount: int | None
    remaining_installments_count: int | None
    invoice_details: list[InvoiceDetailSchema]


class InvoiceCreateIn(InvoiceBaseSchema):
    customer_id: SchemaID
    store_id: SchemaID
    is_enabled: Optional[bool]

    @validator("customer_id")
    @classmethod
    def validate_user_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[User.get_collection_name()].find_one({"_id": value}):
            return value
        raise ValueError(Invoice422MessageEnum.Invalid_user_id__user_not_found.value)

    @validator("store_id")
    @classmethod
    def validate_store_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[Store.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        raise ValueError(Invoice422MessageEnum.Invalid_store_id__store_not_found.value)


class InvoiceCreateOut(InvoiceBaseSchema):
    id: SchemaID
    customer: InvoiceUserSchema
    store: InvoiceStoreSchema
    is_enabled: Optional[bool]
    create_datetime: datetime


class InvoiceSubListOut(InvoiceBaseSchema):
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    create_datetime: datetime
    id: SchemaID
    is_enabled: Optional[bool]
    customer: InvoiceUserSchema
    store: InvoiceStoreSchema


class InvoiceGetOut(InvoiceBaseSchema):
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    create_datetime: datetime
    id: SchemaID
    is_enabled: bool
    customer: InvoiceUserSchema
    store: InvoiceStoreSchema


class InvoiceUpdateIn(InvoiceCreateIn):
    customer_id: SchemaID | None
    store_id: SchemaID | None
    invoice_title: str | None
    total_installments_count: int | None
    invoice_details: list[InvoiceDetailSchema] | None


class InvoiceBulkUpdateIn(InvoiceUpdateIn):
    ids: List[SchemaID]


class InvoiceBulkDeleteIn(BaseSchema):
    ids: List[SchemaID]


class InvoiceUpdateOut(InvoiceBaseSchema):
    id: SchemaID = Field(alias="_id")
    customer: InvoiceUserSchema
    store: InvoiceStoreSchema
    is_enabled: bool


class BulkUpdateOut(BaseSchema):
    is_updated: bool


class InvoiceGetListOut(BaseSchema):
    result: List[InvoiceSubListOut]
