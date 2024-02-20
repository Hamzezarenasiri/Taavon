from datetime import datetime, time
from typing import Generic, List, TypeVar, Union
from typing import Optional

import phonenumbers
from bson import Decimal128, ObjectId
from pydantic import (
    AnyUrl,
    BaseConfig as PydanticBaseConfig,
    BaseModel as PydanticBaseModel,
    root_validator,
)
from pydantic import Field, validator
from pydantic.generics import GenericModel

from src.apps.country.models import City, State
from src.apps.organization.constants import Organization422MessageEnum
from src.apps.user.constants import AddressType
from src.core.base.field import PhoneStr
from src.core.mixins import SchemaID
from src.core.mixins.fields import PointField
from src.core.utils import phone_to_e164_format
from src.fastapi_babel import _
from src.main.config import app_settings
from src.services import global_services


class BaseConfig(PydanticBaseConfig):
    underscore_attrs_are_private = False
    allow_population_by_field_name = True
    anystr_strip_whitespace = True
    max_anystr_length = app_settings.DEFAULT_MAX_STR_LENGTH
    arbitrary_types_allowed = True
    json_encoders = {
        ObjectId: str,
        SchemaID: str,
        # time: lambda t: t.isoformat(),
        time: lambda t: t.strftime("%H:%M:%S.%fZ"),
        # datetime: lambda dt: dt.isoformat(),
        datetime: lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        Decimal128: lambda d: d.to_decimal(),
    }


class BaseSchema(PydanticBaseModel):
    class Config(BaseConfig):
        pass


DataT = TypeVar("DataT", bound=PydanticBaseModel)
MessageT = TypeVar("MessageT")
DetailT = TypeVar("DetailT")


class Response(GenericModel, Generic[DataT]):
    data: Optional[DataT] = {}
    success: bool = True
    message: Optional[str] = "Ok"
    detail: Optional[Union[str, List]] = []

    class Config(BaseConfig):
        pass


class ErrorResponse(GenericModel, Generic[MessageT]):
    data: Optional[dict] = {}
    success: bool = False
    message: Optional[MessageT] = _("Error")
    detail: Optional[Union[str, List]] = []


ListDataT = TypeVar("ListDataT", bound=list)


class PaginatedResponse(GenericModel, Generic[ListDataT]):
    total: Optional[int]
    offset: Optional[int]
    limit: Optional[int]
    next: Optional[AnyUrl]
    previous: Optional[AnyUrl]
    result: Optional[ListDataT] = []

    class Config(BaseConfig):
        pass


class PaginatedListSchema(BaseSchema):
    count: Optional[int]
    offset: Optional[int]
    limit: Optional[int]
    next: Optional[str]
    previous: Optional[str]
    data: Optional[list]


class BulkDeleteIn(BaseSchema):
    ids: List[SchemaID]


class CommonExportCsvSchemaOut(BaseSchema):
    url: str


class CommonExportXmlSchemaOut(BaseSchema):
    url: str


class MobileNumberSchemaMixin(BaseSchema):
    mobile_number: Optional[PhoneStr] = Field(example="+982112345678")

    @validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str):
        if not value:
            return value
        try:
            if value.startswith("00"):
                value = value.replace("00", "+", 1)
            return phone_to_e164_format(value)
        except phonenumbers.NumberParseException as e:
            raise ValueError(_("Invalid Phone Number")) from e


class StateSchema(BaseSchema):
    state_id: SchemaID
    name: str


class CitySchema(BaseSchema):
    city_id: SchemaID
    name: str


class CitySchemaIn(BaseSchema):
    city_id: SchemaID
    name: Optional[str]

    @root_validator()
    @classmethod
    def validate_root(cls, values):
        if city := global_services.SYNC_DB[City.get_collection_name()].find_one(
            {"_id": values.get("city_id")}
        ):
            values["name"] = city.get("name")
        return values

    @validator("city_id")
    @classmethod
    def validate_city_id(cls, value: SchemaID):
        if not value:
            return value
        if global_services.SYNC_DB[City.get_collection_name()].find_one({"_id": value}):
            return value
        else:
            raise ValueError(
                Organization422MessageEnum.Invalid_city_id_city_not_found.value
            )


class StateSchemaIn(BaseSchema):
    state_id: SchemaID
    name: Optional[str]

    @root_validator()
    @classmethod
    def validate_root(cls, values):
        if state := global_services.SYNC_DB[State.get_collection_name()].find_one(
            {"_id": values.get("state_id")}
        ):
            values["name"] = state.get("name")
        return values

    @validator("state_id")
    @classmethod
    def validate_state(cls, value: SchemaID, **kwargs):
        if not value:
            return value
        if global_services.SYNC_DB[State.get_collection_name()].find_one(
            {"_id": value}
        ):
            return value
        else:
            raise ValueError(
                Organization422MessageEnum.Invalid_state_id_state_not_found.value
            )


class AddressSchema(BaseSchema):
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    address_name: Optional[str] = "My Address"
    alternate_phone_number: Optional[PhoneStr]
    apartment_number: Optional[str]
    area: Optional[str]
    building_name: Optional[str]
    city: Optional[CitySchema]
    country_code: Optional[str] = "IR"
    first_name: Optional[str]
    is_default: Optional[bool] = False
    landmark: Optional[str]
    last_name: Optional[str]
    location: Optional[PointField]
    phone_number: Optional[PhoneStr]
    postal_code: Optional[str]
    state: Optional[StateSchema]
    street: Optional[str]
    town: Optional[str]
    type: Optional[AddressType]
