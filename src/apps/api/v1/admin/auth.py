from fastapi import APIRouter, Security, BackgroundTasks

from src.apps.auth import schema as auth_schema
from src.apps.auth.constants import AuthMessageEnum
from src.apps.auth.controller import auth_controller
from src.apps.auth.deps import get_current_user
from src.apps.user.models import User
from src.core.base.schema import Response
from src.core.common.models.token import RefreshRequest
from src.core.responses import (
    common_responses,
    response_404,
    response_500,
    response_401,
)
from src.core.utils import return_on_failure
from src.main.config import jwt_settings

refresh_valid_seconds = jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS

admin_auth_router = APIRouter()


@admin_auth_router.post(
    "/login",
    responses={**response_404, **response_500},
    response_model=Response[auth_schema.AuthToken],
    description="By `Hamze.zn`",
)
@return_on_failure
async def login_username_password(
    user_pass: auth_schema.AuthUsernamePasswordIn,
    background_tasks: BackgroundTasks,
):
    result_data = await auth_controller.login_username_password(
        background_tasks=background_tasks,
        user_pass=user_pass,
    )
    return Response[auth_schema.AuthToken](data=result_data)


@admin_auth_router.get(
    "/logout",
    responses={**common_responses},
    response_model=Response[auth_schema.UserGetLogoutOut],
)
@return_on_failure
async def logout_user(
    current_user: User = Security(get_current_user),
):
    result_data = await auth_controller.logout_user(current_user=current_user)
    return Response[auth_schema.UserGetLogoutOut](data=result_data)


@admin_auth_router.post(
    "/token/refresh",
    responses={
        **response_401,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
)
@return_on_failure
async def refresh_token(refresh_request: RefreshRequest):
    result_data = await auth_controller.refresh_token(refresh_request)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.refresh_token
    )
