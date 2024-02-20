from typing import Optional

from pydantic import BaseModel

from src.apps.user.constants import AddressType
from src.core.base.field import PhoneStr


class OfficeAddress(BaseModel):
    address_id: Optional[str] = ""
    address_name: Optional[str] = "The Vira PRODUCT"
    # location: Optional[PointField] = PointField(coordinates=[0, 0])
    first_name: Optional[str] = "vira"
    last_name: Optional[str] = "PRODUCT"
    country_code: Optional[str] = "IR"
    phone_number: Optional[PhoneStr]
    alternate_phone_number: Optional[PhoneStr]
    street: Optional[str]
    address_line_1: Optional[str] = "Vira PRODUCT store"
    address_line_2: Optional[str] = "Vira PRODUCT store"
    state: Optional[str] = "Dubai"
    city: Optional[str] = "Dubai"
    postal_code: Optional[str]
    type: Optional[AddressType]
    landmark: Optional[str]
    building_name: Optional[str] = "Vira PRODUCT"
    area: Optional[str] = "Dubai"
    town: Optional[str] = "Dubai"
    apartment_number: Optional[str]
