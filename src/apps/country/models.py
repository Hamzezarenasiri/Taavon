from typing import Optional

import pymongo
from beanie import Document
from bson import ObjectId

from src.core.mixins import DB_ID
from src.main.config import collections_names


class State(Document):
    name: str
    is_enabled: Optional[bool] = True
    is_deleted: Optional[bool] = False

    class Config:
        collection = collections_names.STATE
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    class Meta:
        entity_name = "states"
        indexes = [
            pymongo.IndexModel("id", name="id", unique=True),
        ]


class City(Document):
    name: str
    # neighbourhoods: Optional[List[str]] = []
    state_id: DB_ID
    is_enabled: Optional[bool] = True
    is_deleted: Optional[bool] = False

    class Config:
        # allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        collection = collections_names.CITY

    class Meta:
        entity_name = "cities"
