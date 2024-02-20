from datetime import datetime, timedelta, timezone
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from src.core.common.enums import RoleEnum
from src.core.mixins import DB_ID
from src.main.config import jwt_settings


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    user_id: Optional[DB_ID]
    encrypted_values: Optional[str]
    limited: Optional[bool]
    exp: Optional[datetime] = Field(
        default_factory=lambda: (
            datetime.now(timezone.utc)
            + timedelta(seconds=jwt_settings.ACCESS_TOKEN_LIFETIME_SECONDS)
        )
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    # # This validator is needed, because it raises type_error otherwise
    # @validator("user_id", pre=True)
    # @classmethod
    # def uuid_to_str(cls, value):
    #     if isinstance(value, SchemaID):
    #         return str(value)
    #     return value
