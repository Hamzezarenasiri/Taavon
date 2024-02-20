from typing import List

from fastapi import APIRouter, Depends, Path, Security, status, BackgroundTasks
from fastapi.responses import Response as StarletteResponse

from src.apps.auth import schema as role_schema
from src.apps.auth.constants import RoleMessageEnum
from src.apps.auth.controller import role_controller
from src.apps.auth.deps import get_current_user
from src.apps.auth.schema import RoleBulkDeleteIn
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.user.models import User
from src.core.base.schema import Response, PaginatedResponse
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

role_router = APIRouter()
entity = collections_names.ROLE


@role_router.post(
    "",
    status_code=201,
    responses={**common_responses},
    response_model=Response[role_schema.RoleCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_role(
    background_tasks: BackgroundTasks,
    payload: role_schema.RoleCreateIn,
    current_user: User = Security(get_current_user, scopes=[entity, "create"]),
):
    result_data = await role_controller.create_new_role(
        new_role_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=result_data.name,
    )
    return Response[role_schema.RoleCreateOut](
        data=result_data, message=RoleMessageEnum.create_new_role
    )


@role_router.get(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[PaginatedResponse[List[role_schema.RoleGetListOut]]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_role(
    _: User = Security(get_current_user, scopes=[entity, "list"]),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    result_data = await role_controller.get_all_role(
        pagination=pagination, ordering=ordering, criteria={"is_deleted": False}
    )
    return Response[PaginatedResponse[List[role_schema.RoleGetListOut]]](
        data=result_data.dict(), message=RoleMessageEnum.get_roles
    )


@role_router.get(
    "/{role_name}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[role_schema.RoleGetOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_role(
    role_name: str = Path(...),
    _: User = Security(get_current_user, scopes=[entity, "read"]),
):
    result_data = await role_controller.get_single_role(target_role_name=role_name)
    return Response[role_schema.RoleGetOut](
        data=result_data, message=RoleMessageEnum.get_single_role
    )


@role_router.patch(
    "/{role_name}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[role_schema.RoleUpdateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_role(
    background_tasks: BackgroundTasks,
    payload: role_schema.RoleUpdateIn,
    role_name: str = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "update"]),
):
    result_data = await role_controller.update_single_role(
        target_role_name=role_name,
        new_role_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=role_name,
    )
    return Response[role_schema.RoleUpdateOut](
        data=result_data, message=RoleMessageEnum.update_role
    )


@role_router.delete(
    "/{role_name}/",
    status_code=204,
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_role(
    background_tasks: BackgroundTasks,
    role_name: str = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "delete"]),
):
    if await role_controller.soft_delete_single_role(
        name=role_name,
    ):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=role_name,
        )
        return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@role_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_roles(
    background_tasks: BackgroundTasks,
    payload: RoleBulkDeleteIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    await role_controller.bulk_delete_roles(
        names=payload.names,
    )
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.names,
    )
    return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)
