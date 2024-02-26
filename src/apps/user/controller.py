import os
from datetime import datetime
from datetime import timezone
from glob import glob
from io import BytesIO
from typing import List, Optional, Tuple, Union
from uuid import uuid4

from PIL import Image
from fastapi import BackgroundTasks, HTTPException, status
from pymongo.errors import DuplicateKeyError

from src.apps.auth.exceptions import (
    OldPasswordNotMatch,
    UserRegisterPhoneExists,
    InvalidTempToken,
)
from src.apps.auth.schema import (
    AuthChangedPasswordErrorMessageOut,
    AuthChangedPasswordMessageOut,
    AuthUserChangePasswordIn,
    AuthUserResetPasswordOut,
    AuthToken,
    AuthRegisterIn,
)
from src.apps.file.crud import files_crud
from src.apps.file.schema import FileOut, ValidatedFile
from src.apps.user.schema import (
    UsersCreateIn,
    UsersActivationUserPatchOut,
    UsersBlockingUserPatchOut,
    UsersGetUserOut,
    UsersGetUserSubListOut,
    UsersUpdateIn,
    UserCreateSchemaOut,
)
from src.core import token, otp
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse, Response
from src.core.common import exceptions
from src.core.common.exceptions import DeleteFailed, UpdateFailed
from src.core.mixins.fields import SchemaID
from src.core.mixins.models import USERNAME_IS_PHONE
from src.core.ordering import Ordering
from src.core.otp import OtpRequestType
from src.core.pagination import Pagination
from src.core.security import user_password
from src.main.config import app_settings, collections_names
from src.services.db.mongodb import UpdateOperatorsEnum
from . import schema as user_schema
from .constants import UserMessageEnum
from .crud import users_crud
from .exceptions import UserIsDisabled
from .models import User
from ..auth.constants import AuthOTPTypeEnum
from ..auth.crud import permissions_crud
from ..auth.models import PermissionModel


