from datetime import datetime
from datetime import timezone
from pprint import pprint
from typing import Optional, List

import httpx
from fastapi import BackgroundTasks

from src.apps.user import exceptions as user_exceptions
from src.apps.user.controller import user_controller
from src.apps.user.crud import users_crud
from src.apps.user.models import User
from src.apps.user.schema import CreateUserRoleEnum, UserSocialCreateSchema
from src.core import otp, token
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse
from src.core.common import exceptions
from src.core.common.models.security import UsernamePasswordSchema
from src.core.common.models.token import AuthToken, RefreshRequest
from src.core.mixins import Message, SchemaID
from src.core.mixins.models import USERNAME_IS_PHONE, USERNAME_IS_EMAIL
from src.core.ordering import Ordering
from src.core.otp import OtpRequestType
from src.core.pagination import Pagination
from src.core.password import generate_random_password
from src.main.config import google_settings
from src.services.db.mongodb import UpdateOperatorsEnum
from . import schema as auth_schema
from .constants import AuthOTPTypeEnum
from .crud import entities_crud, roles_crud
from .exceptions import (
    OTPExpiredOrInvalid,
    UserSocialLoginNotAcceptable,
    RolesHaveUser,
)
from .models import Role
from .schema import AuthUsernamePasswordIn
from ..user.constants import UserStatus, LoginType
from ..user.exceptions import (
    UserIsDisabled,
    GoogleCodeNotValid,
)


