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


@category_router.post(
    "",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[category_schema.CategoryCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_category(
    background_tasks: BackgroundTasks,
    payload: category_schema.CategoryCreateIn,
    current_user: User = Security(get_current_user, scopes=[entity, "create"]),
):
    result_data = await category_controller.create_new_category(
        new_category_data=payload
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=result_data.id,
    )
    return Response[category_schema.CategoryCreateOut](
        data=result_data, message=CategoryMessageEnum.create_new_category
    )


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
    criteria = {"is_deleted": False}
    if cat_id:
        criteria.update(parent=cat_id)
    if is_enabled is not None:
        criteria["is_enabled"] = is_enabled
    result_data = await category_controller.get_all_category_admin(
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
    criteria = {"is_enabled": True, "is_deleted": False, "parent": parent}

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
        criteria={"parent": None, "is_deleted": False}
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


@category_router.patch(
    "/{category_id}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[category_schema.CategoryUpdateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_category(
    background_tasks: BackgroundTasks,
    payload: category_schema.CategoryUpdateIn,
    category_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "update"]),
):
    result_data = await category_controller.update_single_category(
        target_id=category_id,
        new_category_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=category_id,
    )
    return Response[category_schema.CategoryUpdateOut](
        data=result_data, message=CategoryMessageEnum.update_category
    )


# @category_router.delete(
#     "/{category_id}/",
#     status_code=204,
#     responses={
#         **common_responses,
#         **response_404,
#     },
#     description="By `Hamze.zn`",
# )
# @return_on_failure
# async def delete_single_category(
#     background_tasks: BackgroundTasks,
#     category_id: SchemaID = Path(...),
#     current_user: User = Security(get_current_user, scopes=[entity, "delete"]),
# ):
#     if await category_controller.soft_delete_single_category(
#         target_category_id=category_id,
#     ):
#         background_tasks.add_task(
#             func=log_controller.create_log,
#             action=LogActionEnum.update,
#             action_by=current_user.id,
#             entity=entity,
#             entity_id=category_id,
#         )
#         return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


# @category_router.delete(
#     "",
#     responses={
#         **common_responses,
#         **response_404,
#     },
#     description="By `Hamze.zn`",
# )
# @return_on_failure
# async def bulk_delete_categories(
#     background_tasks: BackgroundTasks,
#     payload: BulkDeleteIn,
#     current_user: User = Security(
#         get_current_user,
#         scopes=[entity, "delete"],
#     ),
# ):
#     await category_controller.bulk_delete_categories(obj_ids=payload.ids)
#     background_tasks.add_task(
#         func=log_controller.bulk_create_log,
#         action=LogActionEnum.delete,
#         action_by=current_user.id,
#         entity=entity,
#         entity_ids=payload.ids,
#     )
#     return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


# @category_router.get(
#     "/{category_id}/attributes",
#     responses={
#         **common_responses,
#     },
#     response_model=Response[category_schema.CategoryAttributesGetOut],
#     description="By `Hamze.zn`",
# )
# @return_on_failure
# async def get_category_attributes(
#     current_user: User = Security(get_current_user),
#     lang: Optional[LanguageEnum] = Query(
#         default=app_settings.DEFAULT_LANGUAGE,
#         enum=ALL_LANGUAGES,
#         title="Current Selected Language",
#     ),
#     category_id: Optional[SchemaID] = Path(default="all"),
# ):
#     result_data = await category_controller.get_category_attributes(
#         target_id=None if category_id == "all" else category_id,
#         language=lang
#         or (
#             current_user.settings.language
#             if current_user
#             else app_settings.DEFAULT_LANGUAGE
#         ),
#     )
#     return Response[category_schema.CategoryAttributesGetOut](
#         data=result_data, message=CategoryMessageEnum.get_category_attributes
#     )
