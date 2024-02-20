from typing import Tuple, Union

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Security

from src.apps.auth import schema as auth_schema
from src.apps.auth.controller import auth_controller
from src.apps.auth.deps import get_current_user, get_user_limited_token
from src.apps.auth.constants import (
    AuthConflict409MessageEnum,
    AuthMessageEnum,
)
from src.apps.user.controller import user_controller
from src.apps.user.models import User
from src.core.base.schema import ErrorResponse, Response
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
    google_settings,
    jwt_settings,
)

refresh_valid_seconds = jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS

auth_router = APIRouter()

#
# @auth_router.post(
#     "/otp/send",
#     description="username( `email` or `mobile_number`)\n\n"
#     "if entered username is `email` >> `mail` otp to entered email\n\n"
#     # "if entered username is `phone` >> `sms` otp to entered phone\n\n"
#     "By `Hamze.zn`",
#     responses={
#         **response_404,
#         **response_500,
#     },
#     # response_model=Response,
# )
# @return_on_failure
# async def otp_request(
#     background_tasks: BackgroundTasks,
#     payload: auth_schema.AuthUserForgetOtpReqIn,
# ):
#     result_detail = await auth_controller.otp_request(
#         request_payload=payload,
#         background_tasks=background_tasks,
#         request_type=OtpRequestType.reset_pass,
#     )
#
#     return Response(detail=result_detail.detail, message=AuthMessageEnum.otp_request)
#
#
# @auth_router.post(
#     "/otp/send-verification-request",
#     description="username( `email` or `mobile_number`)\n\n"
#     "if entered username is `email` >> `mail` otp to entered email\n\n"
#     # "if entered username is `phone` >> `sms` otp to entered phone\n\n"
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
#
#
# @auth_router.post(
#     "/otp/verify",
#     responses={
#         **response_404,
#         **response_500,
#     },
#     response_model=Response[auth_schema.AuthToken],
# )
# @return_on_failure
# async def otp_verify(verification: auth_schema.AuthOTPVerifyIn):
#     result_data = await auth_controller.verify_otp(verification=verification)
#     return Response[auth_schema.AuthToken](data=result_data)
#


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
