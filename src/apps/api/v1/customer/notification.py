from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Security, Query

from src.apps.auth.deps import get_current_user
from src.apps.notification import schema as notification_schema
from src.apps.notification.constants import ALL_NOTIFICATION_TYPE, NotificationType
from src.apps.notification.controller import notification_controller
from src.apps.notification.messages import NotificationMessageEnum
from src.apps.user.models import User
from src.core.base.schema import PaginatedResponse, Response
from src.core.mixins.fields import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses
from src.core.utils import return_on_failure
from src.main.config import collections_names

notification_router = APIRouter()
entity = collections_names.NOTIFICATION


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