class UserController(BaseController):
    @staticmethod
    async def find_by_user_id(
        user_id: SchemaID,
    ) -> Optional[User]:
        user = await User.find_one({"_id": user_id})
        return user or None

    @staticmethod
    async def find_by_username(
        username: str,
        and_conditions: Optional[dict] = None,
        raise_exception: bool = True,
    ) -> Optional[User]:
        if and_conditions is None:
            and_conditions = {}
        query: dict = {"username": username}
        query |= and_conditions
        user_obj = await User.find_one(query)

        return user_obj or None

    async def authenticate_by_username_pass(
        self,
        username: str,
        password: str,
        and_conditions: Optional[dict] = None,
    ) -> Optional[User]:
        user_obj = await self.find_by_username(
            username=username, and_conditions=and_conditions
        )
        if user_obj and user_password.verify_password(
            password, user_obj.hashed_password
        ):
            return user_obj
        return None

    async def reset_forgot_password(
        self,
        verification: AuthUserChangePasswordIn,
        current_user: User,
        is_limited: bool,
    ) -> Tuple[
        Union[AuthUserResetPasswordOut, AuthChangedPasswordErrorMessageOut],
        bool,
    ]:
        if not is_limited:
            raise InvalidTempToken
        if await self.set_password(
            user_id=current_user.id,
            new_password=verification.new_password,
        ):
            await User.find_one({"_id": current_user.id}).set(
                {
                    User.login_datetime: datetime.now(timezone.utc),
                    User.last_login_datetime: current_user.login_datetime,
                    User.login_count: current_user.login_count + 1,
                }
            )
            tokens = await token.generate_token(current_user.id)
            return (
                AuthUserResetPasswordOut(
                    access_token=tokens.access_token,
                    refresh_token=tokens.refresh_token,
                ),
                True,
            )
        return AuthChangedPasswordErrorMessageOut(), False

    async def change_password(
        self,
        verification: AuthUserChangePasswordIn,
        current_user: User,
    ) -> Tuple[
        Union[
            AuthUserResetPasswordOut,
            AuthChangedPasswordMessageOut,
            AuthChangedPasswordErrorMessageOut,
        ],
        bool,
    ]:
        if await self.set_password(
            user_id=current_user.id,
            new_password=verification.new_password,
        ):
            await User.find_one({"_id": current_user.id}).set(
                {
                    User.login_datetime: datetime.now(timezone.utc),
                    User.last_login_datetime: current_user.login_datetime,
                    User.login_count: current_user.login_count + 1,
                }
            )
            tokens = await token.generate_token(current_user.id)
            return (
                AuthUserResetPasswordOut(
                    access_token=tokens.access_token,
                    refresh_token=tokens.refresh_token,
                ),
                True,
            )

    @staticmethod
    async def set_password(
        user_id: SchemaID,
        new_password: str,
        force_change_password: bool = False,
        force_login: bool = False,
    ) -> bool:
        _, is_updated = await users_crud.update_and_get(
            criteria={"_id": user_id},
            new_doc={
                "hashed_password": user_password.get_password_hash(new_password),
                "is_force_change_password": force_change_password,
                "is_force_login": force_login,
            },
        )
        return is_updated

    @staticmethod
    async def create_new_user(
        new_user_data: UsersCreateIn,
        **kwargs,
    ) -> UserCreateSchemaOut:
        user_dict_data = new_user_data.dict()
        user_dict_data.update(
            hashed_password=user_password.get_password_hash(new_user_data.password)
        )
        if kwargs:
            user_dict_data.update(kwargs)
        created = await User(**user_dict_data).insert()
        result = await users_crud.get_joined_user(target_id=created.id)
        return UserCreateSchemaOut(**result)

    async def register_new_user(
        self, background_tasks: BackgroundTasks, new_user_data: AuthRegisterIn, **kwargs
    ) -> Response:
        user_dict_data = new_user_data.dict()
        user_dict_data.update(
            hashed_password=user_password.get_password_hash(new_user_data.password)
        )
        if kwargs:
            user_dict_data.update(kwargs)
        user = await user_controller.find_by_username(
            username=new_user_data.username, raise_exception=False
        )
        username_type = new_user_data.username["value_type"]
        if user:
            if username_type == USERNAME_IS_PHONE and user.phone_verified:
                raise UserRegisterPhoneExists
            # elif username_type == USERNAME_IS_EMAIL and user.email_verified:
            #     raise UserRegisterEmailExists
            else:
                query_options = {
                    # USERNAME_IS_EMAIL: {
                    #     USERNAME_IS_EMAIL: new_user_data.username["value"],
                    #     "email_verified": False,
                    # },
                    USERNAME_IS_PHONE: {
                        USERNAME_IS_PHONE: new_user_data.username["value"],
                        "phone_verified": False,
                    },
                }
                background_tasks.add_task(
                    users_crud.update,
                    query_options[new_user_data.username["value_type"]],
                    {new_user_data.username["value_type"]: None},
                )
                background_tasks.add_task(
                    users_crud.hard_delete_many,
                    criteria={
                        # "email": None,
                        "mobile_number": None,
                    },
                )
                created_user, _ = await users_crud.default_update_and_get(
                    dict(id=user.id), new_doc=user_dict_data
                )
        else:
            created_user = await users_crud.create(User(**user_dict_data))
        await otp.set_otp_and_send_message(
            user=created_user,
            # otp_type=AuthOTPTypeEnum.email
            # if username_type == USERNAME_IS_EMAIL
            # else AuthOTPTypeEnum.sms,
            otp_type=AuthOTPTypeEnum.sms,
            cache_key=new_user_data.username["value"],
            request_type=OtpRequestType.verification,
        )
        return Response(
            message=UserMessageEnum.register_new_user_and_sent_otp, detail=[]
        )

    async def register_new_user_and_login(
        self,
        new_user_data: AuthRegisterIn,
        **kwargs,
    ) -> AuthToken:
        user_dict_data = new_user_data.dict()
        user_dict_data.update(
            hashed_password=user_password.get_password_hash(new_user_data.password)
        )
        if kwargs:
            user_dict_data.update(kwargs)
        try:
            created_user = await users_crud.create(User(**user_dict_data))
        except DuplicateKeyError as e:
            raise UserRegisterPhoneExists from e
        return await self.generate_token_for_user(created_user)

    async def generate_token_for_user(self, user):
        if not user.is_enabled:
            raise UserIsDisabled
        # if user.is_blocked:
        #     raise UserIsBlocked
        # if user.user_status == UserStatus.pending:
        #     raise UserIsPending
        # if user.user_status == UserStatus.rejected:
        #     raise UserIsRejected
        await users_crud.update(
            criteria={"_id": user.id},
            new_doc={
                "login_datetime": datetime.now(timezone.utc),
                "last_login_datetime": user.login_datetime,
                "login_count": user.login_count + 1,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id)

    @staticmethod
    async def get_all_users(
        pagination: Pagination,
        ordering: Ordering,
        criteria: dict = None,
    ) -> PaginatedResponse[List[UsersGetUserSubListOut]]:
        if not criteria:
            criteria = {}
        pipeline = [
            {"$match": criteria},
            {
                "$lookup": {
                    "from": collections_names.ORGANIZATION,
                    "localField": "organization_id",
                    "foreignField": "_id",
                    "as": "organization",
                },
            },
            {"$unwind": {"path": "$organization", "preserveNullAndEmptyArrays": True}},
            {
                "$addFields": {
                    "country": "$settings.country_code",
                    "organization_name": "$organization.name",
                    "id": "$_id",
                }
            },
        ]
        return await pagination.paginate(
            crud=users_crud,
            list_item_model=UsersGetUserSubListOut,
            pipeline=pipeline,
            _sort=await ordering.get_ordering_criteria(),
        )

    @staticmethod
    async def get_single_user(
        target_user_id: SchemaID,
    ) -> UsersGetUserOut:
        criteria = {
            "_id": target_user_id,
        }
        target_user = await users_crud.get_object(criteria=criteria)
        return UsersGetUserOut(
            **target_user.dict(),
        )

    @staticmethod
    async def user_activation(
        target_user_id: SchemaID,
    ) -> UsersActivationUserPatchOut:
        target_user = await users_crud.get_object(
            criteria={"_id": target_user_id},
        )
        updated_target_user, _ = await users_crud.update_and_get(
            criteria={"_id": target_user.id},
            new_doc={"is_enabled": not target_user.is_enabled},
        )
        return UsersActivationUserPatchOut(status=updated_target_user.is_enabled)

    @staticmethod
    async def user_blocking(
        target_user_id: SchemaID,
    ) -> UsersBlockingUserPatchOut:
        target_user = await users_crud.get_object(
            criteria={"_id": target_user_id},
        )
        updated_target_user, _ = await users_crud.update_and_get(
            criteria={"_id": target_user.id},
            new_doc={"is_blocked": not target_user.is_blocked},
        )
        return UsersBlockingUserPatchOut(status=updated_target_user.is_blocked)

    async def update_single_user(
        self,
        new_data: UsersUpdateIn,
        target_id: SchemaID,
    ):
        is_updated, updated_user = await users_crud.update_user(
            new_data=new_data,
            target_id=target_id,
        )

        if not is_updated:
            raise UpdateFailed
        return UsersGetUserOut(
            **updated_user.dict(),
        )

    @staticmethod
    async def soft_delete_single_user(
        target_user_id: SchemaID,
    ) -> bool:
        target_user = await users_crud.get_object(
            criteria={"_id": target_user_id},
        )
        is_deleted = await users_crud.soft_delete_by_id(_id=target_user_id)
        if target_user and is_deleted:
            return is_deleted
        else:
            raise DeleteFailed

    async def bulk_update_obj(
        self,
        obj_ids: List[SchemaID],
        new_obj_data: user_schema.UsersUpdateIn,
    ) -> List[User]:
        data_dict = new_obj_data.dict(exclude_none=True)
        if data_dict.get("password"):
            data_dict["hashed_password"] = user_password.get_password_hash(
                new_obj_data.password
            )
        new_obj_dict = User(**data_dict).dict(exclude_none=True)
        criteria = {"_id": {"$in": obj_ids}}
        (
            updated_users,
            is_updated,
        ) = await self.crud.default_update_many_and_get(
            criteria=criteria, new_doc=new_obj_dict
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return updated_users

    async def bulk_delete_users(self, obj_ids: List[SchemaID]) -> List[User]:
        return await users_crud.bulk_soft_delete(obj_ids=obj_ids)


user_controller = UserController(crud=users_crud)


class ProfileController(BaseController):
    async def get_my_profile(self, current_user: User) -> user_schema.ProfileGetMeOut:
        users_info = await users_crud.get_joined_user(current_user.id)
        permissions_dict = await permissions_crud.get_permissions_dict(current_user)
        permissions = [
            PermissionModel(entity=entity, rules=rules)
            for entity, rules in permissions_dict.items()
        ]
        users_info["permissions"] = permissions
        return user_schema.ProfileGetMeOut(**users_info)

    async def upload_avatar(
        self,
        avatar: ValidatedFile,
        path: str,
        current_user: Optional[User] = None,
        user_id: Optional[SchemaID] = None,
    ) -> FileOut:
        """Receive a file object, save it on server
        filename/file-id
        """
        _, extention = os.path.splitext(avatar.file_name)
        user_id = user_id or current_user.id
        avatar.file_name = str(user_id) + str(extention)
        uploaded_avatar, _ = await files_crud.save_file(file=avatar, path=path)

        img = BytesIO(avatar.content)
        image = Image.open(img)
        image.save(f"{path}/{uploaded_avatar}", quality=50, optimize=True)

        await users_crud.update(
            criteria={"_id": user_id},
            new_doc={
                "avatar": f"{app_settings.DEFAULT_AVATARS_PATH}/{uploaded_avatar}"
            },
            upsert=False,
        )

        return FileOut(
            file_name=uploaded_avatar,
            file_url=f"{app_settings.DEFAULT_AVATARS_PATH}/{uploaded_avatar}",
        )

    async def delete_avatar(self, current_user: User, path=str):
        file_names = glob(f"{path}/{current_user.id}.*")
        for file_name in file_names:
            os.remove(file_name)

    async def update_profile(
        self,
        current_user: User,
        payload: user_schema.ProfileUpdateMeIn,
    ) -> user_schema.ProfileGetMeOut:
        is_updated, updated_user = await users_crud.update_user(
            new_data=payload,
            target_id=current_user.id,
        )
        if not is_updated and updated_user:
            raise exceptions.UpdateFailed
        return await self.get_my_profile(current_user=current_user)

    async def get_all_addresses(
        self, current_user: User
    ) -> List[user_schema.AddressSchemaOut]:
        result = await users_crud.get_object(criteria={"id": current_user.id})
        return result.addresses

    async def create_new_address(
        self, current_user: User, payload: user_schema.AddressSchemaIn
    ) -> List[user_schema.AddressSchemaOut]:
        if payload.is_default:
            is_updated = await users_crud.update(
                criteria={"_id": current_user.id},
                new_doc={"addresses.$[].is_default": False},
            )
            if not is_updated:
                raise exceptions.UpdateFailed
        payload = payload.dict()
        payload.update({"address_id": str(uuid4())})
        user, is_updated = await users_crud.update_and_get(
            criteria={"_id": current_user.id},
            new_doc={"addresses": payload},
            operator=UpdateOperatorsEnum.push_,
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return [
            user_schema.AddressSchemaOut(**address.dict()) for address in user.addresses
        ]

    async def get_single_address(
        self,
        current_user: User,
        address_id: SchemaID,
    ) -> user_schema.AddressSchemaOut:
        result = await users_crud.get_object(
            criteria={"_id": current_user.id, "addresses.address_id": address_id},
            projection={"addresses.$": 1},
        )
        return result.get("addresses")[0]

    async def update_single_address(
        self,
        current_user: User,
        address_id: SchemaID,
        payload: user_schema.AddressSchemaIn,
    ) -> user_schema.AddressSchemaOut:
        if payload.is_default:
            is_updated = await users_crud.update(
                criteria={"_id": current_user.id},
                new_doc={"addresses.$[].is_default": False},
            )
            if not is_updated:
                raise exceptions.UpdateFailed
        payload = payload.dict()
        payload["address_id"] = address_id
        is_updated = await users_crud.update(
            criteria={"_id": current_user.id, "addresses.address_id": address_id},
            new_doc={"addresses.$": payload},
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return user_schema.AddressSchemaOut(**payload)

    async def delete_single_address(
        self, current_user: User, address_id: SchemaID
    ) -> List[user_schema.AddressSchemaOut]:
        user, is_updated = await users_crud.update_and_get(
            criteria={"_id": current_user.id},
            operator=UpdateOperatorsEnum.pull_,
            new_doc={"addresses": {"address_id": address_id}},
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return [
            user_schema.AddressSchemaOut(**address.dict()) for address in user.addresses
        ]

    async def get_my_permissions(
        self, current_user: User
    ) -> user_schema.ProfileGetPermissions:
        permissions_dict = await permissions_crud.get_permissions_dict(current_user)
        permissions = [
            PermissionModel(entity=entity, rules=rules)
            for entity, rules in permissions_dict.items()
        ]
        return user_schema.ProfileGetPermissions(permissions=permissions)

    async def get_my_permissions_dict(
        self, current_user: User
    ) -> user_schema.ProfileGetPermissionsDict:
        permissions_dict = await permissions_crud.get_permissions_dict(current_user)
        return user_schema.ProfileGetPermissionsDict(permissions=permissions_dict)


profile_controller = ProfileController(crud=users_crud)
