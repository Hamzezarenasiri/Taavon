import re
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Security, Query
from persiantools.characters import ar_to_fa

from src.apps.auth import schema as auth_schema
from src.apps.auth.constants import EntityMessageEnum
from src.apps.auth.controller import entity_controller
from src.apps.auth.deps import get_current_user
from src.apps.user.models import User
from src.core.base.schema import Response, PaginatedResponse
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

entity_router = APIRouter()
entity = collections_names.ENTITY


@entity_router.post(
    "",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[auth_schema.EntityCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_entity(
    payload: auth_schema.EntityCreateIn,
    _: User = Security(get_current_user, scopes=[entity, "create"]),
):
    result_data = await entity_controller.create_new_obj(new_data=payload)
    return Response[auth_schema.EntityCreateOut](
        data=result_data, message=EntityMessageEnum.create_new_entity
    )


@entity_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[PaginatedResponse[List[auth_schema.EntityGetSubListOut]]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_entity(
    _: User = Security(get_current_user, scopes=[entity, "list"]),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    result_data = await entity_controller.get_list_objs(
        pagination=pagination, ordering=ordering
    )
    return Response[PaginatedResponse[List[auth_schema.EntityGetSubListOut]]](
        data=result_data.dict(), message=EntityMessageEnum.get_entities
    )


@entity_router.get(
    "/all",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[auth_schema.EntitiesGetListOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_entity_without_pagination(
    _: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    search: Optional[str] = Query(None),
):
    criteria = {}
    if search:
        search = ar_to_fa(search)
        if search := re.sub(r"[()\[\]'*+?\\]", "", search):
            criteria["$or"] = [
                {"code_name": re.compile(search, re.IGNORECASE)},
                {"description": re.compile(search, re.IGNORECASE)},
            ]

    result_data = await entity_controller.get_list_objs_without_pagination(
        criteria=criteria
    )
    return Response[auth_schema.EntitiesGetListOut](
        data=auth_schema.EntitiesGetListOut(result=result_data),
        message=EntityMessageEnum.get_entities,
    )


@entity_router.get(
    "/{code_name}/",
    responses={
        **common_responses,
    },
    response_model=Response[auth_schema.EntityGetOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_entity(
    code_name: str = Path(...),
    _: User = Security(get_current_user, scopes=[entity, "read"]),
):
    result_data = await entity_controller.get_single_obj(
        code_name=code_name,
    )
    return Response[auth_schema.EntityGetOut](
        data=result_data, message=EntityMessageEnum.get_single_entity
    )


# @entity_router.patch(
#     "/{code_name}/",
#     responses={
#         **common_responses,
#     },
#     response_model=Response[auth_schema.EntityUpdateOut],
#     description="By `Hamze.zn`",
# )
# @return_on_failure
# async def update_single_entity(
#     payload: auth_schema.EntityUpdateIn,
#     code_name: str = Path(...),
#     current_user: UserModel = Security(get_current_user, scopes=[entity, "patch"]),
# ):
#     result_data = await entity_controller.update_single_obj(
#         current_user=current_user,
#         target_code_name=code_name,
#         new_obj_data=payload,
#     )
#     return Response[auth_schema.EntityUpdateOut](
#         data=result_data, message=EntityMessageEnum.update_entity
#     )

#
# @entity_router.delete(
#     "/{code_name}/",
#     status_code=204,
#     responses={
#         **common_responses,
#     },
#     description="By `Hamze.zn`",
# )
# @return_on_failure
# async def delete_single_entity(
#     code_name: str = Path(...),
#     _: UserModel = Security(get_current_user, scopes=[entity, "delete"]),
# ):
#     if await entity_controller.soft_delete_single_obj(
#         target_code_name=code_name,
#     ):
#         return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)
