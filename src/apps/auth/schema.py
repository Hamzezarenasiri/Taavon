from datetime import datetime
from typing import Optional, Union, List, Dict

from pydantic import BaseModel, Field

from src.apps.user.constants import GenderEnum, UserStatus
from src.core.base.field import (
    UsernameField,
    PasswordField,
    PhoneStr,
    IranNationalCodeStr,
)
from src.core.base.schema import BaseSchema
from src.core.mixins import DB_ID, ErrorMessage, Message
from src.core.mixins.fields import OptionalEmailStr
from src.core.mixins.models import UsernameSchema
from src.main.config import app_settings
from .constants import AuthErrorMessageEnum, AuthMessageEnum
from ..user.schema import CreateUserRoleEnum


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str


class AuthTokenAndProfile(AuthToken):
    create_datetime: datetime
    first_name: Optional[str] = Field(example="John")
    is_enabled: Optional[bool]
    is_force_change_password: Optional[bool] = Field(example=True)
    is_force_login: Optional[bool] = Field(example=False)
    last_login_datetime: Optional[datetime]
    last_name: Optional[str] = Field(example="Doe")
    login_datetime: Optional[datetime]
    mobile_number: Optional[PhoneStr] = Field(example="+989167076478")
    national_code: Optional[IranNationalCodeStr] = Field(example="hNzrH4'7<-")
    roles: List[Optional[Union[str, CreateUserRoleEnum]]]
    user_status: Optional[UserStatus]
    username: UsernameField
    permissions: Dict[str, List[str]]


class AuthUsernamePasswordIn(BaseSchema):
    username: UsernameField
    password: PasswordField = Field(example="hNzrH4'7<-", min_length=8, max_length=100)


class AuthOTPVerifyIn(UsernameSchema, BaseSchema):
    verification_code: Optional[str] = Field(
        min_length=app_settings.OTP_LENGTH,
        max_length=app_settings.OTP_LENGTH,
        example="12345",
    )


class AuthUserForgetOtpReqIn(UsernameSchema, BaseSchema):
    pass


class AuthUserChangePasswordIn(BaseSchema):
    old_password: PasswordField = Field(
        min_length=8, max_length=100, example="hNzrH4'7<-"
    )
    new_password: PasswordField = Field(
        min_length=8, max_length=100, example="hNzrH4'7<-"
    )


class AuthResetPasswordIn(BaseSchema):
    new_password: PasswordField = Field(
        min_length=8, max_length=100, example="hNzrH4'7<-"
    )


class AuthUserResetPasswordOut(AuthToken):
    pass


class AuthChangedPasswordErrorMessageOut(ErrorMessage):
    detail: str = AuthErrorMessageEnum.changed_password


class AuthChangedPasswordMessageOut(Message):
    detail: str = AuthMessageEnum.changed_password


class AuthRegisterIn(BaseSchema, UsernameSchema):
    first_name: Optional[str]
    last_name: Optional[str]
    username: str = Field(example="+989167076478")
    password: PasswordField = Field(example="hNzrH4'7<-")
    gender: Optional[GenderEnum]


class AuthRegisterOut(BaseSchema):
    id: DB_ID
    first_name: Optional[str]
    last_name: Optional[str]
    mobile_number: PhoneStr
    email: Optional[OptionalEmailStr]


class AuthIDTokenInSchema(BaseModel):
    id_token: Union[str, bytes]


class AuthForgetVerifyOut(BaseSchema):
    access_token: str
    limited: Optional[bool]

    class Config(BaseSchema.Config):
        max_anystr_length = None


class UserGetLogoutOut(BaseSchema):
    force_login: bool


class PermissionItem(BaseSchema):
    entity: str
    rules: List[str]


class RoleCreateIn(BaseSchema):
    name: str
    permissions: List[PermissionItem]
    priority: Optional[int]


class RoleCreateOut(BaseSchema):
    name: str
    permissions: List[PermissionItem]
    priority: Optional[int]


class RoleGetListOut(BaseSchema):
    name: str
    permissions: List[PermissionItem]
    priority: Optional[int]


class RoleGetOut(RoleCreateOut):
    pass


class RoleUpdateIn(BaseSchema):
    name: Optional[str]
    priority: Optional[int]
    permissions: Optional[List[PermissionItem]]


class RoleUpdateOut(RoleCreateOut):
    pass


class RoleBulkDeleteIn(BaseSchema):
    names: List[str]


class EntityCreateIn(BaseSchema):
    code_name: str
    description: Optional[str]
    rules: List[str]


class EntityCreateOut(BaseSchema):
    code_name: str
    description: Optional[str]
    rules: List[str]


class EntityGetSubListOut(BaseSchema):
    code_name: str
    description: Optional[str]
    rules: List[str]


class EntitiesGetListOut(BaseSchema):
    result: List[EntityGetSubListOut]


class EntityGetOut(EntityCreateOut):
    pass


class EntityUpdateIn(BaseSchema):
    code_name: Optional[str]
    description: Optional[str]
    rules: List[str]


class EntityUpdateOut(EntityCreateOut):
    pass


class RoleCreateIn(BaseSchema):
    name: str
    permissions: List[PermissionItem]


class RoleCreateOut(BaseSchema):
    name: str
    permissions: List[PermissionItem]


class RoleGetListOut(BaseSchema):
    name: str
    permissions: List[PermissionItem]


class RoleGetOut(RoleCreateOut):
    pass


class RoleUpdateIn(BaseSchema):
    name: Optional[str]
    permissions: Optional[List[PermissionItem]]


class RoleUpdateOut(RoleCreateOut):
    pass


class RoleBulkDeleteIn(BaseSchema):
    names: List[str]
