from datetime import datetime
from typing import List, Optional

from pydantic import AnyUrl, Field, validator

from src.services import global_services
from src.core.base.field import PhoneStr, IranNationalCodeStr, EconomicCodeStr, ShebaStr
from src.core.base.schema import BaseSchema, FileSchema
from src.core.mixins import SchemaID
from .constants import Store422MessageEnum, LegalTypeEnum
from ..user.models import User
from ..user.schema import AddressSchemaIn


class StoreUserSchema(BaseSchema):
    user_id: Optional[SchemaID]
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[IranNationalCodeStr]
    mobile_number: Optional[PhoneStr]
    telephone: Optional[PhoneStr]


class StoreBaseSchema(BaseSchema):
    address: Optional[AddressSchemaIn]
    legal_type: Optional[LegalTypeEnum]
    national_id: Optional[str] = Field(max_length=10, min_length=10)
    economic_code: Optional[EconomicCodeStr]
    sheba: Optional[ShebaStr]
    agent_bank_name: Optional[str]
    birth_certificate_image: Optional[FileSchema]
    national_card_image: Optional[FileSchema]
    business_license_image: Optional[FileSchema]
    outside_image: Optional[FileSchema]
    inside_image: Optional[FileSchema]
    image_url: Optional[str]
    phone: Optional[PhoneStr]
    telephone: Optional[PhoneStr]
    text: Optional[str]
    name: str
    web_site: Optional[AnyUrl]


class StoreCreateIn(StoreBaseSchema):
    owner_id: SchemaID
    legal_type: LegalTypeEnum
    is_enabled: Optional[bool]

    @validator("owner_id")
    @classmethod
    def validate_user_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[User.get_collection_name()].find_one({"_id": value}):
            return value
        raise ValueError(Store422MessageEnum.Invalid_user_id__user_not_found.value)


class StoreCreateOut(StoreBaseSchema):
    id: SchemaID
    owner: StoreUserSchema
    is_enabled: Optional[bool]
    create_datetime: datetime


class StoreSubListOut(StoreBaseSchema):
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    create_datetime: datetime
    id: SchemaID
    is_enabled: Optional[bool]
    owner: StoreUserSchema


class StoreGetOut(StoreBaseSchema):
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    create_datetime: datetime
    id: SchemaID
    is_enabled: bool
    owner: StoreUserSchema


class StoreUpdateIn(StoreCreateIn):
    owner_id: Optional[SchemaID]
    address: Optional[AddressSchemaIn]
    image_url: Optional[str]
    is_enabled: Optional[bool]
    name: Optional[str]
    phone: Optional[PhoneStr]
    telephone: Optional[PhoneStr]
    text: Optional[str]
    web_site: Optional[AnyUrl]

    @validator("owner_id")
    @classmethod
    def validate_user_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[User.get_collection_name()].find_one({"_id": value}):
            return value
        raise ValueError(Store422MessageEnum.Invalid_user_id__user_not_found.value)


class StoreBulkUpdateIn(StoreUpdateIn):
    ids: List[SchemaID]


class StoreBulkDeleteIn(BaseSchema):
    ids: List[SchemaID]


class StoreUpdateOut(StoreBaseSchema):
    id: SchemaID = Field(alias="_id")
    owner: StoreUserSchema
    is_enabled: bool


class BulkUpdateOut(BaseSchema):
    is_updated: bool


class StoreGetListOut(BaseSchema):
    result: List[StoreSubListOut]
