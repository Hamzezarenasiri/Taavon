from datetime import datetime, date
from typing import List, Optional

from pydantic import EmailStr, AnyUrl, validator, Field, root_validator

from src.core.base.field import PhoneStr, IranPostalCodeField, IranNationalCodeStr
from src.core.base.schema import BaseSchema, CitySchemaIn, StateSchemaIn
from src.core.mixins import SchemaID
from .constants import OrganizationCategoryEnum, Organization422MessageEnum
from .models import (
    OrganizationCityModel,
    OrganizationStateModel,
    Organization,
)
from ..user.models import User
from ..user.schema import AddressSchemaIn
from ...services import global_services


class OrganizationUserSchema(BaseSchema):
    user_id: Optional[SchemaID]
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[IranNationalCodeStr]
    mobile_number: Optional[PhoneStr]
    telephone: Optional[PhoneStr]
    email: Optional[EmailStr]


class OrganizationUserSchemaIn(BaseSchema):
    user_id: Optional[SchemaID]
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[IranNationalCodeStr]
    mobile_number: Optional[PhoneStr]
    telephone: Optional[PhoneStr]
    email: Optional[EmailStr]

    @validator("user_id")
    @classmethod
    def validate_user_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[User.get_collection_name()].find_one({"_id": value}):
            return value
        else:
            raise ValueError(
                Organization422MessageEnum.Invalid_user_id__user_not_found.value
            )

    @root_validator()
    @classmethod
    def validate_root(cls, values):
        if user := global_services.SYNC_DB[User.get_collection_name()].find_one(
            {"_id": values.get("city_id")}
        ):
            values["first_name"] = user.get("first_name")
            values["last_name"] = user.get("last_name")
            values["national_code"] = user.get("national_code")
            values["mobile_number"] = user.get("mobile_number")
            values["telephone"] = user.get("telephone") or values["telephone"]
            values["email"] = user.get("email")
        return values


class OrganizationBaseSchema(BaseSchema):
    address: Optional[AddressSchemaIn]
    ceo: OrganizationUserSchema
    cio: Optional[OrganizationUserSchema]
    city: OrganizationCityModel
    email: Optional[EmailStr]
    image_url: Optional[str]
    organization_id: str
    parent: Optional[SchemaID]
    phone: Optional[PhoneStr]
    postal_code: Optional[IranPostalCodeField]
    state: Optional[OrganizationStateModel]
    telephone: Optional[PhoneStr]
    text: Optional[str]
    name: str
    web_site: Optional[AnyUrl]


class OrganizationCreateIn(OrganizationBaseSchema):
    ceo: Optional[OrganizationUserSchemaIn]
    cio: Optional[OrganizationUserSchemaIn]
    city: CitySchemaIn
    state: StateSchemaIn
    is_enabled: Optional[bool]

    @validator("parent")
    @classmethod
    def validate_parent(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[Organization.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        else:
            raise ValueError(
                Organization422MessageEnum.Invalid_parent__organization_not_found.value
            )


class OrganizationCreateOut(OrganizationBaseSchema):
    id: SchemaID
    is_enabled: Optional[bool]
    ceo: OrganizationUserSchema
    create_datetime: datetime


class OrganizationSubListOut(OrganizationBaseSchema):
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    create_datetime: datetime
    id: SchemaID
    is_enabled: Optional[bool]


class OrganizationGetOut(OrganizationBaseSchema):
    can_edit: bool = Field(True)
    can_confirm: bool = Field(False)
    ceo: OrganizationUserSchema
    create_datetime: datetime
    id: SchemaID
    is_enabled: bool


class OrganizationUpdateIn(OrganizationCreateIn):
    address: Optional[AddressSchemaIn]
    category: Optional[OrganizationCategoryEnum]
    ceo: Optional[OrganizationUserSchema]
    cio: Optional[OrganizationUserSchema]
    city: Optional[CitySchemaIn]
    email: Optional[EmailStr]
    image_url: Optional[str]
    is_enabled: Optional[bool]
    name: Optional[str]
    parent: Optional[SchemaID]
    phone: Optional[PhoneStr]
    postal_code: Optional[IranPostalCodeField]
    state: Optional[StateSchemaIn]
    telephone: Optional[PhoneStr]
    text: Optional[str]
    web_site: Optional[AnyUrl]


class OrganizationBulkUpdateIn(OrganizationUpdateIn):
    ids: List[SchemaID]


class OrganizationBulkDeleteIn(BaseSchema):
    ids: List[SchemaID]


class OrganizationUpdateOut(OrganizationBaseSchema):
    id: SchemaID = Field(alias="_id")
    is_enabled: bool


class BulkUpdateOut(BaseSchema):
    is_updated: bool


class OrganizationGetListOut(BaseSchema):
    result: List[OrganizationSubListOut]


class OrganizationImportOut(BaseSchema):
    pass
