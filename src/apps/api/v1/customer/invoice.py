import re
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Path,
    Security,
    status,
    Query,
)
from fastapi.responses import Response as StarletteResponse
from persiantools.characters import ar_to_fa

from src.apps.auth.deps import get_current_user
from src.apps.invoice import schema as invoice_schema
from src.apps.invoice.controller import invoice_controller
from src.apps.invoice.messages import InvoiceMessageEnum
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.user.models import User
from src.core.base.schema import (
    PaginatedResponse,
    Response,
)
from src.core.mixins.fields import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

invoice_router = APIRouter()
entity = collections_names.INVOICE


@invoice_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[PaginatedResponse[List[invoice_schema.InvoiceSubListOut]]],
    description="",
)
@return_on_failure
async def get_invoice_list(
    search: Optional[str] = Query(None, alias="search", name="Search"),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {
        "is_deleted": {"$ne": True},
        "customer.user_id": current_user.id,
    }
    if search:
        search = ar_to_fa(search)
        criteria["$or"] = [
            {"invoice_title": re.compile(search, re.IGNORECASE)},
            {"invoice_details.product_name": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await invoice_controller.get_list_objs(
        pagination=pagination, ordering=ordering, criteria=criteria
    )
    return Response[PaginatedResponse[List[invoice_schema.InvoiceSubListOut]]](
        data=result_data, message=InvoiceMessageEnum.get_invoices
    )


@invoice_router.get(
    "/{invoice_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[invoice_schema.InvoiceGetOut],
)
@return_on_failure
async def get_single_invoice(
    invoice_id: SchemaID = Path(...),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "read"],
    ),
):
    criteria = {
        "is_deleted": {"$ne": True},
        "customer.user_id": current_user.id,
    }
    result_data = await invoice_controller.get_single_invoice(
        target_invoice_id=invoice_id, criteria=criteria
    )
    return Response[invoice_schema.InvoiceGetOut](
        data=result_data, message=InvoiceMessageEnum.get_single_invoice
    )


@invoice_router.get(
    "/all",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[invoice_schema.InvoiceGetListOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_invoice_without_pagination(
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    search: Optional[str] = Query(None),
):
    criteria = {
        "is_deleted": {"$ne": True},
        "customer.user_id": current_user.id,
    }
    if search:
        search = ar_to_fa(search)
        criteria["$or"] = [
            {"invoice_title": re.compile(search, re.IGNORECASE)},
            {"invoice_details.product_name": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await invoice_controller.get_list_objs_without_pagination(
        criteria=criteria
    )
    return Response[invoice_schema.InvoiceGetListOut](
        data=invoice_schema.InvoiceGetListOut(result=result_data),
        message=InvoiceMessageEnum.get_invoices,
    )


@invoice_router.patch(
    "/{invoice_id}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[invoice_schema.InvoiceUpdateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_invoice(
    background_tasks: BackgroundTasks,
    payload: invoice_schema.InvoiceUpdateIn,
    invoice_id: SchemaID = Path(...),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    criteria = {
        "_id": invoice_id,
        "is_deleted": {"$ne": True},
        "customer.user_id": current_user.id,
    }
    result_data = await invoice_controller.update_single_obj(
        criteria=criteria,
        new_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=invoice_id,
    )
    return Response[invoice_schema.InvoiceUpdateOut](
        data=result_data, message=InvoiceMessageEnum.update_invoice
    )


@invoice_router.delete(
    "/{invoice_id}/",
    status_code=204,
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_invoice(
    background_tasks: BackgroundTasks,
    invoice_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "delete"]),
):
    criteria = {
        "_id": invoice_id,
        "is_deleted": {"$ne": True},
        "customer.user_id": current_user.id,
    }
    if await invoice_controller.soft_delete_obj(**criteria):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=invoice_id,
        )
        return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)
