from typing import Optional

from pydantic import BaseModel, Field

from src.apps.user.constants import AddressType
from src.core.base.field import PyObjectId, PhoneStr, IranPostalCodeField
from src.core.mixins import DB_ID
from src.core.mixins.fields import PointField


# from src.core.mixins.models import AddFieldsModel


class StateModel(BaseModel):
    state_id: DB_ID
    name: str


class CityModel(BaseModel):
    city_id: DB_ID
    name: str


class AddressModel(BaseModel):
    address_id: DB_ID = Field(default_factory=PyObjectId, alias="_id")
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    address_name: Optional[str] = "My Address"
    alternate_phone_number: Optional[PhoneStr]
    apartment_number: Optional[str]
    area: Optional[str]
    building_name: Optional[str]
    city: Optional[CityModel]
    country_code: Optional[str] = "IR"
    first_name: Optional[str]
    is_default: Optional[bool] = False
    last_name: Optional[str]
    location: Optional[PointField]
    phone_number: Optional[PhoneStr]
    postal_code: Optional[IranPostalCodeField]
    state: Optional[StateModel]
    street: Optional[str]
    type: Optional[AddressType]


class FileModel(BaseModel):
    file_id: DB_ID
    file_url: str
