from typing import List, Optional, Union

import pymongo
from beanie import Document
from pydantic import BaseModel

from src.apps.user.constants import DefaultRoleNameEnum
from src.core import mixins
from src.core.mixins import CreateDatetimeMixin


class PermissionModel(BaseModel):
    entity: str
    rules: List[str]


class Role(
    Document,
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
):
    name: Union[str, DefaultRoleNameEnum]
    permissions: Optional[List[Optional[PermissionModel]]]
    priority: Optional[int]

    class Config:
        arbitrary_types_allowed = True

    class Meta:
        entity_name = "role"
        indexes = [
            pymongo.IndexModel("name", name="role_name"),
        ]


class Entity(
    Document,
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    CreateDatetimeMixin,
):
    code_name: str
    rules: List[str]
    description: Optional[str]

    class Meta:
        entity_name = "entity"
        indexes = [
            pymongo.IndexModel("code_name", name="code_name"),
        ]


class Rule(
    Document,
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
):
    code_name: str
    description: str

    class Meta:
        entity_name = "rule"
        indexes = [
            pymongo.IndexModel("code_name", name="code_name", unique=True),
        ]
