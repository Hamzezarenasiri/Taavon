from datetime import datetime
from typing import List, Optional, Union

import pymongo
from beanie import Document, Indexed
from pydantic import BaseModel, Field

from src.apps.auth.models import PermissionModel
from src.apps.user.constants import (
    DefaultRoleNameEnum,
    UserStatus,
    UserType,
    DeviceType,
)
from src.constants import (
    CountryCode,
)
from src.core import mixins
from src.core.base.field import PyObjectId, PhoneStr, IranNationalCodeStr, UsernameField
from src.core.mixins import DB_ID


class DeviceDetail(BaseModel):
    ua_string: str
    os: Optional[str]
    browser: Optional[str]
    device: Optional[str]


class UserDevicesModel(mixins.CreateDatetimeMixin):
    device_id: DB_ID = Field(default_factory=PyObjectId, alias="_id")
    notification_token: str
    device_type: Optional[DeviceType]
    notification_enabled: bool = True
    device_detail: Optional[DeviceDetail]

    class Config:
        arbitrary_types_allowed = True


class UserSettings(BaseModel):
    language: str
    country_code: CountryCode
    state: Optional[str]


class User(Document):
    # wallet_amount: Optional[Decimal128] = 0
    # address: Optional[AddressModel]
    # avatar: Optional[str]
    create_datetime: Optional[datetime] = Field(default_factory=datetime.utcnow)
    # date_of_birth: Optional[date]
    # devices: Optional[List[UserDevicesModel]] = []
    # email: Indexed(EmailStr, unique=True)
    # email_verified: Optional[bool] = False
    first_name: str
    # gender: Optional[GenderEnum]
    hashed_password: str
    # is_blocked: Optional[bool] = False
    is_deleted: Optional[bool] = False
    is_enabled: Optional[bool] = True
    is_force_change_password: Optional[bool] = True
    is_force_login: Optional[bool] = False
    last_login_datetime: Optional[datetime]
    last_name: str
    login_count: Optional[int] = 0
    login_datetime: Optional[datetime]
    # login_type: Optional[LoginType]
    mobile_number: Indexed(PhoneStr, unique=True)
    national_code: Indexed(IranNationalCodeStr, unique=True)
    organization_id: Optional[DB_ID] = None
    organization_name: Optional[str]
    permissions: Optional[List[PermissionModel]] = []
    phone_verified: Optional[bool] = False
    roles: List[Union[str, DefaultRoleNameEnum]]
    # settings: Optional[UserSettings]
    # telephone: Optional[PhoneStr]
    update_datetime: Optional[datetime]
    user_status: Optional[UserStatus] = UserStatus.JUST_ADDED.value
    user_type: Optional[UserType]
    username: Indexed(UsernameField, unique=True)
    organization_ids: list[DB_ID] = Field([])

    # @validator("email")
    # @classmethod
    # def validate_email(cls, value) -> str:
    #     return str(value).lower() if value else None

    # pylint: disable=no-self-argument,no-self-use
    # @validator("date_of_birth")
    # def isoformat_date(cls, value: date) -> str:
    #     return value.isoformat() if value else None

    class Config:
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True
        # json_encoders = {ObjectId: str}

    class Meta:
        entity_name = "user"
        indexes = [
            pymongo.IndexModel([("username", pymongo.HASHED)], name="username"),
            # pymongo.IndexModel([("email", pymongo.ASCENDING)], name="email"),
            pymongo.IndexModel(
                [("mobile_number", pymongo.ASCENDING)], name="mobile_number"
            ),
        ]
