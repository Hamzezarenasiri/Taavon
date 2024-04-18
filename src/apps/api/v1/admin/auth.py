from fastapi import APIRouter, Security, BackgroundTasks

from src.apps.auth import schema as auth_schema
from src.apps.auth.constants import AuthMessageEnum
from src.apps.auth.controller import auth_controller
from src.apps.auth.deps import get_current_user
from src.apps.user.controller import profile_controller
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
    response_model=Response[auth_schema.AuthTokenAndProfile],
    description="By `Hamze.zn`",
)
@return_on_failure
async def login_username_password(
    user_pass: auth_schema.AuthUsernamePasswordIn,
    background_tasks: BackgroundTasks,
):
    (
        current_user,
        tokens,
    ) = await auth_controller.login_username_password_return_token_and_user(
        background_tasks=background_tasks,
        user_pass=user_pass,
    )
    profile = await profile_controller.get_my_profile(current_user=current_user)
    profile.permissions = (
        (await profile_controller.get_my_permissions_dict(current_user=current_user))
        .dict()
        .get("permissions")
    )
    result_data = auth_schema.AuthTokenAndProfile(
        **profile.dict(),
        **tokens.dict(),
    )
    return Response[auth_schema.AuthTokenAndProfile](data=result_data)


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
