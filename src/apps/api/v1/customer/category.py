from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, Security, status, BackgroundTasks
from starlette.responses import Response as StarletteResponse

from src.apps.auth.deps import get_current_user
from src.apps.category import schema as category_schema
from src.apps.category.controller import category_controller
from src.apps.category.constants import CategoryMessageEnum
from src.apps.log_app.controller import log_controller
from src.apps.log_app.constants import LogActionEnum
from src.apps.user.models import User
from src.core.base.schema import Response, PaginatedResponse, BulkDeleteIn
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

category_router = APIRouter()
entity = collections_names.CATEGORY


@category_router.get(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[
        PaginatedResponse[List[category_schema.CategoryGetListOut]]
    ],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_category(
    _: User = Security(get_current_user, scopes=[entity, "list"]),
    cat_id: Optional[SchemaID] = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
    is_enabled: bool = Query(None),
) -> Response[PaginatedResponse[List[category_schema.CategoryGetListOut]]]:
    criteria = {"is_deleted": {"$ne": True}}
    if cat_id:
        criteria.update(parent=cat_id)
    if is_enabled is not None:
        criteria["is_enabled"] = is_enabled
    result_data = await category_controller.get_all_category_customer(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[category_schema.CategoryGetListOut]]](
        data=result_data.dict(), message=CategoryMessageEnum.get_categories
    )


@category_router.get(
    "/hierarchical",
    responses={**common_responses},
    response_model=Response[List[category_schema.CategoryGetListOut]],
    description="by `hamzezn`",
)
@return_on_failure
async def get_all_category_hierarchical(
    depth: int = Query(2),
    parent: SchemaID = Query(None),
):
    criteria = {"is_enabled": True, "is_deleted": {"$ne": True}, "parent": parent}

    result_data = await category_controller.get_all_category_hierarchical(
        criteria=criteria, depth=depth
    )
    return Response[List[category_schema.CategoryGetListOut]](data=result_data)


@category_router.get(
    "/no-pagination",
    responses={**common_responses},
    response_model=Response[List[category_schema.CategoryGetListOut]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_categories_without_pagination(
    _: User = Security(get_current_user, scopes=[entity, "list"]),
):
    result_data = await category_controller.get_list_objs_without_pagination(
        criteria={"parent": None, "is_deleted": {"$ne": True}}
    )
    return Response[List[category_schema.CategoryGetListOut]](data=result_data)


@category_router.get(
    "/{category_id}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[category_schema.CategoryGetOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_category(
    category_id: SchemaID = Path(...),
    _: User = Security(get_current_user, scopes=[entity, "read"]),
):
    result_data = await category_controller.get_single_category(cat_id=category_id)
    return Response[category_schema.CategoryGetOut](
        data=result_data, message=CategoryMessageEnum.get_single_category
    )
