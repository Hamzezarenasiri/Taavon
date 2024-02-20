from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union, Dict

import phonenumbers
from pydantic import BaseModel, Field, HttpUrl, validator, EmailStr

from src import services
from src.apps.auth.models import PermissionModel
from src.apps.organization.models import Organization
from src.apps.user.constants import (
    DefaultRoleNameEnum,
    GenderEnum,
    LoginType,
    UserStatus,
    UserType,
    DeviceType,
    User422MessageEnum,
)
from src.constants import (
    CountryCode,
)
from src.core.base.field import (
    PasswordField,
    UsernameField,
    PhoneStr,
    IranNationalCodeStr,
)
from src.core.base.schema import BaseSchema, AddressSchema, CitySchemaIn, StateSchemaIn
from src.core.mixins import SchemaID
from src.core.mixins.fields import OptionalEmailStr
from src.main.config import app_settings
from src.services import global_services


class UserSettingsSchema(BaseSchema):
    language: str
    country_code: CountryCode
    state: Optional[str]


class AddressSchemaIn(AddressSchema):
    city: Optional[CitySchemaIn]
    state: Optional[StateSchemaIn]


class AddressSchemaOut(AddressSchema):
    pass


class CreateUserRoleEnum(str, Enum):
    super_admin: str = DefaultRoleNameEnum.super_admin.value
    admin: str = DefaultRoleNameEnum.admin.value
    user: str = DefaultRoleNameEnum.user.value


class BaseUserSchema(BaseSchema):
    email: Optional[EmailStr] = Field(example="user@example.com")
    first_name: Optional[str] = Field(example="John")
    is_enabled: Optional[bool] = True
    is_user_data_recorder: Optional[bool] = False
    last_name: Optional[str] = Field(example="Doe")
    mobile_number: Optional[PhoneStr] = Field(example="+989123456789")
    organization_id: Optional[SchemaID] = None
    roles: List[Optional[Union[str, CreateUserRoleEnum]]]
    username: UsernameField
    taking_position_date: Optional[date]

    @validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str):
        if not value:
            return value
        try:
            mobile_number_obj = phonenumbers.parse(value, "IR")
            return phonenumbers.format_number(
                mobile_number_obj,
                phonenumbers.PhoneNumberFormat.E164,
            )
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e


class UsersCreateOut(BaseUserSchema):
    address: Optional[AddressSchemaOut]
    avatar: Optional[str]
    date_of_birth: Optional[date]
    email_verified: Optional[bool]
    first_name: Optional[str] = Field(example="John")
    gender: Optional[GenderEnum]
    id: SchemaID = Field(alias="id")
    is_blocked: Optional[bool] = False
    is_force_change_password: Optional[bool]
    is_force_login: Optional[bool] = False
    last_name: Optional[str] = Field(example="Doe")
    national_code: Optional[IranNationalCodeStr]
    national_code: Optional[str]
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    roles: List[Optional[Union[str, CreateUserRoleEnum]]]
    settings: Optional[UserSettingsSchema]
    telephone: Optional[PhoneStr]
    user_status: Optional[UserStatus]


