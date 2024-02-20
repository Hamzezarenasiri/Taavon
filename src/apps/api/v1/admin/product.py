import re
from typing import List

from fastapi import (
    APIRouter,
    responses,
    Security,
    Depends,
    Query,
    Path,
    BackgroundTasks,
    status,
)
from fastapi.responses import Response as StarletteResponse
from persiantools.characters import ar_to_fa

from src.apps.product import schema as product_schemas
from src.apps.product.controller import product_controller
from src.apps.product.crud import product_crud
from src.apps.product.deps import product_filters
from src.apps.auth.deps import get_current_user
from src.apps.common.schema import BulkConfirmIn, ConfirmIn
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.user.models import User
from src.core.base.schema import Response, PaginatedResponse, BulkDeleteIn
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

product_router = APIRouter()
entity = collections_names.PRODUCT


@product_router.post(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[product_schemas.ProductDetailSchema],
    description="by `hamzezn`",
)
@return_on_failure
async def create_product(
    background_tasks: BackgroundTasks,
    payload: product_schemas.CreateProductIn,
    current_user: User = Security(get_current_user, scopes=[entity, "create"]),
):
    product = await product_controller.create_product(payload=payload)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=product["id"],
    )
    return Response[product_schemas.ProductDetailSchema](data=product)


@product_router.get(
    "/{product_id}",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[product_schemas.ProductDetailSchema],
    description="by `hamzezn`",
)
@return_on_failure
async def get_product(
    product_id: SchemaID = Path(...),
    _: User = Security(get_current_user, scopes=[entity, "read"]),
):
    product = await product_crud.get_product_joined(
        product_id=product_id, criteria={"is_deleted": False}
    )
    return Response[product_schemas.ProductDetailSchema](data=product)


@product_router.patch(
    "/{product_id}",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[product_schemas.ProductDetailSchema],
    description="by `hamzezn`",
)
@return_on_failure
async def update_product(
    background_tasks: BackgroundTasks,
    payload: product_schemas.UpdateProductIn,
    product_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "update"]),
):
    product = await product_controller.update_product(
        product_id=product_id,
        payload=payload,
        current_user=current_user,
        background_tasks=background_tasks,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=product["id"],
    )
    return Response[product_schemas.ProductDetailSchema](data=product)


@product_router.patch(
    "/{product_id}/confirm",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[product_schemas.ProductDetailSchema],
    description="by `hamzezn`",
)
@return_on_failure
async def confirm_product(
    background_tasks: BackgroundTasks,
    payload: ConfirmIn,
    product_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "confirm"]),
):
    product = await product_controller.confirm_obj(
        obj_id=product_id,
        status=payload.status,
        current_user=current_user,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.confirm,
        action_by=current_user.id,
        entity=entity,
        entity_id=product["id"],
    )
    return Response[product_schemas.ProductDetailSchema](data=product)


@product_router.delete(
    "/{product_id}",
    responses={
        **common_responses,
        **response_404,
    },
    description="by `hamzezn`",
    status_code=204,
)
@return_on_failure
async def delete_product(
    background_tasks: BackgroundTasks,
    product_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "delete"]),
):
    await product_controller.soft_delete_obj(_id=product_id)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_id=product_id,
    )
    return responses.Response(status_code=204)


@product_router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[product_schemas.ProductListSchema]]],
    description="by `hamzezn`",
)
@return_on_failure
async def get_products(
    current_user: User = Security(get_current_user, scopes=[entity, "list"]),
    filters: dict = Depends(product_filters),
    search: str = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {
        "organization_ids": current_user.organization_id,
        "is_enabled": True,
        **filters,
    }
    if search:
        search = ar_to_fa(search)
        criteria["title"] = re.compile(search, re.IGNORECASE)
    products = await product_controller.get_products_joined(
        pagination=pagination,
        ordering=ordering,
        schema=product_schemas.ProductListSchema,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[product_schemas.ProductListSchema]]](data=products)


@product_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_confirm_products(
    background_tasks: BackgroundTasks,
    payload: BulkConfirmIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "confirm"],
    ),
):
    await product_controller.bulk_confirm_objs(
        obj_ids=payload.ids, status=payload.status, current_user=current_user
    )
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.confirm,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@product_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_products(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    await product_controller.bulk_delete_objs(
        obj_ids=payload.ids,
    )
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)
