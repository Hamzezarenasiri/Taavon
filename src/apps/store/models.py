from typing import Optional

from beanie import Document
from pydantic import AnyUrl, BaseModel, Field

from src.apps.store.constants import LegalTypeEnum
from src.core import mixins
from src.core.base.field import (
    PhoneStr,
    IranNationalCodeStr,
    IranPostalCodeField,
    EconomicCodeStr,
    ShebaStr,
)
from src.core.base.models import AddressModel, FileModel
from src.core.mixins import DB_ID
from src.main.config import collections_names


class StoreUserModel(BaseModel):
    user_id: Optional[DB_ID]
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[IranNationalCodeStr]
    mobile_number: Optional[PhoneStr]
    telephone: Optional[PhoneStr]

    class Config:
        arbitrary_types_allowed = True


class StoreStateModel(BaseModel):
    state_id: DB_ID
    name: str
    neighbourhood: Optional[str]


class StoreCityModel(BaseModel):
    city_id: DB_ID
    name: str


class Store(
    Document,
    mixins.SoftDeleteMixin,
    mixins.CreateDatetimeMixin,
    mixins.IsEnableMixin,
):
    legal_type: LegalTypeEnum
    national_id: Optional[str] = Field(max_length=10, min_length=10)
    economic_code: Optional[EconomicCodeStr]
    sheba: Optional[ShebaStr]
    agent_bank_name: Optional[str]
    birth_certificate_image: Optional[FileModel]
    national_card_image: Optional[FileModel]
    business_license_image: Optional[FileModel]
    outside_image: Optional[FileModel]
    inside_image: Optional[FileModel]
    owner: StoreUserModel
    address: Optional[AddressModel]
    # email: Optional[EmailStr]
    image_url: Optional[str]
    phone: Optional[PhoneStr]
    postal_code: Optional[IranPostalCodeField]
    telephone: Optional[PhoneStr]
    text: Optional[str]
    name: str
    guild: Optional[str]
    web_site: Optional[AnyUrl]

    class Config:
        arbitrary_types_allowed = True
        collection = collections_names.STORE

    class Meta:
        entity_name = "store"
        indexes = []