class UsersCreateIn(BaseUserSchema):
    address: Optional[AddressSchemaIn]
    avatar: Optional[str]
    date_of_birth: Optional[date]
    email: EmailStr = Field(example="user@example.com")
    email_verified: Optional[bool]
    first_name: str = Field(example="John")
    gender: Optional[GenderEnum]
    is_blocked: Optional[bool] = False
    is_force_change_password: Optional[bool] = True
    is_force_login: Optional[bool] = False
    last_name: str = Field(example="Doe")
    mobile_number: PhoneStr = Field(example="+989123456789")
    national_code: IranNationalCodeStr
    password: PasswordField
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    roles: Optional[List[Union[str, CreateUserRoleEnum]]] = []
    settings: Optional[UserSettingsSchema] = UserSettingsSchema(
        language=app_settings.DEFAULT_LANGUAGE,
        country_code=app_settings.DEFAULT_COUNTRY_CODE,
    ).dict()
    telephone: Optional[PhoneStr]
    user_status: Optional[UserStatus]
    user_type: Optional[UserType]

    @validator("organization_id")
    @classmethod
    def validate_organization_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[Organization.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        else:
            raise ValueError(
                User422MessageEnum.Invalid_organization_id_organization_not_found.value
            )



class UserSocialCreateSchema(UsersCreateIn):
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    roles: Optional[List[Union[str, CreateUserRoleEnum]]] = []


class UserCreateSchemaOut(BaseUserSchema):
    id: SchemaID = Field(alias="_id")
    address: Optional[AddressSchemaOut]
    avatar: Optional[str]
    date_of_birth: Optional[date]
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    gender: Optional[GenderEnum]
    national_code: Optional[IranNationalCodeStr]
    is_blocked: Optional[bool] = False
    is_force_change_password: Optional[bool]
    is_force_login: Optional[bool] = False
    national_code: Optional[IranNationalCodeStr]
    permissions: Optional[List[PermissionModel]]
    settings: Optional[UserSettingsSchema]
    telephone: Optional[PhoneStr]
    user_status: Optional[UserStatus]
    roles: List[Optional[Union[str, CreateUserRoleEnum]]] = [
        CreateUserRoleEnum.admin.value
    ]
    login_type: Optional[LoginType]
    last_login_datetime: Optional[datetime]
    login_datetime: Optional[datetime]
    user_type: Optional[UserType]
    phone_verified: Optional[bool]
    email_verified: Optional[bool]


class UsersGetUserOut(UserCreateSchemaOut):
    id: SchemaID = Field(alias="id")


class UsersActivationUserPatchOut(BaseSchema):
    status: bool


class UsersBlockingUserPatchOut(BaseSchema):
    status: bool


class UsersGetUserSubListOut(BaseUserSchema):
    avatar: Optional[str]
    country: Optional[CountryCode]
    id: SchemaID
    is_blocked: bool
    login_datetime: Optional[datetime]
    login_type: Optional[LoginType]
    national_code: Optional[IranNationalCodeStr]
    organization_name: Optional[str]
    position_in_organization: Optional[str]
    roles: Optional[List[Union[str, CreateUserRoleEnum]]] = []
    user_status: Optional[UserStatus]
    user_type: Optional[UserType]
    username: Optional[UsernameField]


class UsersChangePasswordByAdminIn(BaseModel):
    new_password: PasswordField


class UsersUpdateIn(BaseSchema):
    address: Optional[AddressSchemaIn]
    avatar: Optional[str]
    date_of_birth: Optional[date]
    email: Optional[EmailStr] = Field(example="user@example.com")
    email_verified: Optional[bool]
    first_name: Optional[str] = Field(example="John")
    gender: Optional[GenderEnum]
    is_blocked: Optional[bool]
    is_enabled: Optional[bool]
    is_force_change_password: Optional[bool]
    is_force_login: Optional[bool]
    last_name: Optional[str] = Field(example="Doe")
    mobile_number: Optional[PhoneStr] = Field(example="+989123456789")
    national_code: Optional[IranNationalCodeStr]
    password: Optional[PasswordField]
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    position_in_organization: Optional[str]
    organization_id: Optional[SchemaID] = None
    organization_name: Optional[str]
    roles: Optional[List[Union[str, CreateUserRoleEnum]]]
    settings: Optional[UserSettingsSchema]
    telephone: Optional[PhoneStr]
    user_status: Optional[UserStatus]
    user_type: Optional[UserType]
    username: Optional[UsernameField]


class UsersUpdateAdminUserIn(BaseSchema):
    address: Optional[AddressSchemaIn]
    avatar: Optional[str]
    date_of_birth: Optional[date]
    email_verified: Optional[bool]
    first_name: str = Field(example="John")
    gender: Optional[GenderEnum]
    roles: Optional[List[Union[str, CreateUserRoleEnum]]]
    is_blocked: Optional[bool]
    is_enabled: Optional[bool]
    is_force_change_password: Optional[bool]
    is_force_login: Optional[bool]
    last_name: str = Field(example="Doe")
    national_code: Optional[IranNationalCodeStr]
    password: Optional[PasswordField]
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    position_in_organization: Optional[str]
    settings: Optional[UserSettingsSchema]
    telephone: Optional[PhoneStr]
    user_status: Optional[UserStatus]
    user_type: Optional[UserType]
    username: Optional[UsernameField]


class ProfileUpdateMeIn(BaseSchema):
    avatar: Optional[HttpUrl]
    date_of_birth: Optional[date] = Field(example="1999-09-09")
    first_name: Optional[str]
    gender: Optional[GenderEnum] = Field(example=GenderEnum.male)
    last_name: Optional[str]
    mobile_number: Optional[PhoneStr] = Field(example="+982112345678")
    national_code: Optional[IranNationalCodeStr]
    settings: Optional[UserSettingsSchema]
    telephone: Optional[PhoneStr]
    position_in_organization: Optional[str]

    @validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str):
        if not value:
            return value
        try:
            mobile_number_obj = phonenumbers.parse(value, "IR")
            return phonenumbers.format_number(
                mobile_number_obj,
                phonenumbers.PhoneNumberFormat.E164,
            )
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e


class ProfileGetMeAgg(BaseSchema):
    address: Optional[AddressSchemaOut]
    avatar: Optional[str]
    create_datetime: datetime
    date_of_birth: Optional[date] = Field(example="1999-09-09")
    email: Optional[OptionalEmailStr] = Field(example="user@example.com")
    first_name: Optional[str] = Field(example="John")
    gender: Optional[GenderEnum] = Field(example=GenderEnum.male)
    id: SchemaID = Field(alias="_id")
    is_enabled: Optional[bool]
    is_force_change_password: Optional[bool] = Field(example=True)
    is_force_login: Optional[bool] = Field(example=False)
    last_login_datetime: Optional[datetime]
    last_name: Optional[str] = Field(example="Doe")
    login_datetime: Optional[datetime]
    login_type: Optional[LoginType]
    mobile_number: Optional[PhoneStr] = Field(example="+989123456789")
    national_code: Optional[IranNationalCodeStr] = Field(example="hNzrH4'7<-")
    position_in_organization: Optional[str]
    roles: List[Optional[Union[str, CreateUserRoleEnum]]]
    settings: UserSettingsSchema | None
    telephone: Optional[PhoneStr]
    user_status: UserStatus | None
    username: UsernameField


class ProfileGetMeOut(ProfileGetMeAgg):
    permissions: Optional[List[Optional[PermissionModel]]]


class ProfileUpdateMeOut(ProfileGetMeOut):
    pass


class UserBulkUpdateIn(UsersUpdateIn):
    ids: List[SchemaID]


class AddNewDeviceIn(BaseSchema):
    notification_token: str
    device_type: Optional[DeviceType]
    notification_enabled: bool = True


class ProfileGetPermissions(BaseSchema):
    permissions: Optional[List[Optional[PermissionModel]]]


class ProfileGetPermissionsDict(BaseSchema):
    permissions: Dict[str, List[str]]


class UsersImportOut(BaseSchema):
    pass


class UserImportCsvSchema(UsersUpdateIn):
    hashed_password: str
