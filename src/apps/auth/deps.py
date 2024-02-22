import contextlib
from typing import Optional, Tuple

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from src.apps.user import exceptions as user_exception
from src.apps.user.models import User
from src.core.common.enums import RoleEnum
from src.core.token import token_helper
from . import exceptions
from .crud import permissions_crud
from .exceptions import UserForceLogin
from ..user.controller import user_controller

# from casbin import Enforcer

jwt_authentication = HTTPBearer()


async def get_user_obj(token) -> User:
    payload = await token_helper.verify_token(token.credentials)
    if payload.limited:
        raise exceptions.LimitedToken
    if not payload.user_id:
        raise exceptions.InvalidTokenProvided
    user_obj = await user_controller.find_by_user_id(user_id=payload.user_id)
    if not user_obj:
        raise user_exception.UserNotFound
    if user_obj.is_force_login:
        raise UserForceLogin
    if not user_obj.is_enabled:
        raise user_exception.UserIsDisabled
    # if user_obj.is_blocked:
    #     raise user_exception.UserIsBlocked
    # if user_obj.email and not user_obj.email_verified:
    #     raise user_exception.UserEmailNotVerified(data=dict(username=user_obj.email))
    # if user_obj.mobile_number and not user_obj.phone_verified:
    #     raise user_exception.UserPhoneNotVerified(
    #         data=dict(username=user_obj.mobile_number)
    #     )
    return user_obj


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
    security_scopes: SecurityScopes = None,
) -> User:
    user_obj = await get_user_obj(token)
    if not security_scopes.scopes:
        return user_obj
    return await permissions_crud.check_permissions(security_scopes, user_obj)


# async def get_current_user(
#     token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
# ) -> User:
#     user_obj = await get_user_obj(token)
#     return user_obj


optional_jwt_authentication = HTTPBearer(auto_error=False)


async def get_optional_current_user(
    token: Optional[HTTPAuthorizationCredentials] = Depends(
        optional_jwt_authentication
    ),
) -> Optional[User]:
    if token:
        with contextlib.suppress(HTTPException):
            payload = await token_helper.verify_token(token.credentials)
            if not payload.limited and payload.user_id:
                user_obj = await user_controller.find_by_user_id(
                    user_id=payload.user_id
                )
                if user_obj:
                    return user_obj
    return None


async def get_user_limited_token(
    token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
) -> Tuple[User, bool]:
    payload = await token_helper.verify_token(token.credentials)
    user_obj = await user_controller.find_by_user_id(user_id=payload.user_id)
    if not user_obj:
        raise user_exception.UserNotFound
    if not user_obj.is_enabled:
        raise user_exception.UserIsDisabled
    # if user_obj.is_blocked:
    #     raise user_exception.UserIsBlocked
    return user_obj, payload.limited