class AuthController(object):
    async def login_username_password(
        self,
        background_tasks: BackgroundTasks,
        user_pass: AuthUsernamePasswordIn,
    ):
        user = await user_controller.authenticate_by_username_pass(
            username=user_pass.username,
            password=user_pass.password,
        )
        if not user:
            raise user_exceptions.UserNotFound
        if not user.is_enabled:
            raise user_exceptions.UserIsDisabled
        # if user.is_blocked:
        #     raise user_exceptions.UserIsBlocked
        # if user.email and not user.email_verified:
        #     raise UserEmailNotVerified(data=dict(username=user.email))
        # elif user.mobile_number and not user.phone_verified:
        #     raise UserPhoneNotVerified(data=dict(username=user.mobile_number))
        background_tasks.add_task(
            func=users_crud.update,
            criteria={"_id": user.id},
            new_doc={
                "login_datetime": datetime.now(timezone.utc),
                "last_login_datetime": user.login_datetime,
                "login_count": user.login_count + 1,
                "is_force_login": False,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(str(user.id))

    async def login_username_password_by_organization(
        self, user_pass: AuthUsernamePasswordIn
    ):
        user = await user_controller.authenticate_by_username_pass(
            username=user_pass.username,
            password=user_pass.password,
        )
        if not user:
            raise user_exceptions.UserNotFound
        if not user.is_enabled:
            raise user_exceptions.UserIsDisabled
        # if user.is_blocked:
        #     raise user_exceptions.UserIsBlocked
        # if user.email and not user.email_verified:
        #     raise UserEmailNotVerified(data=dict(username=user.email))
        # elif user.mobile_number and not user.phone_verified:
        #     raise UserPhoneNotVerified(data=dict(username=user.mobile_number))
        await users_crud.update(
            criteria={"_id": user.id},
            new_doc={
                "login_datetime": datetime.utcnow(),
                "last_login_datetime": user.login_datetime,
                "login_count": user.login_count + 1,
                "is_force_login": False,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(str(user.id))

    @staticmethod
    async def access_token(
        user_pass: UsernamePasswordSchema,
    ):
        if user_pass.password:
            user = await user_controller.authenticate_by_username_pass(
                username=user_pass.username,
                password=user_pass.password,
            )
        else:
            user = await user_controller.find_by_username(
                username=user_pass.username,
            )
        if not user:
            raise user_exceptions.UserNotFound

        if not user.is_enabled:
            raise user_exceptions.UserIsDisabled
        # if user.is_blocked:
        #     raise user_exceptions.UserIsBlocked
        # if user.email and not user.email_verified:
        #     raise UserEmailNotVerified(data=dict(username=user.email))
        # if user.mobile_number and not user.phone_verified:
        #     raise UserPhoneNotVerified(data=dict(username=user.mobile_number))
        await users_crud.update(
            criteria={"_id": user.id},
            new_doc={
                "login_datetime": datetime.utcnow(),
                "last_login_datetime": user.login_datetime,
                "login_count": user.login_count + 1,
                "is_force_login": False,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id)

    async def otp_request(
        self,
        request_payload: auth_schema.AuthUserForgetOtpReqIn,
        background_tasks: BackgroundTasks,
        request_type: Optional[OtpRequestType] = OtpRequestType.reset_pass,
    ) -> Message:
        username = request_payload.username
        otp_type = {
            USERNAME_IS_PHONE: AuthOTPTypeEnum.sms,
            USERNAME_IS_EMAIL: AuthOTPTypeEnum.email,
        }[username["value_type"]]
        user_obj = await user_controller.get_single_obj(mobile_number=username["value"])
        if user_obj:
            # background_tasks.add_task(
            #     func=otp.set_otp_and_send_message,
            #     user=user_obj,
            #     otp_type=otp_type,
            #     cache_key=username["value"],
            #     request_type=request_type,
            # )
            # return Message()
            await otp.set_otp_and_send_message(
                user=user_obj,
                otp_type=otp_type,
                cache_key=username["value"],
                request_type=request_type,
            )
            return Message()
        else:
            raise user_exceptions.UserNotFound

    @staticmethod
    async def verify_otp(
        verification: auth_schema.AuthOTPVerifyIn,
    ) -> auth_schema.AuthToken:
        user = await user_controller.get_single_obj(
            mobile_number=verification.username["value"]
        )

        if not user:
            raise user_exceptions.UserNotFound
        if (
            await otp.get_otp(key=verification.username.value)
            != verification.verification_code
        ):
            raise OTPExpiredOrInvalid
        new_doc = {
            "login_datetime": datetime.now(timezone.utc),
            "last_login_datetime": user.login_datetime,
            "login_count": user.login_count + 1,
            "is_force_login": False,
        }
        # if verification.username.value_type == USERNAME_IS_EMAIL:
        #     new_doc["email_verified"] = True
        # elif verification.username.value_type == USERNAME_IS_PHONE:
        #     new_doc["phone_verified"] = True
        await users_crud.update(
            criteria={"_id": user.id},
            new_doc=new_doc,
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id)

    @staticmethod
    async def limited_verify_otp(
        verification: auth_schema.AuthOTPVerifyIn,
    ) -> auth_schema.AuthForgetVerifyOut:
        user = await user_controller.get_single_obj(
            mobile_number=verification.username["value"]
        )
        if not user:
            raise user_exceptions.UserNotFound
        if (
            await otp.get_otp(key=verification.username.value)
            != verification.verification_code
        ):
            raise OTPExpiredOrInvalid
        generated_tokens = await token.generate_token(
            user_id=str(user.id),
            limited=True,
        )
        return auth_schema.AuthForgetVerifyOut(
            access_token=generated_tokens.access_token,
            limited=True,
        )

    @staticmethod
    async def refresh_token(
        refresh_request: RefreshRequest,
    ) -> AuthToken:
        return await token.generate_refresh_token(refresh_request.refresh_token)

    async def google_login(self, code: str) -> auth_schema.AuthToken:
        a_url = "https://oauth2.googleapis.com/token"
        a_payload_body = {
            "code": code,
            "client_id": google_settings.CLIENT_ID,
            "redirect_uri": google_settings.LOGIN_REDIRECT_URI,
            "client_secret": google_settings.CLIENT_SECRET,
            "grant_type": "authorization_code",
        }
        b_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        async with httpx.AsyncClient() as client:
            a_res = await client.post(a_url, json=a_payload_body)
            access_token = a_res.json().get("access_token")
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            b_res = await client.get(b_url)
        if b_res.status_code != 200:
            pprint(b_res.json())
            raise GoogleCodeNotValid(detail=[{"response": b_res.json()}])
        res_json = b_res.json()
        return await self.social_register_and_login(
            user_email=res_json["email"],
            first_name=res_json.get("given_name"),
            last_name=res_json.get("family_name"),
            password=generate_random_password(),
            avatar_url=res_json.get("picture"),
            email_verified=bool(res_json.get("email")),
        )

    async def google_login_id_token(self, id_token: str) -> auth_schema.AuthToken:
        b_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        async with httpx.AsyncClient() as client:
            b_res = await client.get(b_url)
        if b_res.status_code != 200:
            pprint(b_res.json())
            raise GoogleCodeNotValid(detail=[{"response": b_res.json()}])
        res_json = b_res.json()
        return await self.social_register_and_login(
            user_email=res_json.get("email"),
            first_name=res_json.get("given_name"),
            last_name=res_json.get("family_name"),
            password=generate_random_password(),
            avatar_url=res_json.get("picture"),
            email_verified=bool(res_json.get("email")),
        )

    async def social_register_and_login(
        self,
        user_email: str,
        first_name: str,
        last_name: str,
        password: str,
        avatar_url: Optional[str] = None,
        email_verified: Optional[bool] = False,
        **kwargs,
    ) -> auth_schema.AuthToken:
        if not user_email:
            raise UserSocialLoginNotAcceptable
        user = await users_crud.get_object(
            dict(email=user_email), raise_exception=False
        )
        if not user:
            user = await user_controller.create_new_user(
                UserSocialCreateSchema(
                    email=user_email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    roles=[CreateUserRoleEnum.user.value],
                    avatar=avatar_url,
                    user_status=UserStatus.just_added,
                    addresses=[],
                    permissions=[],
                ),
                login_type=LoginType.social,
                email_verified=email_verified,
                **kwargs,
            )
        if not user.is_enabled:
            raise UserIsDisabled
        # if user.is_blocked:
        #     raise UserIsBlocked
        # if user.user_status == UserStatus.pending:
        #     raise UserIsPending
        # if user.user_status == UserStatus.rejected:
        #     raise UserIsRejected
        new_doc = {
            "login_datetime": datetime.utcnow(),
            "last_login_datetime": user.login_datetime,
            "login_count": user.login_count + 1,
            "email_verified": email_verified,
        }
        await users_crud.update(
            criteria={"_id": user.id},
            new_doc=new_doc,
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id)

    async def logout_user(
        self,
        current_user: User,
        user_id: SchemaID = None,
    ) -> auth_schema.UserGetLogoutOut:
        if user_id:
            user = await users_crud.get_object(
                criteria={
                    "_id": user_id,
                },
            )
        else:
            user = current_user
        updated_target_user, is_updated = await users_crud.update_and_get(
            criteria={"_id": user.id},
            new_doc={"is_force_login": True},
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return auth_schema.UserGetLogoutOut(
            force_login=updated_target_user.is_force_login
        )


auth_controller = AuthController()


class RoleController(BaseController):
    async def create_new_role(
        self,
        new_role_data: auth_schema.RoleCreateIn,
    ) -> auth_schema.RoleCreateOut:
        for permission in new_role_data.permissions:
            diff = set(permission.rules).difference(
                set(await entities_crud.get_entity_rules(permission.entity))
            )
            if diff:
                raise exceptions.CustomHTTPException(
                    status_code=422,
                    detail=[f"{diff} rules not found"],
                    message=f"{diff} rules not found",
                )

        created = await self.crud.create(Role(**new_role_data.dict(exclude_none=True)))
        return auth_schema.RoleCreateOut(**created.dict())

    async def get_all_role(
        self,
        pagination: Pagination,
        ordering: Ordering,
        criteria: dict = None,
    ) -> PaginatedResponse[List[auth_schema.RoleGetListOut]]:
        query = {}
        if criteria:
            query |= criteria
        return await pagination.paginate(
            crud=self.crud,
            list_item_model=auth_schema.RoleGetListOut,
            criteria=query,
            _sort=await ordering.get_ordering_criteria(),
        )

    async def get_single_role(self, target_role_name: str) -> auth_schema.RoleGetOut:
        target_role = await self.crud.get_object(criteria=dict(name=target_role_name))
        return auth_schema.RoleGetOut(**target_role.dict())

    async def update_single_role(
        self,
        target_role_name: str,
        new_role_data: auth_schema.RoleUpdateIn,
    ) -> auth_schema.RoleUpdateOut:
        await roles_crud.get_an_object({"name": target_role_name})
        if new_role_data.permissions:
            for permission in new_role_data.permissions:
                diff = set(permission.rules).difference(
                    set(await entities_crud.get_entity_rules(permission.entity))
                )
                if diff:
                    raise exceptions.CustomHTTPException(
                        status_code=422,
                        detail=[f"{diff} rules not found"],
                        message=f"{diff} rules not found",
                    )
        (updated_role, is_updated) = await self.crud.default_update_and_get(
            criteria=dict(name=target_role_name),
            new_doc=new_role_data.dict(exclude_none=True),
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return auth_schema.RoleUpdateOut(**updated_role.dict())

    async def soft_delete_single_role(self, name: str) -> bool:
        target_role = await self.crud.get_object(criteria=dict(name=name))
        is_deleted = await self.crud.soft_delete(criteria=dict(name=name))
        if target_role and is_deleted:
            return is_deleted
        else:
            raise exceptions.DeleteFailed

    async def bulk_delete_roles(
        self,
        names: List[str],
    ) -> List[Role]:
        roles_have_user_ids_ = await users_crud.get_list_of_a_field_values(
            target_field="roles",
            criteria={"roles": {"$in": names}},
        )
        if roles_have_user_ids_:
            roles_have_user_ids = {
                val for sublist in roles_have_user_ids_ for val in sublist
            }
        else:
            roles_have_user_ids = []
        updated_roles = await self.crud.bulk_soft_delete(
            obj_ids=list(set(names).difference(roles_have_user_ids)), id_field="name"
        )
        if roles_have_user_ids:
            raise RolesHaveUser(data={"roles_have_user": roles_have_user_ids})

        return updated_roles


role_controller = RoleController(crud=roles_crud)


class EntityController(BaseController):
    pass


entity_controller = EntityController(crud=entities_crud)
