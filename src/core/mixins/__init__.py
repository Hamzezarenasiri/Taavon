from . import fields
from . import models
from typing import Optional

from pydantic import BaseModel

from src.core.mixins.fields import (  # noqa
    DB_ID,
    SchemaID,
    default_id,
    get_random_gift_key,
    random_code,
)
from src.core.mixins.models import (  # noqa
    CreateDatetimeMixin,
    DurationMixin,
    EmailModelMixin,
    FromToDatetimeMixin,
    IsEnableMixin,
    IsoFormatStartEndTimeMixin,
    MobileNumberModelMixin,
    PhoneNumberModelMixin,
    SoftDeleteMixin,
    UpdateDatetimeMixin,
    UsernameModel,
)


class Message(BaseModel):
    detail: Optional[str]


class ErrorMessage(BaseModel):
    detail: Optional[str]
