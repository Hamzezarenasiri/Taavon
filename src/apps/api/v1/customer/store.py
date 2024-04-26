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

from src.apps.user.crud import users_crud
from src.apps.auth.deps import get_current_user
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.store import schema as store_schema
from src.apps.store.controller import store_controller
from src.apps.store.messages import StoreMessageEnum
from src.apps.user.models import User
from src.core.base.schema import (
    BulkDeleteIn,
    PaginatedResponse,
    Response,
)
from src.core.mixins.fields import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

store_router = APIRouter()
entity = collections_names.STORE


@store_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[PaginatedResponse[List[store_schema.StoreSubListOut]]],
    description="",
)
@return_on_failure
async def get_store_list(
    search: Optional[str] = Query(None, alias="search", name="Search"),
    _: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {
        # "_id": current_user.store_id,
    }
    if search:
        search = ar_to_fa(search)
        criteria["$or"] = [
            {"name": re.compile(search, re.IGNORECASE)},
            {"text": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await store_controller.get_list_objs(
        pagination=pagination, ordering=ordering, criteria=criteria
    )
    return Response[PaginatedResponse[List[store_schema.StoreSubListOut]]](
        data=result_data, message=StoreMessageEnum.get_stores
    )


@store_router.get(
    "/{store_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[store_schema.StoreGetOut],
)
@return_on_failure
async def get_single_store(
    store_id: SchemaID = Path(...),
    _: User = Security(
        get_current_user,
        scopes=[entity, "read"],
    ),
):
    result_data = await store_controller.get_single_store(
        target_store_id=store_id,
    )
    return Response[store_schema.StoreGetOut](
        data=result_data, message=StoreMessageEnum.get_single_store
    )


@store_router.get(
    "/all",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[store_schema.StoreGetListOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_store_without_pagination(
    _: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    search: Optional[str] = Query(None),
):
    criteria = {
        # "$or": [
        #     {"_id": current_user.store_id},
        # ]
    }
    if search:
        search = ar_to_fa(search)
        criteria["$or"] = [
            {"name": re.compile(search, re.IGNORECASE)},
            {"text": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await store_controller.get_list_objs_without_pagination(
        criteria=criteria
    )
    return Response[store_schema.StoreGetListOut](
        data=store_schema.StoreGetListOut(result=result_data),
        message=StoreMessageEnum.get_stores,
    )
