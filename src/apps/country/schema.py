from typing import Optional, List
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID


class StateListSchema(BaseSchema):
    id: Optional[SchemaID]
    name: str
    is_enabled: bool


class StateDetailSchema(BaseSchema):
    id: Optional[SchemaID]
    name: str
    is_enabled: bool


class StateCreateIn(BaseSchema):
    name: str
    is_enabled: Optional[bool]


class StateUpdateIn(BaseSchema):
    name: Optional[str]
    is_enabled: Optional[bool]


class CityListSchema(BaseSchema):
    id: Optional[SchemaID]
    name: str
    # neighbourhoods: Optional[List[str]]
    state_id: SchemaID
    is_enabled: bool


class CityDetailSchema(BaseSchema):
    id: Optional[SchemaID]
    name: str
    # neighbourhoods: Optional[List[str]]
    state_id: SchemaID
    is_enabled: bool


class CityCreateIn(BaseSchema):
    name: str
    # neighbourhoods: Optional[List[str]]
    state_id: SchemaID
    is_enabled: Optional[bool]


class CityUpdateIn(BaseSchema):
    name: Optional[str]
    # neighbourhoods: Optional[List[str]]
    is_enabled: Optional[bool]
