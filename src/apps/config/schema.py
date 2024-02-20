from typing import Optional, List

from pydantic import EmailStr

from src.core.base.schema import BaseSchema


class ConfigBaseSchema(BaseSchema):
    is_enabled: Optional[bool]
    other_configs: Optional[dict]
    default_email_recipients: Optional[List[EmailStr]] = []


class ConfigGetOut(ConfigBaseSchema):
    pass


class ConfigUpdateIn(ConfigBaseSchema):
    pass


class ConfigUpdateOut(ConfigBaseSchema):
    pass
