from typing import Optional, List

from beanie import Document
from pydantic import EmailStr

from src.apps.config.common_model import OfficeAddress
from src.core import mixins
from src.main.config import collections_names


class Config(mixins.SoftDeleteMixin, mixins.IsEnableMixin, Document):
    office_address: Optional[OfficeAddress]
    other_configs: Optional[dict]
    default_email_recipients: Optional[List[EmailStr]]

    class Config:
        collection = collections_names.CONFIG
        arbitrary_types_allowed = True

    class Meta:
        entity_name = "config"
