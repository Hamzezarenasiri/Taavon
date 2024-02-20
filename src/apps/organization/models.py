from datetime import date
from typing import Optional, List

from beanie import Document
from pydantic import AnyUrl, EmailStr, BaseModel, validator

from src.apps.organization.constants import OrganizationCategoryEnum
from src.core import mixins
from src.core.base.field import PhoneStr, IranNationalCodeStr, IranPostalCodeField
from src.core.base.models import AddressModel
from src.core.mixins import DB_ID
from src.main.config import collections_names


class OrganizationUserModel(BaseModel):
    user_id: Optional[DB_ID]
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[IranNationalCodeStr]
    mobile_number: Optional[PhoneStr]
    telephone: Optional[PhoneStr]
    email: Optional[EmailStr]

    class Config:
        arbitrary_types_allowed = True


class OrganizationStateModel(BaseModel):
    state_id: DB_ID
    name: str
    neighbourhood: Optional[str]


class OrganizationCityModel(BaseModel):
    city_id: DB_ID
    name: str


class Organization(
    Document,
    mixins.SoftDeleteMixin,
    mixins.CreateDatetimeMixin,
    mixins.IsEnableMixin,
):
    address: Optional[AddressModel]
    ancestors: Optional[List[DB_ID]] = []
    category: Optional[OrganizationCategoryEnum]
    ceo: Optional[OrganizationUserModel]
    cio: Optional[OrganizationUserModel]
    city: Optional[OrganizationCityModel]
    email: Optional[EmailStr]
    image_url: Optional[str]
    organization_id: str
    parent: Optional[DB_ID] = None
    phone: Optional[PhoneStr]
    postal_code: Optional[IranPostalCodeField]
    state: Optional[OrganizationStateModel]
    telephone: Optional[PhoneStr]
    text: Optional[str]
    name: str
    web_site: Optional[AnyUrl]

    class Config:
        arbitrary_types_allowed = True
        collection = collections_names.ORGANIZATION

    class Meta:
        entity_name = "organization"
        indexes = []
