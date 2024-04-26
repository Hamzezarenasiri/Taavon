from typing import Union, Tuple

from fastapi import APIRouter, Security, Depends

from src.apps.auth.constants import AuthConflict409MessageEnum, AuthMessageEnum
from src.apps.auth.schema import (
    AuthChangedPasswordMessageOut,
    AuthUserChangePasswordIn,
    AuthChangedPasswordErrorMessageOut,
)
from src.apps.auth.deps import get_current_user, get_user_limited_token
from src.apps.user import schema as user_schema
from src.apps.user.controller import profile_controller, user_controller
from src.apps.user.models import User
from src.core.base.schema import Response, ErrorResponse
from src.core.responses import common_responses, response_500
from src.core.utils import return_on_failure
from src.main.config import collections_names

profile_router = APIRouter()
entity = collections_names.PROFILE


@profile_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.ProfileGetMeOut],
    description="Get customer profile data",
    response_model_by_alias=False,
)
@return_on_failure
async def my_profile(
    current_user: User = Security(get_current_user),
) -> Response[user_schema.ProfileGetMeOut]:
    result_data = await profile_controller.get_my_profile(current_user=current_user)
    return Response[user_schema.ProfileGetMeOut](data=result_data)


@profile_router.get(
    "/permissions",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.ProfileGetPermissions],
    description="Get User Permissions",
)
@return_on_failure
async def my_permissions(
    current_user: User = Security(get_current_user),
) -> Response[user_schema.ProfileGetPermissions]:
    result_data = await profile_controller.get_my_permissions(current_user=current_user)
    return Response[user_schema.ProfileGetPermissions](data=result_data)


@profile_router.get(
    "/permissions_dict",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.ProfileGetPermissionsDict],
    description="Get User Permissions",
)
@return_on_failure
async def get_my_permissions_dict(
    current_user: User = Security(get_current_user),
) -> Response[user_schema.ProfileGetPermissionsDict]:
    result_data = await profile_controller.get_my_permissions_dict(
        current_user=current_user
    )
    return Response[user_schema.ProfileGetPermissionsDict](data=result_data)


@profile_router.post(
    "/password/change",
    responses={
        409: {"model": ErrorResponse[AuthConflict409MessageEnum]},
        **response_500,
    },
    response_model=Response[
        Union[
            AuthChangedPasswordMessageOut,
            AuthChangedPasswordErrorMessageOut,
        ]
    ],
    description="`By `Hamze.zn`",
)
@return_on_failure
async def change_password(
    payload: AuthUserChangePasswordIn,
    current_user: User = Security(get_current_user),
):
    result_data, is_changed = await user_controller.change_password(
        verification=payload, current_user=current_user
    )
    if is_changed:
        message = AuthMessageEnum.changed_password
        success = True
    else:
        message = AuthMessageEnum.changed_password_failed
        success = False
    return Response[
        Union[
            AuthChangedPasswordMessageOut,
            AuthChangedPasswordErrorMessageOut,
        ]
    ](
        data=result_data,
        success=success,
        message=message,
        detail=[message],
    )
