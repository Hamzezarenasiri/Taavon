from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Dict

import phonenumbers
from pydantic import BaseModel, Field, validator

from src.apps.auth.models import PermissionModel
from src.apps.organization.models import Organization
from src.apps.user.constants import (
    DefaultRoleNameEnum,
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
    SUPER_ADMIN: str = DefaultRoleNameEnum.SUPER_ADMIN.value
    ADMIN: str = DefaultRoleNameEnum.ADMIN.value
    VENDOR: str = DefaultRoleNameEnum.VENDOR.value
    CUSTOMER: str = DefaultRoleNameEnum.CUSTOMER.value


class BaseUserSchema(BaseSchema):
    first_name: Optional[str] = Field(example="John")
    is_enabled: Optional[bool] = True
    last_name: Optional[str] = Field(example="Doe")
    mobile_number: Optional[PhoneStr] = Field(example="+989167076478")
    # organization_id: Optional[SchemaID] = None
    roles: List[Optional[Union[str, CreateUserRoleEnum]]]
    username: UsernameField
    # email: Optional[EmailStr] = Field(example="user@example.com")

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
    # address: Optional[AddressSchemaOut]
    # avatar: Optional[str]
    # date_of_birth: Optional[date]
    # email_verified: Optional[bool]
    # gender: Optional[GenderEnum]
    # is_blocked: Optional[bool] = False
    # user_status: Optional[UserStatus]
    # is_force_change_password: Optional[bool]
    # is_force_login: Optional[bool] = False
    first_name: Optional[str] = Field(example="John")
    id: SchemaID = Field(alias="id")
    last_name: Optional[str] = Field(example="Doe")
    national_code: IranNationalCodeStr
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    roles: List[Optional[Union[str, CreateUserRoleEnum]]]
    settings: Optional[UserSettingsSchema]
    telephone: Optional[PhoneStr]


class UsersCreateIn(BaseUserSchema):
    # address: Optional[AddressSchemaIn]
    # avatar: Optional[str]
    # date_of_birth: Optional[date]
    # email: EmailStr = Field(example="user@example.com")
    # email_verified: Optional[bool]
    # gender: Optional[GenderEnum]
    # is_force_change_password: Optional[bool] = True
    # is_force_login: Optional[bool] = False
    # settings: Optional[UserSettingsSchema] = UserSettingsSchema(language=app_settings.DEFAULT_LANGUAGE,
    #       country_code=app_settings.DEFAULT_COUNTRY_CODE,).dict()
    # telephone: Optional[PhoneStr]
    # is_blocked: Optional[bool] = False
    # user_status: Optional[UserStatus]
    first_name: str = Field(example="John")
    last_name: str = Field(example="Doe")
    mobile_number: PhoneStr = Field(example="+989167076478")
    national_code: IranNationalCodeStr
    password: PasswordField
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    roles: Optional[List[Union[str, CreateUserRoleEnum]]] = []
    # user_type: Optional[UserType]

    # @validator("organization_id")
    # @classmethod
    # def validate_organization_id(cls, value: SchemaID):
    #     if not value:
    #         return value
    #     if global_services.SYNC_DB[Organization.get_collection_name()].find_one(
    #         {"_id": value}
    #     ):
    #         return value
    #     else:
    #         raise ValueError(
    #             User422MessageEnum.Invalid_organization_id_organization_not_found.value
    #         )


class UserSocialCreateSchema(UsersCreateIn):
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    roles: Optional[List[Union[str, CreateUserRoleEnum]]] = []


class UserCreateSchemaOut(BaseUserSchema):
    # address: Optional[AddressSchemaOut]
    # avatar: Optional[str]
    # date_of_birth: Optional[date]
    # gender: Optional[GenderEnum]
    # is_blocked: Optional[bool] = False
    # settings: Optional[UserSettingsSchema]
    # telephone: Optional[PhoneStr]
    # login_type: Optional[LoginType]
    # email_verified: Optional[bool]
    # user_status: Optional[UserStatus]

    id: SchemaID = Field(alias="_id")
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    # is_force_change_password: Optional[bool]
    # is_force_login: Optional[bool] = False
    national_code: Optional[IranNationalCodeStr]
    permissions: Optional[List[PermissionModel]]
    roles: List[Optional[Union[str, CreateUserRoleEnum]]] = [
        CreateUserRoleEnum.ADMIN.value
    ]
    last_login_datetime: Optional[datetime]
    login_datetime: Optional[datetime]
    # user_type: Optional[UserType]
    phone_verified: Optional[bool]


class UsersGetUserOut(UserCreateSchemaOut):
    id: SchemaID = Field(alias="id")


class UsersActivationUserPatchOut(BaseSchema):
    status: bool


class UsersBlockingUserPatchOut(BaseSchema):
    status: bool


class UsersGetUserSubListOut(BaseUserSchema):
    # avatar: Optional[str]
    # country: Optional[CountryCode]
    # is_blocked: bool
    # login_type: Optional[LoginType]
    id: SchemaID
    login_datetime: Optional[datetime]
    national_code: Optional[IranNationalCodeStr]
    organization_name: Optional[str]
    roles: Optional[List[Union[str, CreateUserRoleEnum]]] = []
    # user_status: Optional[UserStatus]
    # user_type: Optional[UserType]
    username: Optional[UsernameField]


class UsersChangePasswordByAdminIn(BaseModel):
    new_password: PasswordField


class UsersUpdateIn(BaseSchema):
    # address: Optional[AddressSchemaIn]
    # avatar: Optional[str]
    # date_of_birth: Optional[date]
    # email: Optional[EmailStr] = Field(example="user@example.com")
    # email_verified: Optional[bool]
    # gender: Optional[GenderEnum]
    # is_blocked: Optional[bool]
    # settings: Optional[UserSettingsSchema]
    # telephone: Optional[PhoneStr]
    # is_force_change_password: Optional[bool]
    # is_force_login: Optional[bool]
    # organization_id: Optional[SchemaID] = None
    # organization_name: Optional[str]
    first_name: Optional[str] = Field(example="John")
    is_enabled: Optional[bool]
    last_name: Optional[str] = Field(example="Doe")
    mobile_number: Optional[PhoneStr] = Field(example="+989167076478")
    national_code: Optional[IranNationalCodeStr]
    password: Optional[PasswordField]
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    roles: Optional[List[Union[str, CreateUserRoleEnum]]]
    # user_status: Optional[UserStatus]
    # user_type: Optional[UserType]
    username: Optional[UsernameField]


class UsersUpdateAdminUserIn(BaseSchema):
    # address: Optional[AddressSchemaIn]
    # avatar: Optional[str]
    # date_of_birth: Optional[date]
    # email_verified: Optional[bool]
    # gender: Optional[GenderEnum]
    # settings: Optional[UserSettingsSchema]
    # telephone: Optional[PhoneStr]
    # is_blocked: Optional[bool]
    first_name: str = Field(example="John")
    roles: Optional[List[Union[str, CreateUserRoleEnum]]]
    is_enabled: Optional[bool]
    # is_force_change_password: Optional[bool]
    # is_force_login: Optional[bool]
    last_name: str = Field(example="Doe")
    national_code: Optional[IranNationalCodeStr]
    password: Optional[PasswordField]
    permissions: Optional[List[PermissionModel]]
    phone_verified: Optional[bool]
    # user_status: Optional[UserStatus]
    # user_type: Optional[UserType]
    username: Optional[UsernameField]


class ProfileUpdateMeIn(BaseSchema):
    # avatar: Optional[HttpUrl]
    # date_of_birth: Optional[date] = Field(example="1999-09-09")
    # gender: Optional[GenderEnum] = Field(example=GenderEnum.male)
    # settings: Optional[UserSettingsSchema]
    # telephone: Optional[PhoneStr]
    first_name: Optional[str]
    # last_name: Optional[str]
    # mobile_number: Optional[PhoneStr] = Field(example="+982112345678")
    # national_code: Optional[IranNationalCodeStr]

    # @validator("mobile_number")
    # @classmethod
    # def validate_mobile_number(cls, value: str):
    #     if not value:
    #         return value
    #     try:
    #         mobile_number_obj = phonenumbers.parse(value, "IR")
    #         return phonenumbers.format_number(
    #             mobile_number_obj,
    #             phonenumbers.PhoneNumberFormat.E164,
    #         )
    #     except phonenumbers.NumberParseException as e:
    #         raise ValueError("Invalid Phone Number") from e


class ProfileGetMeAgg(BaseSchema):
    # address: Optional[AddressSchemaOut]
    # avatar: Optional[str]
    # date_of_birth: Optional[date] = Field(example="1999-09-09")
    # email: Optional[OptionalEmailStr] = Field(example="user@example.com")
    # login_type: Optional[LoginType]
    # settings: UserSettingsSchema | None
    # telephone: Optional[PhoneStr]
    # gender: Optional[GenderEnum] = Field(example=GenderEnum.male)
    create_datetime: datetime
    first_name: Optional[str] = Field(example="John")
    id: SchemaID = Field(alias="_id")
    is_enabled: Optional[bool]
    # is_force_change_password: Optional[bool] = Field(example=True)
    # is_force_login: Optional[bool] = Field(example=False)
    last_login_datetime: Optional[datetime]
    last_name: Optional[str] = Field(example="Doe")
    login_datetime: Optional[datetime]
    mobile_number: Optional[PhoneStr] = Field(example="+989167076478")
    national_code: Optional[IranNationalCodeStr] = Field(example="hNzrH4'7<-")
    roles: List[Optional[Union[str, CreateUserRoleEnum]]]
    # user_status: Optional[UserStatus]
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
