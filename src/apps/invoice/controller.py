from typing import Optional

from src.core.base.controller import BaseController
from src.core.common.exceptions import UpdateFailed
from src.core.mixins import SchemaID
from . import schema as invoice_schema
from .crud import invoice_crud
from .models import Invoice
from ..common.constants import ConfirmStatusEnum
from ..user.models import User


class InvoiceController(BaseController):
    async def get_single_invoice(
        self,
        target_invoice_id: SchemaID,
        criteria: Optional[dict] = None,
    ) -> invoice_schema.InvoiceGetOut:
        return await invoice_crud.get_joined(
            target_id=target_invoice_id,
            criteria=criteria,
        )

    async def update_single_invoice(
        self,
        target_id: SchemaID,
        new_invoice_data: invoice_schema.InvoiceUpdateIn,
    ) -> invoice_schema.InvoiceUpdateOut:
        new_invoice_dict = new_invoice_data.dict()
        (
            updated_invoice,
            is_updated,
        ) = await invoice_crud.default_update_and_get(
            criteria={"id": target_id}, new_doc=new_invoice_dict
        )
        if not is_updated:
            raise UpdateFailed
        updated_invoice = await invoice_crud.get_joined(
            target_id=target_id,
            criteria={"id": updated_invoice.id},
        )
        return invoice_schema.InvoiceUpdateOut(**updated_invoice)

    async def create_new_obj(
        self, new_data: invoice_schema.InvoiceCreateIn, **kwargs
    ) -> invoice_schema.InvoiceCreateOut:
        return await self.crud.create(
            self.create_model(**new_data.dict(exclude_none=True), **kwargs)
        )


invoice_controller = InvoiceController(
    crud=invoice_crud,
)
