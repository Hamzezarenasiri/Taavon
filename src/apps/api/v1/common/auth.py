from typing import Union, Tuple

from fastapi import APIRouter, BackgroundTasks, Security
from fastapi import Depends

from src.apps.auth import schema as auth_schema
from src.apps.auth.constants import (
    AuthMessageEnum,
    AuthConflict409MessageEnum,
    AuthErrorMessageEnum,
)
from src.apps.auth.controller import auth_controller
from src.apps.auth.deps import get_current_user, get_user_limited_token
from src.apps.user.controller import user_controller, profile_controller
from src.apps.user.models import User
from src.core.base.schema import Response, ErrorResponse
from src.core.common.models.token import RefreshRequest
from src.core.otp import OtpRequestType
from src.core.responses import (
    common_responses,
    response_401,
    response_404,
    response_500,
)
from src.core.utils import return_on_failure
from src.main.config import (
    jwt_settings,
)

REFRESH_VALID_SECONDS = jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS

auth_router = APIRouter()


#
@auth_router.post(
    "/otp/send",
    description="username(`mobile_number`)\n\n"
    "if entered username is `phone` >> `sms` otp to entered phone\n\n"
    "By `Hamze.zn`",
    responses={
        **response_404,
        **response_500,
    },
    # response_model=Response,
)
@return_on_failure
async def otp_request(
    background_tasks: BackgroundTasks,
    payload: auth_schema.AuthUserForgetOtpReqIn,
):
    result_detail = await auth_controller.otp_request(
        request_payload=payload,
        background_tasks=background_tasks,
        request_type=OtpRequestType.verification,
    )

    return Response(detail=result_detail.detail, message=AuthMessageEnum.otp_request)


# @auth_router.post(
#     "/otp/send-verification-request",
#     description="username( `email` or `mobile_number`)\n\n"
#     "if entered username is `phone` >> `sms` otp to entered phone\n\n"
#     "By `Hamze.zn`",
#     responses={
#         **response_404,
#         **response_500,
#     },
#     # response_model=Response,
# )
# @return_on_failure
# async def otp_verification_request(
#     background_tasks: BackgroundTasks,
#     payload: auth_schema.AuthUserForgetOtpReqIn,
# ):
#     result_detail = await auth_controller.otp_request(
#         request_payload=payload,
#         background_tasks=background_tasks,
#         request_type=OtpRequestType.verification,
#     )
#
#     return Response(detail=result_detail.detail, message=AuthMessageEnum.otp_request)


@auth_router.post(
    "/otp/verify",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthTokenAndProfile],
)
@return_on_failure
async def otp_verify(verification: auth_schema.AuthOTPVerifyIn):
    (
        current_user,
        tokens,
    ) = await auth_controller.verify_otp_return_token_and_user(
        verification=verification
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


@auth_router.post(
    "/token/refresh",
    responses={
        **response_401,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
)
@return_on_failure
async def refresh_token(
    refresh_request: RefreshRequest,
):
    result_data = await auth_controller.refresh_token(refresh_request)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.refresh_token
    )


@auth_router.get(
    "/logout",
    responses={
        **common_responses,
    },
    response_model=Response[auth_schema.UserGetLogoutOut],
)
@return_on_failure
async def logout_user(
    current_user: User = Security(get_current_user),
):
    result_data = await auth_controller.logout_user(current_user=current_user)
    return Response[auth_schema.UserGetLogoutOut](
        data=result_data, message=AuthMessageEnum.logout_user
    )


@auth_router.post(
    "/password/forgot/otp_send",
    description="username(`mobile_number`)\n\n"
    # "if entered username is `email` >> `mail` otp to entered email\n\n"
    "if entered username is `phone` >> `sms` otp to entered phone\n\n" "By `Hamze.zn`",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response,
)
@return_on_failure
async def otp_reset_pass_request(
    background_tasks: BackgroundTasks,
    payload: auth_schema.AuthUserForgetOtpReqIn,
):
    result_detail = await auth_controller.otp_request(
        request_payload=payload,
        background_tasks=background_tasks,
        request_type=OtpRequestType.reset_pass,
    )

    return Response(detail=result_detail.detail, message=AuthMessageEnum.otp_request)


@auth_router.post(
    "/password/forgot/verify",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthForgetVerifyOut],
)
@return_on_failure
async def otp_reset_pass_verify_and_get_rest_token(
    verification: auth_schema.AuthOTPVerifyIn,
):
    result_data = await auth_controller.limited_verify_otp(verification=verification)
    return Response[auth_schema.AuthForgetVerifyOut](
        data=result_data, message=AuthMessageEnum.otp_verify_limited
    )


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
