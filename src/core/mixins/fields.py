import abc
import random
import string
import uuid
from enum import Enum
from typing import Optional, Union

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field, validate_email

__all__ = (
    "DB_ID",
    "SchemaID",
    "default_id",
    "OptionalEmailStr",
    "DimensionsField",
    "DimensionsField",
    "PointField",
)

DB_ID = PydanticObjectId
SchemaID = PydanticObjectId


# we do the following for lazy initialization
# just a tiny hack to make the tests & patches work


def default_id():
    return PydanticObjectId()  # noqa: E731


def random_code():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for _ in range(6)
    )


def get_random_gift_key():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for _ in range(16)
    )


class CustomUUID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class OptionalEmailStr(EmailStr):
    @classmethod
    def validate(cls, value: Optional[str]) -> Optional[str]:
        return None if not value or value == "none" else validate_email(value)[1]


NumType = Union[float, int]
# Coordinate = Union[Tuple[NumType, NumType], Tuple[NumType, NumType, NumType]]
Coordinate = tuple


class _GeometryBase(BaseModel, abc.ABC):
    """Base class for geometry models"""

    coordinates: Coordinate

    @property
    def __geo_interface__(self):
        return self.dict()


class CoordinateType(str, Enum):
    point = "Point"


class PointField(_GeometryBase):
    """Point Model"""

    type: CoordinateType = Field(CoordinateType.point.value, const=True)
    coordinates: Coordinate


class DimensionsField(BaseModel):
    length: float
    width: float
    height: float


# class DimensionsFieldSchema(BaseModel):
#     length: Decimal
#     width: Decimal
#     height: Decimal
