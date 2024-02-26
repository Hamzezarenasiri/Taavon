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
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.organization import schema as organization_schema
from src.apps.organization.controller import organization_controller
from src.apps.organization.messages import OrganizationMessageEnum
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

organization_router = APIRouter()
entity = collections_names.ORGANIZATION


@organization_router.post(
    "",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[organization_schema.OrganizationCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_organization(
    payload: organization_schema.OrganizationCreateIn,
    _: User = Security(get_current_user, scopes=[entity, "create"]),
):
    result_data = await organization_controller.create_new_obj(new_data=payload)
    if result_data:
        result_data = await organization_controller.get_single_organization(
            target_organization_id=result_data.id
        )
    return Response[organization_schema.OrganizationCreateOut](
        data=result_data, message=OrganizationMessageEnum.create_new_organization
    )


@organization_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[organization_schema.OrganizationSubListOut]]
    ],
    description="",
)
@return_on_failure
async def get_organization_list(
    search: Optional[str] = Query(None, alias="search", name="Search"),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {
        "$or": [
            {"ancestors": current_user.organization_id},
            {"_id": current_user.organization_id},
        ]
    }
    if search:
        search = ar_to_fa(search)
        criteria["$or"] = [
            {"name": re.compile(search, re.IGNORECASE)},
            {"text": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await organization_controller.get_list_objs(
        pagination=pagination, ordering=ordering, criteria=criteria
    )
    return Response[
        PaginatedResponse[List[organization_schema.OrganizationSubListOut]]
    ](data=result_data, message=OrganizationMessageEnum.get_organizations)


@organization_router.get(
    "/{organization_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[organization_schema.OrganizationGetOut],
)
@return_on_failure
async def get_single_organization(
    organization_id: SchemaID = Path(...),
    _: User = Security(
        get_current_user,
        scopes=[entity, "read"],
    ),
):
    result_data = await organization_controller.get_single_organization(
        target_organization_id=organization_id,
    )
    return Response[organization_schema.OrganizationGetOut](
        data=result_data, message=OrganizationMessageEnum.get_single_organization
    )


@organization_router.get(
    "/{organization_id}/descendant",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[organization_schema.OrganizationGetListOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_organization_descendant(
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    organization_id: SchemaID = Path(...),
    search: Optional[str] = Query(None),
):
    criteria = {
        "$or": [
            {"ancestors": current_user.organization_id},
            {"_id": current_user.organization_id},
        ],
        "ancestors": organization_id,
    }
    if search:
        search = ar_to_fa(search)
        criteria["$or"] = [
            {"name": re.compile(search, re.IGNORECASE)},
            {"text": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await organization_controller.get_list_objs_without_pagination(
        criteria=criteria
    )
    return Response[organization_schema.OrganizationGetListOut](
        data=organization_schema.OrganizationGetListOut(result=result_data),
        message=OrganizationMessageEnum.get_organizations,
    )


@organization_router.get(
    "/all",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[organization_schema.OrganizationGetListOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_organization_without_pagination(
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    search: Optional[str] = Query(None),
):
    criteria = {
        "$or": [
            {"ancestors": current_user.organization_id},
            {"_id": current_user.organization_id},
        ]
    }
    if search:
        search = ar_to_fa(search)
        criteria["$or"] = [
            {"name": re.compile(search, re.IGNORECASE)},
            {"text": re.compile(search, re.IGNORECASE)},
        ]

    result_data = await organization_controller.get_list_objs_without_pagination(
        criteria=criteria
    )
    return Response[organization_schema.OrganizationGetListOut](
        data=organization_schema.OrganizationGetListOut(result=result_data),
        message=OrganizationMessageEnum.get_organizations,
    )


@organization_router.patch(
    "/{organization_id}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[organization_schema.OrganizationUpdateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_organization(
    background_tasks: BackgroundTasks,
    payload: organization_schema.OrganizationUpdateIn,
    organization_id: SchemaID = Path(...),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result_data = await organization_controller.update_single_obj(
        criteria={"_id": organization_id},
        new_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=organization_id,
    )
    return Response[organization_schema.OrganizationUpdateOut](
        data=result_data, message=OrganizationMessageEnum.update_organization
    )


@organization_router.patch(
    "",
    responses={**common_responses},
    response_model=Response[organization_schema.BulkUpdateOut],
    description="Update organization",
)
@return_on_failure
async def update_organization(
    background_tasks: BackgroundTasks,
    payload: organization_schema.OrganizationBulkUpdateIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result = await organization_controller.bulk_update_objs(
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
        data=organization_schema.BulkUpdateOut(is_updated=bool(result)),
        message=OrganizationMessageEnum.update_organization,
    )


@organization_router.delete(
    "/{organization_id}/",
    status_code=204,
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_organization(
    background_tasks: BackgroundTasks,
    organization_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "delete"]),
):
    if await organization_controller.soft_delete_obj(_id=organization_id):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=organization_id,
        )
        return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@organization_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_organizations(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    await organization_controller.bulk_delete_objs(
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
