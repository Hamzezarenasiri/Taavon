from typing import Tuple, Union

from fastapi import APIRouter, BackgroundTasks, Depends

from src.core.base.schema import ErrorResponse, Response
from src.core.common.models.token import RefreshRequest
from src.core.mixins import Message
from src.core.responses import response_401, response_404, response_500
from src.core.utils import return_on_failure
from src.main.config import jwt_settings
from . import schema as auth_schema
from .controller import auth_controller
from .deps import get_user_limited_token
from .constants import AuthConflict409MessageEnum, AuthErrorMessageEnum, AuthMessageEnum
from ..user.controller import user_controller
from ..user.models import User

refresh_valid_seconds = jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS

auth_router = APIRouter()


@auth_router.post(
    "/otp/send",
    description="username( `email` or `mobile_number`)\n\n"
    "if entered username is `email` >> `mail` otp to entered email\n\n"
    # "if entered username is `phone` >> `sms` otp to entered phone\n\n"
    "By `Hamze.zn`",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[Message],
)
@return_on_failure
async def otp_request(
    background_tasks: BackgroundTasks,
    payload: auth_schema.AuthUserForgetOtpReqIn,
):
    result_detail = await auth_controller.otp_request(
        request_payload=payload,
        background_tasks=background_tasks,
    )
    return Response[Message](data=result_detail)


@auth_router.post(
    "/otp/verify",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
    description="By `Hamze.zn`",
)
@return_on_failure
async def otp_verify(verification: auth_schema.AuthOTPVerifyIn):
    result_data = await auth_controller.verify_otp(verification=verification)
    return Response[auth_schema.AuthToken](data=result_data)


@auth_router.post(
    "/password/forgot/verify",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthForgetVerifyOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def otp_verify_limited(
    verification: auth_schema.AuthOTPVerifyIn,
):
    result_data = await auth_controller.limited_verify_otp(verification=verification)
    return Response[auth_schema.AuthForgetVerifyOut](data=result_data)


@auth_router.post(
    "/password/forgot/reset",
    responses={
        409: {"model": ErrorResponse[AuthConflict409MessageEnum]},
        **response_500,
    },
    response_model=Response[
        Union[
            auth_schema.AuthUserResetPasswordOut,
            auth_schema.AuthChangedPasswordErrorMessageOut,
        ]
    ],
    description="if token `limited` is `true`:  user can change password\n\nBy `Hamze.zn`",
)
@return_on_failure
async def rest_forgot_password(
    payload: auth_schema.AuthResetPasswordIn,
    current_user_limited: Tuple[User, bool] = Depends(get_user_limited_token),
):
    current_user, is_limited = current_user_limited
    result_data, is_changed = await user_controller.reset_forgot_password(
        verification=payload, current_user=current_user, is_limited=is_limited
    )
    if is_changed:
        message = AuthMessageEnum.changed_password
        success = True
    else:
        message = AuthErrorMessageEnum.changed_password
        success = False
    return Response[
        Union[
            auth_schema.AuthUserResetPasswordOut,
            auth_schema.AuthChangedPasswordErrorMessageOut,
        ]
    ](
        data=result_data,
        success=success,
        message=message,
        detail=[message],
    )


@auth_router.post(
    "/token/refresh",
    responses={
        **response_401,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
    description="By `Hamze.zn`",
)
@return_on_failure
async def refresh_token(
    refresh_request: RefreshRequest,
):
    result_data = await auth_controller.refresh_token(refresh_request)
    return Response[auth_schema.AuthToken](data=result_data)
