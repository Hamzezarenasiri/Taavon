from fastapi import APIRouter, Security

from src.apps.auth.deps import get_current_user
from src.apps.user import schema as user_schema
from src.apps.user.controller import profile_controller
from src.apps.user.models import User
from src.core.base.schema import Response
from src.core.responses import common_responses
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
    description="Get admin profile data",
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


@profile_router.patch(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.ProfileGetMeOut],
    description="Update admin profile record",
)
@return_on_failure
async def update_my_profile(
    payload: user_schema.ProfileUpdateMeIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
) -> Response[user_schema.ProfileGetMeOut]:
    result_data = await profile_controller.update_profile(
        current_user=current_user,
        payload=payload,
    )
    return Response[user_schema.ProfileGetMeOut](data=result_data)
