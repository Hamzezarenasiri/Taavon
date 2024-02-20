from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Security, status, Query
from fastapi.responses import Response as StarletteResponse

from src.apps.auth.deps import get_current_user
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.notification import schema as notification_schema
from src.apps.notification.constants import ALL_NOTIFICATION_TYPE, NotificationType
from src.apps.notification.controller import notification_controller
from src.apps.notification.messages import NotificationMessageEnum
from src.apps.user.models import User
from src.core.base.schema import BulkDeleteIn, PaginatedResponse, Response
from src.core.mixins.fields import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

notification_router = APIRouter()
entity = collections_names.NOTIFICATION


@notification_router.post(
    "",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[notification_schema.NotificationCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_notification(
    background_tasks: BackgroundTasks,
    payload: notification_schema.NotificationCreateIn,
    current_user: User = Security(get_current_user, scopes=[entity, "create"]),
):
    result_data = await notification_controller.create_new_obj(new_data=payload)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=result_data.id,
    )
    return Response[notification_schema.NotificationCreateOut](
        data=result_data, message=NotificationMessageEnum.create_new_notification
    )


@notification_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[notification_schema.NotificationSubListOut]]
    ],
    description="",
)
@return_on_failure
async def get_notification_list(
    notification_type: Optional[List[NotificationType]] = Query(
        None, enum=ALL_NOTIFICATION_TYPE
    ),
    is_read: Optional[bool] = Query(None),
    _: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {}
    if is_read is not None:
        criteria["is_read"] = is_read
    if notification_type:
        criteria["notification_type"] = {"$in": notification_type}
    result_data = await notification_controller.get_list_objs(
        pagination=pagination, ordering=ordering, criteria=criteria
    )
    return Response[
        PaginatedResponse[List[notification_schema.NotificationSubListOut]]
    ](data=result_data, message=NotificationMessageEnum.get_notifications)


@notification_router.get(
    "/{notification_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[notification_schema.NotificationGetOut],
)
@return_on_failure
async def get_single_notification(
    notification_id: SchemaID = Path(...),
    _: User = Security(
        get_current_user,
        scopes=[entity, "read"],
    ),
):
    result_data = await notification_controller.get_single_obj(
        id=notification_id,
    )
    return Response[notification_schema.NotificationGetOut](
        data=result_data, message=NotificationMessageEnum.get_single_notification
    )


@notification_router.patch(
    "",
    responses={**common_responses},
    response_model=Response[notification_schema.BulkUpdateOut],
    description="Update notification",
)
@return_on_failure
async def update_notification(
    background_tasks: BackgroundTasks,
    payload: notification_schema.NotificationBulkUpdateIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result = await notification_controller.bulk_update_objs(
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
        data=notification_schema.BulkUpdateOut(is_updated=bool(result)),
        message=NotificationMessageEnum.update_notification,
    )


@notification_router.delete(
    "/{notification_id}/",
    status_code=204,
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_notification(
    background_tasks: BackgroundTasks,
    notification_id: SchemaID = Path(...),
    current_user: User = Security(get_current_user, scopes=[entity, "delete"]),
):
    if await notification_controller.soft_delete_obj(_id=notification_id):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=notification_id,
        )
        return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@notification_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_notifications(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    await notification_controller.bulk_delete_objs(
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
