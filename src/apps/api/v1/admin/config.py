from fastapi import APIRouter, Security, BackgroundTasks, status

from src.apps.auth.deps import get_current_user
from src.apps.config import schema as config_schema
from src.apps.config.controller import config_controller
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.user.models import User
from src.core.base.schema import Response
from src.core.responses import common_responses
from src.core.utils import return_on_failure
from src.main.config import collections_names

config_router = APIRouter()
entity = collections_names.CONFIG


@config_router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
    response_model=Response[config_schema.ConfigGetOut],
    response_model_exclude_none=True,
    description="Get configurations",
)
@return_on_failure
async def get_configs(
    _: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
):
    result_data = await config_controller.get_configs()
    return Response[config_schema.ConfigGetOut](data=result_data)


@config_router.patch(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
    response_model=Response[config_schema.ConfigUpdateOut],
    description="Update an existing configuration using provided config_id",
)
@return_on_failure
async def update_single_config(
    background_tasks: BackgroundTasks,
    payload: config_schema.ConfigUpdateIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
) -> Response[config_schema.ConfigUpdateOut]:
    result_data = await config_controller.update_single_config(
        new_config_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id="",
    )
    return Response[config_schema.ConfigUpdateOut](data=result_data)
