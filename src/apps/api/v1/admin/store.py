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


@store_router.post(
    "",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[store_schema.StoreCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_store(
    payload: store_schema.StoreCreateIn,
    _: User = Security(get_current_user, scopes=[entity, "create"]),
):
    owner = users_crud.get_object(criteria={"_id": payload.owner_id})
    result_data = await store_controller.create_new_obj(new_data=payload, owner=owner)
    if result_data:
        result_data = await store_controller.get_single_store(
            target_store_id=result_data.id
        )
    return Response[store_schema.StoreCreateOut](
        data=result_data, message=StoreMessageEnum.create_new_store
    )


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
    current_user: User = Security(
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
    current_user: User = Security(
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


@store_router.patch(
    "/{store_id}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[store_schema.StoreUpdateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_store(
    background_tasks: BackgroundTasks,
    payload: store_schema.StoreUpdateIn,
    store_id: SchemaID = Path(...),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result_data = await store_controller.update_single_obj(
        criteria={"_id": store_id},
        new_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=store_id,
    )
    return Response[store_schema.StoreUpdateOut](
        data=result_data, message=StoreMessageEnum.update_store
    )


@store_router.patch(
    "",
    responses={**common_responses},
    response_model=Response[store_schema.BulkUpdateOut],
    description="Update store",
)
@return_on_failure
async def update_store(
    background_tasks: BackgroundTasks,
    payload: store_schema.StoreBulkUpdateIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result = await store_controller.bulk_update_objs(
        obj_ids=payload.ids,
        new_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return Response(
        data=store_schema.BulkUpdateOut(is_updated=bool(result)),
        message=StoreMessageEnum.update_store,
    )


@store_router.delete(
    "/{store_id}/",
    status_code=204,
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_store(
    background_tasks: BackgroundTasks,
    store_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "delete"]),
):
    if await store_controller.soft_delete_obj(_id=store_id):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=store_id,
        )
        return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@store_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_stores(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    await store_controller.bulk_delete_objs(
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
