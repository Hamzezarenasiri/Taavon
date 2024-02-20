from fastapi import status

from src.core.common.enums import (
    Unauthorized401DetailEnum,
    Unauthorized401MessageEnum,
    UpdatePass422DetailEnum,
    UpdatePass422MessageEnum,
)
from src.core.common.exceptions.base import CustomHTTPException
from . import constants as auth_enums

InvalidTempToken = CustomHTTPException(
    detail=Unauthorized401DetailEnum.invalid_temp_token,
    message=Unauthorized401MessageEnum.invalid_temp_token,
    status_code=status.HTTP_401_UNAUTHORIZED,
)
InvalidTokenProvided = CustomHTTPException(
    detail=Unauthorized401DetailEnum.invalid_token,
    message=Unauthorized401MessageEnum.invalid_token,
    status_code=status.HTTP_401_UNAUTHORIZED,
)
TokenExpired = CustomHTTPException(
    detail=Unauthorized401DetailEnum.access_token_expired,
    message=Unauthorized401MessageEnum.access_token_expired,
    status_code=status.HTTP_401_UNAUTHORIZED,
)
RefreshTokenExpired = CustomHTTPException(
    detail=Unauthorized401DetailEnum.refresh_token_expired,
    message=Unauthorized401MessageEnum.refresh_token_expired,
    status_code=status.HTTP_401_UNAUTHORIZED,
)
PermissionDenied = CustomHTTPException(
    detail=auth_enums.AuthForbidden403DetailEnum.permission_denied,
    message=auth_enums.AuthForbidden403MessageEnum.permission_denied,
    status_code=status.HTTP_403_FORBIDDEN,
)
OTPExpiredOrInvalid = CustomHTTPException(
    detail=auth_enums.AuthNotFound404DetailEnum.otp_expired,
    message=auth_enums.AuthNotFound404MessageEnum.otp_expired,
    status_code=status.HTTP_404_NOT_FOUND,
)
LimitedToken = CustomHTTPException(
    detail=Unauthorized401DetailEnum.limited_token,
    message=Unauthorized401MessageEnum.limited_token,
    status_code=status.HTTP_401_UNAUTHORIZED,
)

OldPasswordNotMatch = CustomHTTPException(
    detail=UpdatePass422DetailEnum.old_password_not_match,
    message=UpdatePass422MessageEnum.old_password_not_match,
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
)
UserForceLogin = CustomHTTPException(
    detail=auth_enums.AuthForbidden403DetailEnum.is_force_login,
    message=auth_enums.AuthForbidden403MessageEnum.is_force_login,
    status_code=status.HTTP_403_FORBIDDEN,
)

UserRegisterEmailExists = CustomHTTPException(
    detail=[auth_enums.AuthErrorMessageEnum.user_exists_email],
    message=auth_enums.AuthErrorMessageEnum.user_exists_email,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
)

UserRegisterPhoneExists = CustomHTTPException(
    detail=[auth_enums.AuthErrorMessageEnum.user_exists_phone],
    message=auth_enums.AuthErrorMessageEnum.user_exists_phone,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
)

UserSocialLoginNotAcceptable = CustomHTTPException(
    detail=[auth_enums.AuthErrorMessageEnum.social_login_failed],
    message=auth_enums.AuthErrorMessageEnum.social_login_failed,
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
)

RolesHaveUser = CustomHTTPException(
    message=auth_enums.RoleErrorMessageEnum.roles_have_user,
    status_code=status.HTTP_400_BAD_REQUEST,
)
